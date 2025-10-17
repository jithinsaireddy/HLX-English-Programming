from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_cors import CORS, cross_origin
import uuid
import json as _json
import json
import sys
from pathlib import Path
import logging


def _ensure_src_on_path():
    current_file = Path(__file__).resolve()
    src_dir = current_file.parents[2]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


_ensure_src_on_path()

from compiler.improved_nlp_compiler import ImprovedNLPCompiler  # noqa: E402
from vm.improved_nlvm import ImprovedNLVM  # noqa: E402
import os  # noqa: E402
from compiler.linter import lint_lines  # noqa: E402
from english_programming.hlx.grammar import HLXParser  # noqa: E402
from english_programming.hlx.transpile_rtos import generate_rust_freertos  # noqa: E402
from english_programming.hlx.transpile_edge import generate_greengrass_manifest  # noqa: E402
from english_programming.hlx.net import generate_wot_td  # noqa: E402
from english_programming.hlx.run_demo import simulate_pressure_sequence  # noqa: E402
from english_programming.bin.nlp_compiler_bin import _normalize_text_with_spacy, _canonicalize_synonyms  # noqa: E402


app = Flask(__name__)
# Permissive CORS for frontend at 5173 (and general dev)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False, methods=["GET","POST","OPTIONS"], allow_headers=["Content-Type"])
compiler = ImprovedNLPCompiler()
vm = ImprovedNLVM(debug=False)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('epl_bin')
# Server-side telemetry aggregator (in-memory)
app.config.setdefault('_telemetry_server', {
    'normalized_count': 0,
    'unknown_count': 0,
    'normalized_samples': [],  # last 50 samples
    'unknown_samples': [],     # last 50 samples
})
# Disable legacy extensions by default to avoid noisy warnings with current VM API
# Set EP_LOAD_EXTENSIONS=1 to attempt loading
if os.getenv('EP_LOAD_EXTENSIONS') == '1':
    try:
        from extensions.extension_loader import ExtensionLoader  # noqa: E402
        extensions = ExtensionLoader(compiler, vm)
        extensions.load_all_extensions()
    except Exception:
        pass


@app.route("/health", methods=["GET"])
def health():
    return ("ok", 200)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        code = request.form.get("code", "")
        lines = [ln for ln in code.strip().split("\n") if ln.strip()]
        try:
            instructions = compiler.translate_to_bytecode(lines)
            if instructions:
                # Execute instructions via temp file to reuse VM execute
                temp_file = Path(".web_temp_bytecode.nlc")
                try:
                    if request.form.get("lint"):
                        warns = lint_lines(lines)
                        if warns:
                            output = "\n".join(warns)
                            raise Exception("Lint warnings present")
                    with open(temp_file, "w") as f:
                        for instr in instructions:
                            f.write(instr + "\n")
                    vm.execute(str(temp_file))
                    output = "Executed successfully. Check server logs for prints."
                finally:
                    if temp_file.exists():
                        try:
                            temp_file.unlink()
                        except OSError:
                            pass
        except Exception as e:
            output = f"Error: {str(e)}"
    # save if requested
    if request.method == "POST" and request.form.get("save"):
        snippet = request.form.get("code", "")
        name = request.form.get("name", "snippet")
        snippets_dir = Path("snippets")
        snippets_dir.mkdir(exist_ok=True)
        with open(snippets_dir / f"{name}.nl", "w") as fh:
            fh.write(snippet)
        return redirect(url_for('index', load=f"{name}.nl"))
    snippets = []
    snippets_dir = Path("snippets")
    if snippets_dir.exists():
        for p in snippets_dir.glob("*.nl"):
            snippets.append(p.name)
    # Load a snippet if requested
    load = request.args.get("load")
    prefill = ""
    if load:
        try:
            with open(snippets_dir / load, 'r') as fh:
                prefill = fh.read()
        except Exception:
            prefill = ""
    return render_template("index.html", output=output, snippets=snippets, prefill=prefill)


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv('PORT', '5050')))

# ---------------- HLX React Playground ----------------
@app.route("/hlx", methods=["GET"])
def hlx_index():
    return render_template("hlx.html")


