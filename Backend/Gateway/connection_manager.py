from fastapi import WebSocket


connections: dict[int, WebSocket] = {}
