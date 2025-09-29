#!/usr/bin/env python3
"""Minimal LSP stub to enable future diagnostics and completions.
Run: python -m english_programming.tools.english_lsp
"""
import sys
import json


def _read_message():
    headers = {}
    while True:
        line = sys.stdin.readline()
        if not line:
            return None
        line = line.rstrip('\r\n')
        if line == '':
            break
        k, v = line.split(':', 1)
        headers[k.strip().lower()] = v.strip()
    length = int(headers.get('content-length', 0))
    body = sys.stdin.read(length)
    return json.loads(body)


def _send_message(obj):
    data = json.dumps(obj)
    sys.stdout.write(f"Content-Length: {len(data)}\r\n\r\n{data}")
    sys.stdout.flush()


def main():
    while True:
        msg = _read_message()
        if msg is None:
            break
        method = msg.get('method')
        id_ = msg.get('id')
        if method == 'initialize':
            _send_message({
                'jsonrpc': '2.0', 'id': id_, 'result': {
                    'capabilities': {
                        'textDocumentSync': 1,
                        'documentFormattingProvider': False
                    }
                }
            })
        elif method == 'shutdown':
            _send_message({'jsonrpc': '2.0', 'id': id_, 'result': None})
        elif method == 'exit':
            break
        elif method == 'textDocument/didOpen':
            # echo a trivial diagnostic scaffold
            params = msg.get('params', {})
            uri = params.get('textDocument', {}).get('uri')
            diag = {
                'jsonrpc': '2.0',
                'method': 'textDocument/publishDiagnostics',
                'params': {
                    'uri': uri,
                    'diagnostics': []
                }
            }
            _send_message(diag)
        elif method == 'textDocument/hover':
            id_ = msg.get('id')
            _send_message({'jsonrpc': '2.0', 'id': id_, 'result': {'contents': 'English Programming Language'}})
        elif method == 'textDocument/completion':
            id_ = msg.get('id')
            items = [
                {'label': 'Set', 'kind': 14},
                {'label': 'Add', 'kind': 14},
                {'label': 'Print', 'kind': 14},
                {'label': 'For each', 'kind': 14},
                {'label': 'Case', 'kind': 14}
            ]
            _send_message({'jsonrpc': '2.0', 'id': id_, 'result': {'isIncomplete': False, 'items': items}})
        elif method == 'textDocument/signatureHelp':
            id_ = msg.get('id')
            _send_message({'jsonrpc': '2.0', 'id': id_, 'result': {'signatures': [{'label': 'Add <a> and <b> and store the result in <dst>'}]}})
        else:
            if id_ is not None:
                _send_message({'jsonrpc': '2.0', 'id': id_, 'result': None})


if __name__ == '__main__':
    main()


