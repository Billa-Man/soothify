import asyncio
import base64
import datetime
import os
from hume.client import AsyncHumeClient
from hume.empathic_voice.chat.socket_client import ChatConnectOptions, ChatWebsocketConnection
from hume.empathic_voice.chat.types import SubscribeEvent
from hume.empathic_voice.types import UserInput
from hume.core.api_error import ApiError
from hume import MicrophoneInterface, Stream
from loguru import logger

from settings import settings

class WebSocketHandler:

    def __init__(self):
        self.socket = None
        self.byte_strs = Stream.new()

    def set_socket(self, socket: ChatWebsocketConnection):
        self.socket = socket

    async def on_open(self):
        logger.info("WebSocket connection opened.")

    async def on_message(self, message: SubscribeEvent):
        scores = {}

        if message.type == "chat_metadata":
            message_type = message.type.upper()
            chat_id = message.chat_id
            chat_group_id = message.chat_group_id
            text = f"<{message_type}> Chat ID: {chat_id}, Chat Group ID: {chat_group_id}"

        elif message.type in ["user_message", "assistant_message"]:
            role = message.message.role.upper()
            message_text = message.message.content
            text = f"{role}: {message_text}"
            if message.from_text is False:
                scores = dict(message.models.prosody.scores)

        elif message.type == "audio_output":
            message_str: str = message.data
            message_bytes = base64.b64decode(message_str.encode("utf-8"))
            await self.byte_strs.put(message_bytes)
            return
        
        elif message.type == "error":
            error_message: str = message.message
            error_code: str = message.code
            raise ApiError(f"Error ({error_code}): {error_message}")
        
        else:
            message_type = message.type.upper()
            text = f"<{message_type}>"
        
        self._print_prompt(text)

        # Extract and print the top 3 emotions inferred from user and assistant expressions
        if len(scores) > 0:
            top_3_emotions = self._extract_top_n_emotions(scores, 3)
            self._print_emotion_scores(top_3_emotions)
            print("")
        else:
            print("")

    async def on_close(self):
        logger.info("WebSocket connection closed.")

    async def on_error(self, error):
        logger.error(f"Error: {error}")

    def _print_prompt(self, text: str) -> None:

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        now_str = now.strftime("%H:%M:%S")
        print(f"[{now_str}] {text}")

    def _extract_top_n_emotions(self, emotion_scores: dict, n: int) -> dict:

        sorted_emotions = sorted(emotion_scores.items(), key=lambda item: item[1], reverse=True)
        top_n_emotions = {emotion: score for emotion, score in sorted_emotions[:n]}

        return top_n_emotions

    def _print_emotion_scores(self, emotion_scores: dict) -> None:

        formatted_emotions = ' | '.join([f"{emotion} ({score:.2f})" for emotion, score in emotion_scores.items()])
        print(f"|{formatted_emotions}|")    


async def sending_handler(socket: ChatWebsocketConnection):

    await asyncio.sleep(1)

    user_input_message = UserInput("Hey There! How are you doing today?")
    await socket.send_user_input(user_input_message)


async def main():
    
    client = AsyncHumeClient(api_key=settings.HUME_API_KEY)
    options = ChatConnectOptions(config_id=settings.HUME_CONFIG_ID, secret_key=settings.HUME_SECRET_KEY)
    websocket_handler = WebSocketHandler()

    async with client.empathic_voice.chat.connect_with_callbacks(
        options=options,
        on_open=websocket_handler.on_open,
        on_message=websocket_handler.on_message,
        on_close=websocket_handler.on_close,
        on_error=websocket_handler.on_error
    ) as socket:
        # Set the socket instance in the handler
        websocket_handler.set_socket(socket)

        # Create an asynchronous task to continuously detect and process input from the microphone, as well as play audio
        microphone_task = asyncio.create_task(
            MicrophoneInterface.start(
                socket,
                allow_user_interrupt=False,
                byte_stream=websocket_handler.byte_strs
            )
        )
        
        # Create an asynchronous task to send messages over the WebSocket connection
        message_sending_task = asyncio.create_task(sending_handler(socket))
        
        # Schedule the coroutines to occur simultaneously
        await asyncio.gather(microphone_task, message_sending_task)   

if __name__ == "__main__":
    asyncio.run(main()) 