@app.route("/hlx/compile", methods=["POST","OPTIONS"])
@cross_origin()
def hlx_compile():
    try:
        spec_text = request.get_json(force=True).get("spec", "")
        spec = HLXParser().parse(spec_text)
        rtos = generate_rust_freertos(spec)
        manifest = generate_greengrass_manifest(spec)
        td = generate_wot_td(spec)
        return {"ok": True, "rtos": rtos, "manifest": manifest, "td": td}
    except Exception as e:
        return {"ok": False, "error": str(e)}, 400


@app.route("/hlx/run_demo", methods=["POST","OPTIONS"])
@cross_origin()
def hlx_run_demo():
    try:
        body = request.get_json(force=True) or {}
        spec_text = body.get("spec", "")
        spec = HLXParser().parse(spec_text)
        # Basic model: evaluate first policy; list all sensor values for transparency
        policy = spec.policies[0]
        sensors = spec.sensors
        period_ms = sensors[0].period_ms if sensors else 1000
        # Trigger quickly in demos: ceil(duration/period), capped at 2 ticks
        try:
            import math as _math
            need_consecutive = max(1, min(2, _math.ceil(policy.duration_ms / max(1, period_ms))))
        except Exception:
            need_consecutive = 1
        hysteresis = getattr(policy, 'hysteresis_pct', 0.0) / 100.0
        cooldown_ms = getattr(policy, 'cooldown_ms', 0)
        cooldown_until = -1
        logs = []
        # Helpers to evaluate metrics/thresholds
        def _is_number(x):
            try:
                float(x)
                return True
            except Exception:
                return False
        def _val(token: str, ctx: dict):
            t = token.strip()
            if _is_number(t):
                return float(t)
            return float(ctx.get(t, 'nan')) if _is_number(ctx.get(t, 'nan')) else float('nan')
        def _eval_expr(expr: str, ctx: dict):
            s = expr.strip()
            # Very small expression support: a, a-b, a+b
            if ' - ' in s:
                a, b = s.split(' - ', 1)
                return _val(a, ctx) - _val(b, ctx)
            if ' + ' in s:
                a, b = s.split(' + ', 1)
                return _val(a, ctx) + _val(b, ctx)
            return _val(s, ctx)
        # Data source: real stream if provided; else deterministic per-sensor series
        data = body.get("data")
        series = []  # list of ctx dicts per tick {sensor_name: value}
        sensor_names = [s.name for s in sensors]
        if isinstance(data, list) and data:
            if isinstance(data[0], dict) and any(k in data[0] for k in sensor_names):
                # list of dicts with sensor values
                for d in data:
                    ctx = {name: float(d.get(name, 'nan')) for name in sensor_names}
                    series.append(ctx)
            elif isinstance(data[0], dict) and 'value' in data[0] and len(sensor_names) == 1:
                for d in data:
                    series.append({sensor_names[0]: float(d.get('value', 0.0))})
            elif len(sensor_names) == 1:
                for v in data:
                    series.append({sensor_names[0]: float(v)})
        if not series:
            # Build deterministic values per sensor; trigger fast after a few ticks
            ticks = max(5, need_consecutive + 2)
            left_expr = policy.metric.strip()
            thr_num = float(policy.threshold) if not isinstance(policy.threshold, str) and _is_number(policy.threshold) else None
            # Initialize baseline
            for i in range(ticks):
                ctx = {name: 22.5 for name in sensor_names}
                # Handle simple single-token metric: x OP thr
                if ' - ' not in left_expr and ' + ' not in left_expr:
                    x = left_expr
                    if thr_num is not None and x in ctx:
                        if policy.comparator in ('>','>='):
                            ctx[x] = thr_num - 0.5 if i < need_consecutive else thr_num + 0.6
                        elif policy.comparator in ('<','<='):
                            ctx[x] = thr_num + 0.5 if i < need_consecutive else thr_num - 0.6
                    elif isinstance(policy.threshold, str) and policy.threshold in ctx and x in ctx:
                        # symbolic threshold, e.g., flow_in > flow_out
                        base = 11.0
                        ctx[policy.threshold] = base
                        if policy.comparator in ('>','>='):
                            ctx[x] = base - 0.5 if i < need_consecutive else base + 0.6
                        elif policy.comparator in ('<','<='):
                            ctx[x] = base + 0.5 if i < need_consecutive else base - 0.6
                else:
                    # Handle a - b or a + b metrics
                    op = ' - ' if ' - ' in left_expr else ' + '
                    a, b = left_expr.split(op, 1)
                    a = a.strip(); b = b.strip()
                    # Choose a fixed baseline for b
                    b_base = 10.0
                    ctx[b] = b_base
                    if thr_num is not None:
                        if op == ' - ':
                            # want a - b cross thr
                            if policy.comparator in ('>','>='):
                                a_val = thr_num - 0.5 + b_base if i < need_consecutive else thr_num + 0.6 + b_base
                            else:
                                a_val = thr_num + 0.5 + b_base if i < need_consecutive else thr_num - 0.6 + b_base
                            ctx[a] = a_val
                        else:
                            # a + b cross thr
                            if policy.comparator in ('>','>='):
                                a_val = thr_num - b_base - 0.5 if i < need_consecutive else thr_num - b_base + 0.6
                            else:
                                a_val = thr_num - b_base + 0.5 if i < need_consecutive else thr_num - b_base - 0.6
                            ctx[a] = a_val
                series.append(ctx)
        consec = 0
        for idx, ctx in enumerate(series):
            cond = False
            # compute left value
            left_val = _eval_expr(policy.metric, ctx)
            # compute threshold value
            thr = _eval_expr(str(policy.threshold), ctx) if isinstance(policy.threshold, str) else float(policy.threshold)
            if cooldown_until >= 0 and idx*period_ms < cooldown_until and policy.comparator in ('>','>='):
                thr = thr * (1.0 + hysteresis) if thr == thr else thr
            if policy.comparator == '>':
                cond = (left_val > thr) if thr == thr else False
            elif policy.comparator == '>=':
                cond = (left_val >= thr) if thr == thr else False
            elif policy.comparator == '<':
                cond = (left_val < thr) if thr == thr else False
            elif policy.comparator == '<=':
                cond = (left_val <= thr) if thr == thr else False
            elif policy.comparator == '==':
                cond = (abs(left_val - thr) < 1e-9) if thr == thr else False
            consec = consec + 1 if cond else 0
            # Log all sensors at this tick
            vals_str = ' '.join(f"{n}={ctx.get(n)}" for n in sensor_names)
            logs.append(f"t={idx*period_ms:04d}ms {vals_str} cond={cond} consec={consec}")
            if consec >= need_consecutive:
                logs.append("-- POLICY TRIGGERED --")
                for act in policy.actions:
                    logs.append(f"ACTION: {act}")
                if cooldown_ms > 0:
                    cooldown_until = idx*period_ms + cooldown_ms
                break
        return {"ok": True, "log": "\n".join(logs)}
    except Exception as e:
        return {"ok": False, "error": str(e)}, 400


