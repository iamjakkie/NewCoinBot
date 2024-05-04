def get_json_payload(method, **kwargs):
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": [
            kwargs
        ]
    }
