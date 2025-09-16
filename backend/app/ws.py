from fastapi import APIRouter, WebSocket
from asyncio import sleep

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def ws_updates(ws: WebSocket, user_id: str):
    await ws.accept()
    # Demo: 3 mensajes de status
    for step in ["queued", "running", "done"]:
        await ws.send_json({"user_id": user_id, "status": step})
        await sleep(1.0)
    await ws.close()