# ---------------- EPL React Playground (no build; CDN React) ----------------
@app.route("/epl", methods=["GET"])
def epl_index():
    return render_template("epl.html")


@app.route("/epl/exec", methods=["POST","OPTIONS"])
@cross_origin()
def epl_exec():
    try:
        # Enable network for EPL binary VM in this route (dev/demo)
        try:
            os.environ['EP_ALLOW_NET'] = '1'
            # Satisfy module_cache import lock requirement for network
            _lock_dir = os.path.expanduser('~/.english_cache')
            os.makedirs(_lock_dir, exist_ok=True)
            _lock_file = os.path.join(_lock_dir, 'registry.lock')
            try:
                open(_lock_file, 'a').close()
            except Exception:
                pass
        except Exception:
            pass
        code = request.get_json(force=True).get("code", "")
        lines = [ln for ln in code.strip().split("\n") if ln.strip()]
        # Prefer friendly mode for users: always try to interpret and not fail
        try:
            os.environ['EP_FUZZY'] = os.getenv('EP_FUZZY', '1') or '1'
            os.environ['EP_FUZZY_PRINT'] = os.getenv('EP_FUZZY_PRINT', '1') or '1'
        except Exception:
            pass
        # Text IR via ImprovedNLPCompiler (best-effort). If empty, still continue to binary compile.
        try:
            text_ir = compiler.translate_to_bytecode(lines)
        except Exception as _e:
            text_ir = []
        # Map EP_ENABLE_NET -> EP_ALLOW_NET for binary VM compatibility
        try:
            if os.getenv('EP_ALLOW_NET') is None and os.getenv('EP_ENABLE_NET', '0') == '1':
                os.environ['EP_ALLOW_NET'] = '1'
        except Exception:
            pass
        # Binary compilation (NLBC)
        from english_programming.bin.nlbc_disassembler import disassemble
        from english_programming.bin.nlvm_bin import parse_module, run_module
        from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.nlbc', delete=False) as tf:
            out_path = tf.name
        try:
            compile_english_to_binary(lines, out_path)
            logger.info('EPL compile (binary) OK')
            data = Path(out_path).read_bytes()
            disasm = disassemble(data)
            ver_major, ver_minor, flags, consts, syms, main_code, funcs, classes = parse_module(data)
            env = run_module(consts, syms, main_code, funcs, classes)
            logger.info('EPL run (binary VM) OK')
            # Extract printed output from traces, and user vars from env
            def _jsonable(x):
                if isinstance(x, set):
                    return list(x)
                if isinstance(x, dict):
                    return {str(k): _jsonable(v) for k, v in x.items()}
                if isinstance(x, (list, tuple)):
                    return [_jsonable(v) for v in x]
                try:
                    json.dumps(x)  # type: ignore[name-defined]
                    return x
                except Exception:
                    return str(x)
            traces = env.get('_traces', [])
            output = [_jsonable(v) for (op, *rest) in traces for v in ([rest[0]] if op == 'PRINT' and rest else [])]
            user_env = {k: _jsonable(v) for k, v in env.items() if not k.startswith('_')}
            # Infer a likely result when users don't write explicit prints
            inferred_result = None
            try:
                candidate_names = [
                    'result', 'sum', 'output', 'answer', 'value',
                    'res', 'retval', 'total', 'count', 'final', 'final_result'
                ]
                for name in candidate_names:
                    if name in user_env:
                        inferred_result = user_env.get(name)
                        break
                if inferred_result is None:
                    # Prefer a single numeric variable if there is exactly one
                    numeric_items = [
                        (k, v) for k, v in user_env.items()
                        if isinstance(v, (int, float))
                    ]
                    if len(numeric_items) == 1:
                        inferred_result = numeric_items[0][1]
                if inferred_result is None and output:
                    # Fall back to first printed value if available
                    inferred_result = output[-1]
            except Exception:
                inferred_result = None
            hints = env.get('_hints', [])
            # Update server-side telemetry based on hints
            try:
                tel = app.config.setdefault('_telemetry_server', {
                    'normalized_count': 0,
                    'unknown_count': 0,
                    'normalized_samples': [],
                    'unknown_samples': [],
                })
                for h in hints or []:
                    if isinstance(h, str) and h.startswith('Normalized: '):
                        tel['normalized_count'] = int(tel.get('normalized_count', 0)) + 1
                        tel['normalized_samples'] = (tel.get('normalized_samples', []) + [h])[-50:]
                    elif isinstance(h, str) and h.startswith('Unknown: '):
                        tel['unknown_count'] = int(tel.get('unknown_count', 0)) + 1
                        tel['unknown_samples'] = (tel.get('unknown_samples', []) + [h])[-50:]
            except Exception:
                pass
            return {"ok": True, "text_ir": text_ir, "disasm": disasm, "output": output, "env": user_env, "hints": hints,
                    "result": _jsonable(inferred_result),
                    "version": {"major": ver_major, "minor": ver_minor}}
        finally:
            try:
                Path(out_path).unlink(missing_ok=True)
            except Exception:
                pass
    except Exception as e:
        # Friendly mode: never hard-fail; surface as hints for UI
        try:
            msg = str(e)
        except Exception:
            msg = "Unknown error"
        return {"ok": True, "text_ir": [], "disasm": "", "output": [], "env": {},
                "hints": [f"Error: {msg}"], "version": {"major": 1, "minor": 0}}


