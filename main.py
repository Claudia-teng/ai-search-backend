import logging
import os
from contextlib import asynccontextmanager

import autogen
from autogen import LLMConfig
from autogen.io.websockets import IOWebsockets
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from search_function import perform_web_search

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


llm_config = LLMConfig(
    config_list={
        "api_type": "openai",
        "model": os.environ["OPENAI_MODEL"],
        "api_key": os.environ["OPENAI_API_KEY"],
        "temperature": 0.6,
        "max_tokens": 600,
        "stream": True,
    }
)


def on_connect(iostream: IOWebsockets) -> None:
    logger.info("Receiving message from client.")

    # 1. Receive Initial Message
    initial_msg = iostream.input()
    logger.info(f"{initial_msg=}")

    try:
        # 2. Instantiate ConversableAgent
        agent = autogen.ConversableAgent(
            name="chatbot",
            system_message="""
            You MUST use tool 'perform_web_search' to get information. 
            Give a summary of the information you found. 
            Do not need to provide the links, just the summary. 
            When the query is a random word or contains random words, just use the tool to search the web.
            """,
            llm_config=llm_config,
        )

        # 3. Define UserProxyAgent
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            system_message="A proxy for the user.",
            is_termination_msg=lambda x: x.get("content", "")
            and x.get("content", "").rstrip().endswith("TERMINATE"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False,
        )

        # 4. Register function
        autogen.register_function(
            perform_web_search,
            caller=agent,
            executor=user_proxy,
            description="Search the web for information about a query.",
            name="perform_web_search",
        )

        # 5. Initiate conversation
        logger.info(f"Initiating chat with agent {agent} using message '{initial_msg}'")

        user_proxy.initiate_chat(
            agent,
            message=initial_msg,
        )
    except Exception as e:
        logger.error(f" - on_connect(): Exception: {e}")
        raise e


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>AG2 websocket test</title>
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
            var ws = new WebSocket("ws://localhost:8080/ws");
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


@asynccontextmanager
async def run_websocket_server(app):
    with IOWebsockets.run_server_in_thread(
        on_connect=on_connect, host="0.0.0.0", port=8080
    ) as uri:
        logger.info(f"Websocket server started at {uri}.")
        yield


app = FastAPI(lifespan=run_websocket_server)


@app.get("/frontend")
async def get():
    return HTMLResponse(html)
