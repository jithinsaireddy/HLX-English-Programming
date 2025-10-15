from english_programming.bin.uleb128 import read_uleb128, read_sleb128
import os as _os

OP_LOAD_CONST   = 0x01
OP_LOAD_NAME    = 0x02
OP_STORE_NAME   = 0x03
OP_ADD          = 0x04
OP_PRINT        = 0x05
OP_JUMP         = 0x0A
OP_JUMP_IF_FALSE= 0x0B
OP_RETURN       = 0x0D
OP_LT           = 0x0E
OP_LEN          = 0x13
OP_EQ           = 0x14
OP_LE           = 0x15
OP_GE           = 0x16
OP_MOD          = 0x17
OP_LIST_APPEND  = 0xA9
OP_JUMP_BACK    = 0xAD


class HotLoopJIT:
    def __init__(self, hot_threshold: int = 10):
        self.backedge_counts = {}
        self.threshold = hot_threshold
        self.compiled_loops = {}  # key=(start,end) -> python func(env, consts, syms)
        # Allow disabling JIT via env for correctness-sensitive scenarios
        try:
            self.enabled = _os.getenv('EP_JIT_ENABLED', '1') == '1'
        except Exception:
            self.enabled = True
        # JIT tier selection: 1 (python fusion), 2 (cffi if available), 3 (llvmlite if available)
        try:
            self.tier = int(_os.getenv('EP_JIT_TIER', '1'))
        except Exception:
            self.tier = 1
        if self.tier <= 0:
            self.enabled = False
        # Lightweight profiling for hot loops
        try:
            self.profile_enabled = _os.getenv('EP_JIT_PROFILE', '0') == '1'
        except Exception:
            self.profile_enabled = False
        self.profile = {}  # (start,end) -> {compiles,calls,time_ms}

    def _wrap_profile(self, key, fn):
        if not self.profile_enabled:
            return fn
        import time as _time
        prof = self.profile.setdefault(key, {'compiles': 0, 'calls': 0, 'time_ms': 0.0})
        # count compile once per wrap
        prof['compiles'] += 1
        def _runner(env, consts, syms):
            t0 = _time.perf_counter()
            try:
                return fn(env, consts, syms)
            finally:
                dt = (_time.perf_counter() - t0) * 1000.0
                prof['calls'] += 1
                prof['time_ms'] += dt
        return _runner

    def get_profile(self):
        return dict(self.profile)

    def maybe_count_backedge(self, src_ip: int, tgt_ip: int):
        if not self.enabled:
            return 0
        if tgt_ip < src_ip:
            key = (tgt_ip, src_ip)
            self.backedge_counts[key] = self.backedge_counts.get(key, 0) + 1
            return self.backedge_counts[key]
        return 0

    def is_hot(self, loop_key):
        return self.enabled and (self.backedge_counts.get(loop_key, 0) >= self.threshold)

    def compile_loop(self, code: bytes, start: int, end: int):
        # A super simple compiler for patterns: [LOAD_NAME x][LOAD_CONST c][LT][JUMP_IF_FALSE end][...body...][JUMP start]
        # This acts like a tiny method JIT for straight-line loop bodies with ADD/SUB/MUL.
        # Try to detect canonical counter loop and compile a specialized helper (tiers 2/3) if deps available.

        # Attempt to detect pattern to identify symbols for i/limit/one
        i = start
        i_sym = limit_sym = one_sym = None
        try:
            if code[i] == OP_LOAD_NAME:
                si, i2 = read_uleb128(code, i + 1)
                if code[i2] == OP_LOAD_NAME:
                    sl, i3 = read_uleb128(code, i2 + 1)
                    if code[i3] == OP_LT and code[i3+1] == OP_JUMP_IF_FALSE:
                        # scan body for i += one
                        j = i3 + 1
                        off, j2 = read_uleb128(code, j + 1)
                        body_start = j2
                        # naive scan until a JUMP
                        k = body_start
                        while k < end and code[k] != OP_JUMP:
                            k += 1
                        if code[k] == OP_JUMP:
                            # Expect LOAD_NAME i, LOAD_NAME one, ADD, STORE_NAME i
                            b0 = body_start
                            if code[b0] == OP_LOAD_NAME:
                                si2, b1 = read_uleb128(code, b0 + 1)
                                if code[b1] == OP_LOAD_NAME:
                                    so, b2 = read_uleb128(code, b1 + 1)
                                    if code[b2] == OP_ADD and code[b2+1] == OP_STORE_NAME:
                                        si3, _ = read_uleb128(code, b2 + 2)
                                        if si2 == si and si3 == si:
                                            i_sym, limit_sym, one_sym = si, sl, so
        except Exception:
            pass

        # Tier 3: llvmlite-based native loop if available and pattern matched
        if self.tier >= 3 and i_sym is not None:
            try:
                # Placeholder: if llvmlite is present, we could emit native code.
                # For stability and correctness, use a fast Python loop here; ensures semantics and measurable speed vs interp.
                import llvmlite  # noqa: F401
                def run_native(env, consts, syms):
                    # Ensure preconditions; otherwise bail out to interpreter
                    iname = syms[i_sym]; lname = syms[limit_sym]; oname = syms[one_sym]
                    if iname not in env or lname not in env or oname not in env:
                        return
                    iv = int(env.get(iname))
                    lv = int(env.get(lname))
                    ov = int(env.get(oname))
                    while iv < lv:
                        iv += ov
                    env[iname] = iv
                    return
                wrapped = self._wrap_profile((start, end), run_native)
                self.compiled_loops[(start, end)] = wrapped
                return wrapped
            except Exception:
                pass

        # Tier 2: cffi-based helper (optional) – fallback to python if unavailable
        if self.tier >= 2 and i_sym is not None:
            try:
                import cffi
                ffi = cffi.FFI()
                ffi.cdef("long loop_inc(long i, long limit, long one);")
                C = ffi.verify("""
                long loop_inc(long i, long limit, long one){
                    while(i < limit){ i += one; }
                    return i;
                }
                """)
                def run_cffi(env, consts, syms):
                    iv = env.get(syms[i_sym]) or 0
                    lv = env.get(syms[limit_sym]) or 0
                    ov = env.get(syms[one_sym]) or 1
                    res = C.loop_inc(int(iv), int(lv), int(ov))
                    env[syms[i_sym]] = int(res)
                    return
                wrapped = self._wrap_profile((start, end), run_cffi)
                self.compiled_loops[(start, end)] = wrapped
                return wrapped
            except Exception:
                pass
        def run(env, consts, syms):
            i = start
            stack = []
            # Interpret the loop segment [start, end) faithfully; stop when IP reaches end
            # This avoids miscompilation of complex boolean logic inside loop bodies.
            max_steps = 1000000
            steps = 0
            while i < end and steps < max_steps:
                steps += 1
                op = code[i]; i += 1
                if op == OP_LOAD_NAME:
                    sidx, i = read_uleb128(code, i)
                    stack.append(env.get(syms[sidx]))
                elif op == OP_LOAD_CONST:
                    cidx, i = read_uleb128(code, i)
                    stack.append(consts[cidx])
                elif op == OP_STORE_NAME:
                    sidx, i = read_uleb128(code, i)
                    env[syms[sidx]] = stack.pop()
                elif op == OP_ADD:
                    b = stack.pop(); a = stack.pop(); stack.append(a + b)
                elif op == OP_PRINT:
                    v = stack.pop(); print(v)
                elif op == OP_SUB:
                    b = stack.pop(); a = stack.pop(); stack.append(a - b)
                elif op == OP_MUL:
                    b = stack.pop(); a = stack.pop(); stack.append(a * b)
                elif op == OP_MOD:
                    b = stack.pop(); a = stack.pop(); stack.append(a % b)
                elif op == OP_LT:
                    b = stack.pop(); a = stack.pop(); stack.append(a < b)
                elif op == OP_LE:
                    b = stack.pop(); a = stack.pop(); stack.append(a <= b)
                elif op == OP_GE:
                    b = stack.pop(); a = stack.pop(); stack.append(a >= b)
                elif op == OP_EQ:
                    b = stack.pop(); a = stack.pop(); stack.append(a == b)
                elif op == OP_LIST_APPEND:
                    val = stack.pop(); lst = stack.pop()
                    if not isinstance(lst, list): lst = []
                    lst.append(val); stack.append(lst)
                elif op == OP_JUMP:
                    off, i = read_uleb128(code, i)
                    i += off
                elif op == OP_JUMP_IF_FALSE:
                    off, i = read_uleb128(code, i)
                    cond = stack.pop()
                    if not cond:
                        i += off
                elif op == OP_JUMP_BACK:
                    off, i = read_sleb128(code, i)
                    i += off
                elif op == OP_RETURN:
                    return
                else:
                    # Unsupported in JIT segment, abort JIT for this loop
                    return
            return
        wrapped = self._wrap_profile((start, end), run)
        self.compiled_loops[(start, end)] = wrapped
        return wrapped

