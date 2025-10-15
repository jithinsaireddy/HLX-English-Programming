from struct import unpack
from english_programming.bin.uleb128 import read_uleb128, read_sleb128

MAGIC = b"NLBC"
SEC_CONSTANTS = 1
SEC_SYMBOLS   = 2
SEC_CODE      = 3
SEC_FUNCS     = 4
SEC_CLASSES   = 5

# opcodes
OP_LOAD_CONST  = 0x01
OP_LOAD_NAME   = 0x02
OP_STORE_NAME  = 0x03
OP_ADD         = 0x04
OP_PRINT       = 0x05
OP_BUILD_LIST  = 0x06
OP_INDEX       = 0x07
OP_BUILD_MAP   = 0x08
OP_GET_ATTR    = 0x09
OP_JUMP        = 0x0A
OP_JUMP_IF_FALSE=0x0B
OP_JUMP_BACK    = 0xAD  # signed offset for backward jumps
OP_CALL        = 0x0C
OP_RETURN      = 0x0D
OP_LT          = 0x0E
OP_SUB         = 0x0F
OP_MUL         = 0x10
OP_DIV         = 0x11
OP_CONCAT      = 0x12
OP_LEN         = 0x13
OP_EQ          = 0x14
OP_LE          = 0x15
OP_GE          = 0x16
OP_MOD         = 0x17

OP_WRITEFILE   = 0x20
OP_READFILE    = 0x21
OP_APPENDFILE  = 0x22
OP_DELETEFILE  = 0x23
OP_HTTPGET     = 0x40
OP_HTTPPOST    = 0x41
OP_IMPORTURL   = 0x50
OP_NEW         = 0x30
OP_GETFIELD    = 0x31
OP_SETFIELD    = 0x32
OP_CALL_METHOD = 0x33
OP_SETUP_CATCH = 0x61
OP_END_TRY     = 0x62
OP_THROW       = 0x63
OP_AWAIT       = 0x70
OP_ASYNC_READFILE = 0x71
OP_ASYNC_HTTPGET  = 0x72
OP_SCHEDULE       = 0x73
OP_RUN_TASKS      = 0x74
OP_THROW_T        = 0x75
OP_SETUP_CATCH_T  = 0x76
OP_ASYNC_SLEEP    = 0x78
OP_ASYNC_CONNECT  = 0x79
OP_ASYNC_SEND     = 0x7A
OP_ASYNC_RECV     = 0x7B
OP_SET_NEW        = 0x80
OP_SET_ADD        = 0x81
OP_SET_CONTAINS   = 0x82
OP_CSV_PARSE      = 0x90
OP_YAML_PARSE     = 0x91
OP_CSV_STRINGIFY  = 0x92
OP_YAML_STRINGIFY = 0x93
OP_ANNOTATE_FUNC  = 0xB0
OP_ITER_NEW       = 0xA0
OP_ITER_NEXT      = 0xA1
OP_ITER_HAS_NEXT  = 0xA2
OP_NEW         = 0x30
OP_GETFIELD    = 0x31
OP_SETFIELD    = 0x32
OP_CALL_METHOD = 0x33
OP_STRUPPER    = 0xA6
OP_STRLOWER    = 0xA7
OP_STRTRIM     = 0xA8
OP_LIST_APPEND = 0xA9
OP_LIST_POP    = 0xAA
OP_MAP_PUT     = 0xAB
OP_MAP_GET     = 0xAC