# ---------------- Sharing (HLX/EPL snippets) ----------------
SHARE_DIR = Path("shared_snippets"); SHARE_DIR.mkdir(exist_ok=True)


@app.route("/share/save", methods=["POST","OPTIONS"])
@cross_origin()
def share_save():
    body = request.get_json(force=True) or {}
    content = body.get('content', '')
    kind = body.get('kind', 'hlx')
    if not content:
        return {"ok": False, "error": "Empty content"}, 400
    sid = str(uuid.uuid4())
    data = {"kind": kind, "content": content}
    (SHARE_DIR / f"{sid}.json").write_text(_json.dumps(data))
    return {"ok": True, "id": sid}


@app.route("/share/get", methods=["GET","OPTIONS"])
@cross_origin()
def share_get():
    sid = request.args.get('id')
    fp = SHARE_DIR / f"{sid}.json"
    if not sid or not fp.exists():
        return {"ok": False, "error": "Not found"}, 404
    data = _json.loads(fp.read_text())
    return {"ok": True, **data}
# ----------- Synonyms endpoint -----------
@app.route('/epl/synonyms', methods=['GET','OPTIONS'])
@cross_origin()
def epl_synonyms():
    try:
        from english_programming.bin.nlp_compiler_bin import _load_synonyms_yaml
        m = _load_synonyms_yaml() or {}
        return {"ok": True, "synonyms": m}
    except Exception:
        # Always return ok with empty map in friendly mode
        return {"ok": True, "synonyms": {}}
