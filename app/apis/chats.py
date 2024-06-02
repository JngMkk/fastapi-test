import asyncio
from datetime import datetime

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect

HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


async def echo_message(websocket: WebSocket) -> None:
    msg = await websocket.receive_text()
    await websocket.send_text(f"Message: {msg}")


async def send_time(websocket: WebSocket) -> None:
    await asyncio.sleep(5)
    await websocket.send_text(f"time now: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# * 실행: uvicorn apps.chat.test:app
app = FastAPI()


@app.get("/")
async def get() -> HTMLResponse:
    return HTMLResponse(HTML)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()  # * 클라이언트에게 서버가 tunnel을 여는 것을 동의한다고 알림 (필수)
    try:
        while True:
            # * create_task: coroutine을 Task 객체로 변환
            # * Task 객체는 asyncio.wait 메서드를 사용하기 위해 필수적임.
            # * asyncio.wait 메서드는 coroutine을 동시에 실행할 때 매우 유용함.
            echo_msg_task = asyncio.create_task(echo_message(websocket))
            send_time_task = asyncio.create_task(send_time(websocket))

            # * 첫 번째 인자로 실행할 Task들의 set을 받음.
            # * 기본 설정에 의하면 이 함수는 인자로 제공된 Task들이 모두 완료될 때까지 blocking 됨.
            # * 그러나 return_when 인자를 설정하여 Task 중 1개가 끝나면 blocking된 상태에서 벗어나서 이후의 코드를 수행할 수 있음.
            # * 반환 값으로는 done, pending 상태에 맞는 Task set을 반환하게 됨.
            # * pending: 각 set 내에 Task 각각에 대해서 완료가 안된 경우, iteration 마다의 coroutine이 쌓여서 문제가 생길 수 있기 때문에 task.cancel() 수행
            # * done: 완료된 경우 task.result() 수행. 이는 coroutine 수행 결과물을 반환하고, exception을 re-raise하는 역할을 함. 클라이언트 쪽에서 연결이 끊기는 경우를 다룰 때 유용.
            done, pending = await asyncio.wait(
                {echo_msg_task, send_time_task}, return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()

    # * 클라이언트가 연결을 끊으면, receive_text 메서드가 error(WebSocketDisconnect) 발생시킴.
    except WebSocketDisconnect:
        await websocket.close()