def parse_module(buf: bytes):
    assert buf[:4] == MAGIC, "bad magic"
    ver_major = int.from_bytes(buf[4:6], "little")
    ver_minor = int.from_bytes(buf[6:8], "little")
    flags     = buf[8]
    i = 9
    consts, syms, code = [], [], b""
    funcs = []  # list of (name_idx, params, code_bytes)
    classes = []

    while i < len(buf):
        sid = buf[i]; i += 1
        slen, i = read_uleb128(buf, i)
        sec = buf[i:i+slen]; i += slen

        if sid == SEC_CONSTANTS:
            j = 0
            count, j = read_uleb128(sec, j)
            for _ in range(count):
                tag = sec[j]; j += 1
                if tag == 0:  # int
                    v, j = read_sleb128(sec, j); consts.append(v)
                elif tag == 1:  # float64
                    v = unpack("<d", sec[j:j+8])[0]; j += 8; consts.append(v)
                elif tag == 2:  # string
                    ln, j = read_uleb128(sec, j)
                    v = sec[j:j+ln].decode("utf-8"); j += ln; consts.append(v)
                else:
                    raise ValueError("bad const tag")
        elif sid == SEC_SYMBOLS:
            j = 0
            count, j = read_uleb128(sec, j)
            for _ in range(count):
                ln, j = read_uleb128(sec, j)
                syms.append(sec[j:j+ln].decode("utf-8")); j += ln
        elif sid == SEC_CODE:
            code = sec
        elif sid == SEC_FUNCS:
            j = 0
            count, j = read_uleb128(sec, j)
            for _ in range(count):
                name_idx, j = read_uleb128(sec, j)
                # params
                pcount, j = read_uleb128(sec, j)
                params = []
                for _ in range(pcount):
                    p, j = read_uleb128(sec, j); params.append(p)
                # code
                ln, j = read_uleb128(sec, j)
                code_b = sec[j:j+ln]; j += ln
                funcs.append((name_idx, params, code_b))
        elif sid == SEC_CLASSES:
            j = 0
            count, j = read_uleb128(sec, j)
            for _ in range(count):
                class_idx, j = read_uleb128(sec, j)
                base_idx, j = read_uleb128(sec, j)
                fcount, j = read_uleb128(sec, j)
                field_syms = []
                for _ in range(fcount):
                    fs, j = read_uleb128(sec, j); field_syms.append(fs)
                mcount, j = read_uleb128(sec, j)
                methods = []
                for _ in range(mcount):
                    mname_idx, j = read_uleb128(sec, j)
                    pcount, j = read_uleb128(sec, j)
                    params = []
                    for _ in range(pcount):
                        p, j = read_uleb128(sec, j); params.append(p)
                    ln, j = read_uleb128(sec, j)
                    code_b = sec[j:j+ln]; j += ln
                    methods.append((mname_idx, params, code_b))
                # Decode base using offset scheme: 0 -> None, otherwise idx-1
                decoded_base = None if base_idx == 0 else (base_idx - 1)
                classes.append((class_idx, decoded_base, field_syms, methods))
        else:
            pass

    return (ver_major, ver_minor, flags, consts, syms, code, funcs, classes)