# ----------- Telemetry endpoint -----------
@app.route('/epl/telemetry', methods=['GET','OPTIONS'])
@cross_origin()
def epl_telemetry():
    try:
        tel = app.config.get('_telemetry_server', {})
        # Return a copy to avoid mutation surprises
        out = {
            'normalized_count': int(tel.get('normalized_count', 0)),
            'unknown_count': int(tel.get('unknown_count', 0)),
            'normalized_samples': list(tel.get('normalized_samples', []))[-50:],
            'unknown_samples': list(tel.get('unknown_samples', []))[-50:],
        }
        return {"ok": True, "telemetry": out}
    except Exception as e:
        return {"ok": False, "error": str(e)}, 500
# ----------- Debug NLP endpoint -----------
@app.route('/debug', methods=['POST'])
@cross_origin()
def debug_nlp():
    try:
        body = request.get_json(force=True) or {}
        text = body.get('text', '')
        norm = _normalize_text_with_spacy(text)
        canon = _canonicalize_synonyms(norm)
        return {"ok": True, "input": text, "spacy_norm": norm, "canonical": canon}
    except Exception as e:
        return {"ok": False, "error": str(e)}, 400


# Global CORS safeguard for any missing headers (defensive)
@app.after_request
def add_cors_headers(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp


@app.before_request
def global_preflight():
    # Simple per-IP rate limiting (default 60 req/min)
    try:
        import time
        rl = app.config.setdefault('_rate_limit', {})
        ip = request.remote_addr or 'unknown'
        window = int(os.getenv('EP_RATE_WINDOW_S', '60'))
        limit = int(os.getenv('EP_RATE_LIMIT', '120'))
        now = int(time.time())
        bucket = rl.setdefault(ip, [])
        # drop old entries
        cutoff = now - window
        while bucket and bucket[0] < cutoff:
            bucket.pop(0)
        if len(bucket) >= limit:
            resp = make_response(_json.dumps({"ok": False, "error": "Too Many Requests"}), 429)
            resp.headers['Content-Type'] = 'application/json'
            return resp
        bucket.append(now)
    except Exception:
        pass
    if request.method == 'OPTIONS':
        resp = make_response("", 204)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp


@app.route('/favicon.ico')
def favicon():
    # Avoid console 404s; return empty icon
    return ("", 204)