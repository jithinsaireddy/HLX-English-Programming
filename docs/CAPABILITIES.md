# VM Capability Model

## Default Deny
- Network operations (HTTPGET/HTTPPOST/IMPORTURL) require `EP_ALLOW_NET=1`.
- Time/ops guards: `EP_MAX_MS` (default 2000) and `EP_MAX_OPS` (default 200000).

## Filesystem
- WRITEFILE/READFILE/APPENDFILE/DELETEFILE operate on local paths; sandboxing to be configured by embedding environment.

## Network
- Disabled by default; enable via environment; user-agent and headers are set defensively.

## Async/Tasks
- Futures (async ops) are explicit; scheduler is cooperative via `SCHEDULE`/`RUN_TASKS`.

## Classes/Methods
- OOP features are dictionary-based; classes are registered via `_classes` in env.