def run_code(consts, syms, code, env=None, func_map=None):
    env = {} if env is None else env
    stack = []
    i = 0
    # iterator peek buffer: maps id(iterator) -> next value fetched by HAS_NEXT
    env.setdefault('_iter_peek', {})
    # simple JIT backedge profiler
    try:
        from english_programming.bin.nlvm_jit import HotLoopJIT
        jit = HotLoopJIT()
    except Exception:
        jit = None
    catch_stack = []  # list of positions to jump to on throw
    # --------- OOP helpers (inheritance-aware) ---------
    def _class_entry(cname: str):
        # returns (field_syms, method_map, base_name)
        return env.get('_classes', {}).get(cname, ([], {}, None))
    def _collect_fields(cname: str):
        # base-first order, unique by symbol index
        order = []
        seen = set()
        cur = cname
        chain = []
        while cur:
            fs, _m, base = _class_entry(cur)
            chain.append((fs, base))
            cur = base
        # iterate reversed to have base-first
        for fs, _ in reversed(chain):
            for idx in fs:
                if idx not in seen:
                    seen.add(idx)
                    order.append(idx)
        return order
    def _lookup_method(cname: str, mname: str):
        # returns (params, code_bytes, defining_class) or (None, None, None)
        cur = cname
        while cur:
            _fs, methods, base = _class_entry(cur)
            entry = methods.get(mname)
            if entry:
                return entry[0], entry[1], cur
            cur = base
        return None, None, None
    # wall-clock guard
    try:
        import time as _time, os as _os
        _start_ms = int(_time.time() * 1000)
        _max_ms = int(_os.getenv('EP_MAX_MS', '30000'))
    except Exception:
        _start_ms = 0
        _max_ms = 2000
    while i < len(code):
        op = code[i]; i += 1
        # expose a simple profiler counter in env
        env['_op_counts'] = env.get('_op_counts', 0) + 1
        # hard guard on max op count
        try:
            import os as _os
            max_ops = int(_os.getenv('EP_MAX_OPS', '200000'))
        except Exception:
            max_ops = 200000
        if env['_op_counts'] > max_ops:
            raise RuntimeError('Operation limit exceeded')
        # time guard
        if _start_ms:
            import time as _time
            if int(_time.time() * 1000) - _start_ms > _max_ms:
                raise RuntimeError('Time limit exceeded')
        if op == OP_LOAD_CONST:
            idx, i = read_uleb128(code, i)
            stack.append(consts[idx])
        elif op == OP_LOAD_NAME:
            sidx, i = read_uleb128(code, i)
            stack.append(env.get(syms[sidx]))
        elif op == OP_STORE_NAME:
            sidx, i = read_uleb128(code, i)
            env[syms[sidx]] = stack.pop()
        elif op == OP_ADD:
            b = stack.pop(); a = stack.pop(); stack.append(a + b)
        elif op == OP_SUB:
            b = stack.pop(); a = stack.pop(); stack.append(a - b)
        elif op == OP_MUL:
            b = stack.pop(); a = stack.pop(); stack.append(a * b)
        elif op == OP_DIV:
            b = stack.pop(); a = stack.pop(); stack.append(a / b)
        elif op == OP_MOD:
            b = stack.pop(); a = stack.pop(); stack.append(a % b)
        elif op == OP_CONCAT:
            b = stack.pop(); a = stack.pop(); stack.append(str(a) + str(b))
        elif op == OP_LEN:
            a = stack.pop(); stack.append(len(a))
        elif op == OP_STRUPPER:
            a = stack.pop(); stack.append(str(a).upper())
        elif op == OP_STRLOWER:
            a = stack.pop(); stack.append(str(a).lower())
        elif op == OP_STRTRIM:
            a = stack.pop(); stack.append(str(a).strip())
        elif op == OP_LIST_APPEND:
            val = stack.pop(); lst = stack.pop();
            if not isinstance(lst, list): lst = []
            lst.append(val); stack.append(lst)
        elif op == OP_LIST_POP:
            lst = stack.pop();
            if not isinstance(lst, list) or not lst: stack.append(None)
            else: stack.append(lst.pop())
        elif op == OP_MAP_PUT:
            val = stack.pop(); key = stack.pop(); mp = stack.pop();
            if not isinstance(mp, dict): mp = {}
            mp[key] = val; stack.append(mp)
        elif op == OP_MAP_GET:
            key = stack.pop(); mp = stack.pop();
            if not isinstance(mp, dict): stack.append(-1)
            else: stack.append(mp.get(key, -1))
        elif op == OP_EQ:
            b = stack.pop(); a = stack.pop(); stack.append(a == b)
        elif op == OP_LE:
            b = stack.pop(); a = stack.pop(); stack.append(a <= b)
        elif op == OP_GE:
            b = stack.pop(); a = stack.pop(); stack.append(a >= b)
        elif op == OP_PRINT:
            val = stack.pop()
            # Explainable trace
            traces = env.setdefault('_traces', [])
            traces.append(('PRINT', val))
            print(val)
        elif op == OP_BUILD_LIST:
            count, i = read_uleb128(code, i)
            # guard against optimizer mishaps: if not enough values, fill None
            collected = []
            for _ in range(count):
                collected.append(stack.pop() if stack else None)
            lst = collected[::-1]
            stack.append(lst)
        elif op == OP_INDEX:
            idx = stack.pop(); seq = stack.pop(); stack.append(seq[idx])
        elif op == OP_BUILD_MAP:
            pairs, i = read_uleb128(code, i)
            m = {}
            for _ in range(pairs):
                v = stack.pop(); k = stack.pop(); m[k] = v
            stack.append(m)
        elif op == OP_GET_ATTR:
            name_idx, i = read_uleb128(code, i)
            obj = stack.pop(); stack.append(obj.get(syms[name_idx]))
            # trace attr access
            env.setdefault('_traces', []).append(('GET_ATTR', syms[name_idx]))
        elif op == OP_JUMP:
            off, i = read_uleb128(code, i)
            prev = i
            i += off
            if jit:
                cnt = jit.maybe_count_backedge(prev, i)
                if cnt and jit.is_hot((i, prev)):
                    # Only JIT very simple counter loops (no complex boolean chains inside body)
                    def _loop_is_simple(start_ip: int, end_ip: int) -> bool:
                        k = start_ip
                        extra_if = 0
                        has_eq = False
                        has_mod = False
                        # Skip the initial condition sequence: LOAD_NAME, LOAD_CONST/NAME, LE/GE, JUMP_IF_FALSE
                        # We conservatively scan entire body and require no EQ/MOD and at most one JUMP_IF_FALSE
                        while k < end_ip:
                            opk = code[k]; k += 1
                            if opk == OP_JUMP_IF_FALSE:
                                off2, k = read_uleb128(code, k)
                                extra_if += 1
                            elif opk == OP_EQ:
                                has_eq = True
                            elif opk == OP_MOD:
                                has_mod = True
                            elif opk in (OP_LOAD_CONST, OP_LOAD_NAME, OP_STORE_NAME, OP_ADD, OP_SUB, OP_MUL, OP_LE, OP_GE, OP_LT, OP_LIST_APPEND, OP_GET_ATTR, OP_BUILD_LIST, OP_LEN, OP_CONCAT):
                                # benign
                                # advance operands for ops we consumed above
                                if opk in (OP_LOAD_CONST, OP_LOAD_NAME, OP_STORE_NAME, OP_GET_ATTR):
                                    _, k = read_uleb128(code, k)
                                elif opk in (OP_BUILD_LIST,):
                                    _, k = read_uleb128(code, k)
                                else:
                                    pass
                            elif opk == OP_JUMP:
                                off_b, k = read_uleb128(code, k)
                                # don't follow
                            elif opk == OP_JUMP_BACK:
                                from english_programming.bin.uleb128 import read_sleb128 as _read_sleb
                                _, k = _read_sleb(code, k)
                            else:
                                # unknown/complex op – bail out
                                return False
                        return (extra_if <= 1) and (not has_eq) and (not has_mod)
                    if _loop_is_simple(i, prev):
                        try:
                            comp = jit.compiled_loops.get((i, prev)) or jit.compile_loop(code, i, prev)
                            comp(env, consts, syms)
                        except Exception:
                            # Fallback to interpreter on JIT failure
                            pass
                        finally:
                            # continue from after loop end
                            i = prev
        elif op == OP_JUMP_IF_FALSE:
            off, i = read_uleb128(code, i)
            cond = stack.pop()
            if not cond:
                i += off
        elif op == OP_JUMP_BACK:
            # signed relative jump (typically for loop backedges)
            off, i = read_sleb128(code, i)
            prev = i
            i += off
            if jit:
                cnt = jit.maybe_count_backedge(prev, i)
                if cnt and jit.is_hot((i, prev)):
                    def _loop_is_simple(start_ip: int, end_ip: int) -> bool:
                        k = start_ip
                        extra_if = 0
                        has_eq = False
                        has_mod = False
                        while k < end_ip:
                            opk = code[k]; k += 1
                            if opk == OP_JUMP_IF_FALSE:
                                off2, k = read_uleb128(code, k)
                                extra_if += 1
                            elif opk == OP_EQ:
                                has_eq = True
                            elif opk == OP_MOD:
                                has_mod = True
                            elif opk in (OP_LOAD_CONST, OP_LOAD_NAME, OP_STORE_NAME, OP_ADD, OP_SUB, OP_MUL, OP_LE, OP_GE, OP_LT, OP_LIST_APPEND, OP_GET_ATTR, OP_BUILD_LIST, OP_LEN, OP_CONCAT):
                                if opk in (OP_LOAD_CONST, OP_LOAD_NAME, OP_STORE_NAME, OP_GET_ATTR):
                                    _, k = read_uleb128(code, k)
                                elif opk in (OP_BUILD_LIST,):
                                    _, k = read_uleb128(code, k)
                                else:
                                    pass
                            elif opk == OP_JUMP:
                                off_b, k = read_uleb128(code, k)
                            elif opk == OP_JUMP_BACK:
                                from english_programming.bin.uleb128 import read_sleb128 as _read_sleb
                                _, k = _read_sleb(code, k)
                            else:
                                return False
                        return (extra_if <= 1) and (not has_eq) and (not has_mod)
                    if _loop_is_simple(i, prev):
                        try:
                            comp = jit.compiled_loops.get((i, prev)) or jit.compile_loop(code, i, prev)
                            comp(env, consts, syms)
                        except Exception:
                            pass
                        finally:
                            i = prev
        elif op == OP_LT:
            b = stack.pop(); a = stack.pop(); stack.append(a < b)
        elif op == OP_CALL:
            fidx, i = read_uleb128(code, i)
            argc, i = read_uleb128(code, i)
            args = [stack.pop() for _ in range(argc)][::-1]
            if func_map is None:
                raise RuntimeError("CALL used without function map")
            fname = syms[fidx]
            env.setdefault('_traces', []).append(('CALL', fname, argc))
            entry = func_map.get(fname)
            if entry is None:
                raise RuntimeError(f"function {fname} not found")
            params, fcode = entry
            # build frame
            frame = {}
            for idx, p_sym in enumerate(params):
                pname = syms[p_sym]
                frame[pname] = args[idx] if idx < len(args) else None
            combined = dict(env); combined.update(frame)
            ret = run_code(consts, syms, fcode, combined, func_map)
            stack.append(ret)
        elif op == OP_RETURN:
            return stack.pop() if stack else None
        elif op == OP_WRITEFILE:
            # expects: content, filename
            fname = stack.pop(); content = stack.pop()
            with open(fname, 'w') as f:
                f.write(content)
        elif op == OP_READFILE:
            # expects: filename; pushes content
            fname = stack.pop()
            with open(fname, 'r') as f:
                stack.append(f.read())
        elif op == OP_APPENDFILE:
            fname = stack.pop(); content = stack.pop()
            with open(fname, 'a') as f:
                f.write(content)
        elif op == OP_DELETEFILE:
            import os as _os
            fname = stack.pop();
            try:
                _os.remove(fname)
            except FileNotFoundError:
                pass
        elif op == OP_HTTPGET:
            # network gate
            import os as _os
            if _os.getenv('EP_ALLOW_NET', '0') != '1':
                raise RuntimeError('Network fetch not allowed. Set EP_ALLOW_NET=1 to enable.')
            import urllib.request as _r
            url = stack.pop()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/'
            }
            req = _r.Request(url, headers=headers, method='GET')
            with _r.urlopen(req) as resp:
                stack.append(resp.read().decode('utf-8'))
        elif op == OP_HTTPPOST:
            import os as _os
            if _os.getenv('EP_ALLOW_NET', '0') != '1':
                raise RuntimeError('Network fetch not allowed. Set EP_ALLOW_NET=1 to enable.')
            import urllib.request as _r
            import json as _json
            url = stack.pop(); data = stack.pop()
            if isinstance(data, (dict, list)):
                payload = _json.dumps(data).encode('utf-8')
                headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
                    'Accept': 'application/json,text/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.google.com/'
                }
            else:
                payload = str(data).encode('utf-8')
                headers = {
                    'Content-Type': 'text/plain',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
                    'Accept': 'text/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.google.com/'
                }
            req = _r.Request(url, data=payload, headers=headers, method='POST')
            with _r.urlopen(req) as resp:
                stack.append(resp.read().decode('utf-8'))
        elif op == OP_AWAIT:
            # Wait for a future-like object; in this stub, futures are callables that return the result
            fut = stack.pop()
            if callable(fut):
                stack.append(fut())
            else:
                stack.append(fut)
        elif op == OP_ASYNC_READFILE:
            # expects: filename; pushes a future-like lambda returning content
            fname = stack.pop()
            def _read():
                with open(fname, 'r') as f:
                    return f.read()
            stack.append(_read)
        elif op == OP_ASYNC_HTTPGET:
            url = stack.pop()
            def _get():
                try:
                    from english_programming.bin.module_cache import fetch
                    return fetch(url)
                except Exception:
                    return ''
            stack.append(_get)
        elif op == OP_SCHEDULE:
            # schedule a future (callable) for later execution
            fut = stack.pop()
            q = env.setdefault('_tasks', [])
            if callable(fut):
                q.append(fut)
        elif op == OP_RUN_TASKS:
            q = env.get('_tasks', [])
            results = []
            while q:
                fut = q.pop(0)
                try:
                    results.append(fut())
                except Exception as e:
                    results.append(str(e))
            stack.append(results)
        elif op == OP_ASYNC_SLEEP:
            ms, i = read_uleb128(code, i)
            import time
            def _sleep():
                time.sleep(ms/1000.0)
                return None
            stack.append(_sleep)
        elif op == OP_ASYNC_CONNECT:
            host_idx, i = read_uleb128(code, i)
            port, i = read_uleb128(code, i)
            host = syms[host_idx]
            def _conn():
                import socket
                s = socket.socket()
                s.settimeout(0.5)
                s.connect((host, port))
                return s
            stack.append(_conn)
        elif op == OP_ASYNC_SEND:
            # expects: data, socket
            import socket
            data = stack.pop(); sock = stack.pop()
            def _send():
                try:
                    if isinstance(data, str):
                        b = data.encode('utf-8')
                    else:
                        b = data
                    sock.sendall(b)
                    return True
                except Exception:
                    return False
            stack.append(_send)
        elif op == OP_ASYNC_RECV:
            # expects: socket; pushes future that returns str
            import socket
            sock = stack.pop()
            def _recv():
                try:
                    sock.settimeout(0.5)
                    return sock.recv(4096).decode('utf-8', 'ignore')
                except Exception:
                    return ''
            stack.append(_recv)
        elif op == OP_IMPORTURL:
            # Defer network/local permission to module_cache.fetch()
            from english_programming.bin.module_cache import fetch
            url = stack.pop()
            content = fetch(url)
            stack.append(content)
        elif op == OP_NEW:
            class_idx, i = read_uleb128(code, i)
            cname = syms[class_idx]
            obj = {'__class__': cname}
            for fs in _collect_fields(cname):
                obj[syms[fs]] = None
            stack.append(obj)
        elif op == OP_GETFIELD:
            field_idx, i = read_uleb128(code, i)
            obj = stack.pop()
            if isinstance(obj, dict):
                stack.append(obj.get(syms[field_idx]))
            else:
                stack.append(None)
        elif op == OP_SETFIELD:
            field_idx, i = read_uleb128(code, i)
            val = stack.pop(); obj = stack.pop()
            obj[syms[field_idx]] = val
        elif op == OP_SET_NEW:
            stack.append(set())
        elif op == OP_SET_ADD:
            v = stack.pop(); s = stack.pop(); s.add(v); stack.append(s)
        elif op == OP_SET_CONTAINS:
            v = stack.pop(); s = stack.pop(); stack.append(v in s)
        elif op == OP_CSV_PARSE:
            import csv, io
            data = stack.pop()
            reader = csv.reader(io.StringIO(data))
            stack.append([row for row in reader])
        elif op == OP_CSV_STRINGIFY:
            import csv, io
            rows = stack.pop()
            buf = io.StringIO(); w = csv.writer(buf)
            for r in rows: w.writerow(r)
            stack.append(buf.getvalue())
        elif op == OP_YAML_PARSE:
            try:
                import yaml as _yaml
                data = stack.pop(); stack.append(_yaml.safe_load(data))
            except Exception:
                # Fallback: pass through raw string
                data = stack.pop() if not 'data' in locals() else data
                stack.append(data)
        elif op == OP_YAML_STRINGIFY:
            try:
                import yaml as _yaml
                obj = stack.pop(); stack.append(_yaml.safe_dump(obj))
            except Exception:
                obj = stack.pop()
                stack.append(obj if isinstance(obj, str) else str(obj))
        elif op == OP_ANNOTATE_FUNC:
            # store function annotations in env['_annotations']
            fidx, i = read_uleb128(code, i)
            argc, i = read_uleb128(code, i)
            anns = [stack.pop() for _ in range(argc)][::-1]
            name = syms[fidx]
            env.setdefault('_annotations', {})[name] = anns
        elif op == OP_ITER_NEW:
            seq = stack.pop(); stack.append(iter(seq))
        elif op == OP_ITER_HAS_NEXT:
            # Pop iterator, peek next element without advancing primary iterator using internal buffer
            try:
                it = stack.pop()
            except IndexError:
                it = None
            ok = False
            if it is not None:
                try:
                    val = next(it)
                    env['_iter_peek'][id(it)] = val
                    ok = True
                except StopIteration:
                    ok = False
                except Exception:
                    ok = False
            stack.append(bool(ok))
        elif op == OP_ITER_NEXT:
            it = stack.pop()
            try:
                key = id(it)
                if key in env.get('_iter_peek', {}):
                    stack.append(env['_iter_peek'].pop(key))
                else:
                    stack.append(next(it))
            except StopIteration:
                stack.append(None)
        elif op == OP_CALL_METHOD:
            m_idx, i = read_uleb128(code, i)
            argc, i = read_uleb128(code, i)
            args = [stack.pop() for _ in range(argc)][::-1]
            obj = stack.pop()
            cname = obj.get('__class__')
            mname = syms[m_idx]
            env.setdefault('_traces', []).append(('CALL_METHOD', cname, mname, argc))
            params, mcode, _owner = _lookup_method(cname, mname)
            if params is None:
                raise RuntimeError(f"method {mname} not found on class {cname}")
            frame = {'self': obj}
            for idx, p_sym in enumerate(params):
                pname = syms[p_sym]
                frame[pname] = args[idx] if idx < len(args) else None
            combined = dict(env); combined.update(frame)
            ret = run_code(consts, syms, mcode, combined, func_map)
            stack.append(ret)
        elif op == OP_SETUP_CATCH:
            # operand is jump offset to catch handler
            off, i = read_uleb128(code, i)
            catch_stack.append(i + off)
        elif op == OP_END_TRY:
            # end of try scope
            if catch_stack:
                catch_stack.pop()
        elif op == OP_THROW:
            # push message before THROW
            msg = stack.pop() if stack else 'Error'
            if catch_stack:
                i = catch_stack[-1]
                # place message into env['exception']
                env['exception'] = msg
            else:
                raise RuntimeError(msg)
        elif op == OP_SETUP_CATCH_T:
            # operand is type symbol idx and catch target
            t_sym_idx, i = read_uleb128(code, i)
            off, i = read_uleb128(code, i)
            # Track target only; type symbol kept in env for simplicity
            env['_catch_type'] = syms[t_sym_idx]
            catch_stack.append(i + off)
        elif op == OP_THROW_T:
            # expects: message, type_name
            tname = stack.pop() if stack else 'Error'
            msg = stack.pop() if stack else ''
            if catch_stack and env.get('_catch_type') in (tname, 'Exception'):
                i = catch_stack[-1]
                env['exception'] = msg
                env['exception_type'] = tname
            else:
                raise RuntimeError(f"{tname}: {msg}")
        elif op == OP_NEW:
            class_idx, i = read_uleb128(code, i)
            cname = syms[class_idx]
            obj = {'__class__': cname}
            for fs in _collect_fields(cname):
                obj[syms[fs]] = None
            stack.append(obj)
        elif op == OP_GETFIELD:
            field_idx, i = read_uleb128(code, i)
            obj = stack.pop()
            stack.append(obj.get(syms[field_idx]))
        elif op == OP_SETFIELD:
            field_idx, i = read_uleb128(code, i)
            val = stack.pop(); obj = stack.pop()
            obj[syms[field_idx]] = val
        elif op == OP_CALL_METHOD:
            m_idx, i = read_uleb128(code, i)
            argc, i = read_uleb128(code, i)
            args = [stack.pop() for _ in range(argc)][::-1]
            obj = stack.pop()
            cname = obj.get('__class__')
            mname = syms[m_idx]
            params, mcode, _owner = _lookup_method(cname, mname)
            if params is None:
                raise RuntimeError(f"method {mname} not found on class {cname}")
            frame = {'self': obj}
            for idx, p_sym in enumerate(params):
                pname = syms[p_sym]
                frame[pname] = args[idx] if idx < len(args) else None
            combined = dict(env); combined.update(frame)
            ret = run_code(consts, syms, mcode, combined, func_map)
            stack.append(ret)
        else:
            raise RuntimeError(f"unknown opcode {op}")
    return None


