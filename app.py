from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.schema import Activity, ActivityTypes


APP_ID = ""
APP_PASSWORD = ""

SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


class SimpleTraditionalChatbot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == ActivityTypes.message:
            user_text = turn_context.activity.text

            if user_text is None or user_text.strip() == "":
                await turn_context.send_activity(
                    "I did not understand that. Please type help to see what I can do."
                )
                return

            message = user_text.lower().strip()

            if message in ["hi", "hello", "hey"]:
                response = "Hello! I am a simple traditional chatbot. Type help to see what I can do."

            elif message == "help":
                response = (
                    "Here are my capabilities:\n"
                    "1. Say hello\n"
                    "2. Tell my purpose\n"
                    "3. Answer what is HCI\n"
                    "4. Answer what is AI\n"
                    "5. Reverse your text\n"
                    "6. Say goodbye\n\n"
                    "Try typing: hello, purpose, hci, ai, reverse hello, or bye."
                )

            elif message == "purpose":
                response = (
                    "My purpose is to show a simple chatbot using traditional rules. "
                    "I use if and elif statements to match user input and give a response."
                )

            elif message == "hci":
                response = (
                    "HCI means Human-Computer Interaction. It is about how people use and interact with computers."
                )

            elif message == "ai":
                response = (
                    "AI means Artificial Intelligence. It is when computers perform tasks that usually need human thinking."
                )

            elif message.startswith("reverse"):
                text_to_reverse = user_text[7:].strip()

                if text_to_reverse == "":
                    response = "Please type something after reverse. Example: reverse chatbot"
                else:
                    response = "Reversed text: " + text_to_reverse[::-1]

            elif message in ["bye", "goodbye"]:
                response = "Goodbye! Thank you for chatting with me."

            else:
                response = (
                    "Sorry, I do not understand that question. "
                    "Please type help to see what I can answer."
                )

            await turn_context.send_activity(response)

        else:
            await turn_context.send_activity("Hello and welcome!")


BOT = SimpleTraditionalChatbot()


async def messages(req: web.Request) -> web.Response:
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)

    if response:
        return web.json_response(data=response.body, status=response.status)

    return web.Response(status=201)


APP = web.Application()
APP.router.add_post("/api/messages", messages)


if __name__ == "__main__":
    web.run_app(APP, host="localhost", port=3978)