def run_module(consts, syms, main_code, funcs, classes=None):
    # verify and optimize
    try:
        from english_programming.bin.nlbc_verify import verify_module
        verify_module(consts, syms, main_code, funcs, classes)
    except Exception as e:
        raise
    try:
        import os as _os
        if _os.getenv('EP_OPT', '0') == '1':
            from english_programming.bin.nlbc_opt import optimize_module
            consts, syms, main_code, funcs = optimize_module(consts, syms, main_code, funcs)
        # SSA hooks: build a lightweight instruction view and run CSE/LICM/inliner
        try:
            from english_programming.src.compiler.ssa_ir import ssa_from_bytecode, ssa_cse, ssa_licm, ssa_inline_noop
            import os as _os
            # Decode code bytes into a simple (op, operands) list for SSA passes
            def _decode_instrs(code_bytes: bytes):
                op_names = {
                    OP_LOAD_CONST: 'LOAD_CONST', OP_LOAD_NAME: 'LOAD_NAME', OP_STORE_NAME: 'STORE_NAME',
                    OP_ADD: 'ADD', OP_PRINT: 'PRINT', OP_BUILD_LIST: 'BUILD_LIST', OP_INDEX: 'INDEX',
                    OP_BUILD_MAP: 'BUILD_MAP', OP_GET_ATTR: 'GET_ATTR', OP_JUMP: 'JUMP',
                    OP_JUMP_IF_FALSE: 'JUMP_IF_FALSE', OP_CALL: 'CALL', OP_RETURN: 'RETURN', OP_LT: 'LT',
                    OP_SUB: 'SUB', OP_MUL: 'MUL', OP_DIV: 'DIV', OP_CONCAT: 'CONCAT', OP_LEN: 'LEN',
                    OP_EQ: 'EQ', OP_LE: 'LE', OP_GE: 'GE', OP_WRITEFILE: 'WRITEFILE', OP_READFILE: 'READFILE',
                    OP_APPENDFILE: 'APPENDFILE', OP_DELETEFILE: 'DELETEFILE', OP_HTTPGET: 'HTTPGET',
                    OP_HTTPPOST: 'HTTPPOST', OP_IMPORTURL: 'IMPORTURL', OP_NEW: 'NEW', OP_GETFIELD: 'GETFIELD',
                    OP_SETFIELD: 'SETFIELD', OP_CALL_METHOD: 'CALL_METHOD', OP_SETUP_CATCH: 'SETUP_CATCH',
                    OP_END_TRY: 'END_TRY', OP_THROW: 'THROW', OP_AWAIT: 'AWAIT', OP_ASYNC_READFILE: 'ASYNC_READFILE',
                    OP_ASYNC_HTTPGET: 'ASYNC_HTTPGET', OP_SCHEDULE: 'SCHEDULE', OP_RUN_TASKS: 'RUN_TASKS',
                    OP_THROW_T: 'THROW_T', OP_SETUP_CATCH_T: 'SETUP_CATCH_T', OP_ASYNC_SLEEP: 'ASYNC_SLEEP',
                    OP_ASYNC_CONNECT: 'ASYNC_CONNECT', OP_ASYNC_SEND: 'ASYNC_SEND', OP_ASYNC_RECV: 'ASYNC_RECV',
                    OP_SET_NEW: 'SET_NEW', OP_SET_ADD: 'SET_ADD', OP_SET_CONTAINS: 'SET_CONTAINS',
                    OP_CSV_PARSE: 'CSV_PARSE', OP_YAML_PARSE: 'YAML_PARSE', OP_CSV_STRINGIFY: 'CSV_STRINGIFY',
                    OP_YAML_STRINGIFY: 'YAML_STRINGIFY', OP_ANNOTATE_FUNC: 'ANNOTATE_FUNC', OP_ITER_NEW: 'ITER_NEW',
                    OP_ITER_NEXT: 'ITER_NEXT', OP_ITER_HAS_NEXT: 'ITER_HAS_NEXT'
                }
                instrs = []
                i = 0
                while i < len(code_bytes):
                    op = code_bytes[i]; i += 1
                    name = op_names.get(op, f'OP_{op}')
                    # Parse operands similar to interpreter
                    if op in (OP_LOAD_CONST, OP_LOAD_NAME, OP_STORE_NAME, OP_GET_ATTR, OP_LT, OP_LEN, OP_EQ, OP_LE, OP_GE):
                        a, i = read_uleb128(code_bytes, i); instrs.append((name, a))
                    elif op in (OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_CONCAT, OP_PRINT, OP_INDEX, OP_RETURN):
                        instrs.append((name,))
                    elif op == OP_BUILD_LIST or op == OP_BUILD_MAP:
                        n, i = read_uleb128(code_bytes, i); instrs.append((name, n))
                    elif op in (OP_JUMP, OP_JUMP_IF_FALSE, OP_SETUP_CATCH):
                        off, i = read_uleb128(code_bytes, i); instrs.append((name, off))
                    elif op == OP_CALL:
                        fidx, i = read_uleb128(code_bytes, i); argc, i = read_uleb128(code_bytes, i)
                        instrs.append((name, fidx, argc))
                    elif op == OP_CALL_METHOD:
                        midx, i = read_uleb128(code_bytes, i); argc, i = read_uleb128(code_bytes, i)
                        instrs.append((name, midx, argc))
                    elif op in (OP_WRITEFILE, OP_READFILE, OP_APPENDFILE, OP_DELETEFILE, OP_HTTPGET, OP_HTTPPOST, OP_IMPORTURL, OP_AWAIT, OP_ITER_NEW, OP_ITER_NEXT, OP_ITER_HAS_NEXT, OP_END_TRY, OP_THROW, OP_SCHEDULE, OP_RUN_TASKS, OP_SET_NEW, OP_SET_ADD, OP_SET_CONTAINS, OP_CSV_PARSE, OP_CSV_STRINGIFY, OP_YAML_PARSE, OP_YAML_STRINGIFY):
                        instrs.append((name,))
                    elif op == OP_SETUP_CATCH_T:
                        t, i = read_uleb128(code_bytes, i); off, i = read_uleb128(code_bytes, i)
                        instrs.append((name, t, off))
                    elif op == OP_ASYNC_SLEEP:
                        ms, i = read_uleb128(code_bytes, i); instrs.append((name, ms))
                    elif op == OP_ASYNC_CONNECT:
                        host_idx, i = read_uleb128(code_bytes, i); port, i = read_uleb128(code_bytes, i)
                        instrs.append((name, host_idx, port))
                    elif op in (OP_ASYNC_SEND, OP_ASYNC_RECV, OP_ASYNC_READFILE, OP_ASYNC_HTTPGET):
                        instrs.append((name,))
                    elif op in (OP_NEW, OP_GETFIELD, OP_SETFIELD, OP_ANNOTATE_FUNC):
                        a, i = read_uleb128(code_bytes, i)
                        if op in (OP_SETFIELD, OP_ANNOTATE_FUNC, OP_CALL, OP_CALL_METHOD):
                            # these have variable trailing operands handled above
                            pass
                        instrs.append((name, a))
                    else:
                        instrs.append((name,))
                return instrs

            try:
                # Build SSA, run safe passes. Re-assembly is gated for safety.
                ssa_mod = ssa_from_bytecode(syms, _decode_instrs(main_code))
                ssa_mod = ssa_cse(ssa_mod)
                ssa_mod = ssa_licm(ssa_mod)
                ssa_mod = ssa_inline_noop(ssa_mod)
                if _os.getenv('EP_SSA_FEEDBACK') == '1':
                    from english_programming.bin.nlbc_encoder import assemble_code
                    # Re-encode main code (experimental; unsafe by default)
                    instrs = []
                    for block in ssa_mod.blocks:
                        for ins in block.instrs:
                            ops = []
                            for a in ins.args:
                                try:
                                    ops.append(int(a))
                                except Exception:
                                    pass
                            instrs.append(tuple([ins.op] + ops))
                    main_code = assemble_code(instrs)
                    # Re-encode functions similarly
                    new_funcs = []
                    for (name_idx, params, code_b) in funcs:
                        f_ssa = ssa_inline_noop(ssa_licm(ssa_cse(ssa_from_bytecode(syms, _decode_instrs(code_b)))))
                        finstrs = []
                        for block in f_ssa.blocks:
                            for ins in block.instrs:
                                ops = []
                                for a in ins.args:
                                    try:
                                        ops.append(int(a))
                                    except Exception:
                                        pass
                                finstrs.append(tuple([ins.op] + ops))
                        new_funcs.append((name_idx, params, assemble_code(finstrs)))
                    funcs = new_funcs
            except Exception:
                pass
        except Exception:
            pass
    except Exception:
        pass
    env = {}
    # Build a callable registry
    func_map = { syms[name_idx]: (params, code) for (name_idx, params, code) in funcs }
    class_map = {}
    if classes:
        for class_idx, base_idx, field_syms, methods in classes:
            cname = syms[class_idx]
            method_map = { syms[mname_idx]: (params, code) for (mname_idx, params, code) in methods }
            base_name = syms[base_idx] if base_idx is not None and base_idx != -1 else None
            class_map[cname] = (field_syms, method_map, base_name)

    def call(name, args):
        entry = func_map.get(name)
        if entry is None:
            raise RuntimeError(f"function {name} not found")
        params, code = entry
        frame = {}
        for idx, p_sym in enumerate(params):
            pname = syms[p_sym]
            frame[pname] = args[idx] if idx < len(args) else None
        combined = dict(env); combined.update(frame)
        result = run_code(consts, syms, code, combined, func_map)
        for k, v in combined.items():
            if k not in env:
                env[k] = v
        return result

    # Expose CALL by symbol name via env if needed
    env['_call'] = call
    env['_classes'] = class_map
    run_code(consts, syms, main_code, env, func_map)
    # Filter return: keep internal '_' keys; for user keys, drop class instances (dicts with '__class__')
    def _is_instance(x):
        return isinstance(x, dict) and ('__class__' in x)
    ret = {}
    for k, v in env.items():
        if k.startswith('_'):
            ret[k] = v
        else:
            if not _is_instance(v):
                ret[k] = v
    return ret

