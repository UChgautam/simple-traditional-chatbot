import os
from aiohttp import web
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes


APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
AZURE_LANGUAGE_ENDPOINT = os.environ.get("AZURE_LANGUAGE_ENDPOINT", "https://hemangainstance.openai.azure.com/")
AZURE_LANGUAGE_KEY = os.environ.get("AZURE_LANGUAGE_KEY", "1CZ9O8exC6bAowZxoYiSuTkucrtZYub3DaLjyL4yrg4LuC9MVf4aJQQJ99CFACYeBjFXJ3w3AAABACOGPARM")

SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


def get_text_analytics_client():
    if not AZURE_LANGUAGE_ENDPOINT or not AZURE_LANGUAGE_KEY:
        return None

    credential = AzureKeyCredential(AZURE_LANGUAGE_KEY)
    return TextAnalyticsClient(
        endpoint=AZURE_LANGUAGE_ENDPOINT,
        credential=credential
    )


TEXT_CLIENT = get_text_analytics_client()


class AzureIntegratedChatbot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type != ActivityTypes.message:
            await turn_context.send_activity("Hello! Type help to see what I can do.")
            return

        user_text = turn_context.activity.text

        if user_text is None or user_text.strip() == "":
            await turn_context.send_activity(
                "I did not understand that. Please type help to see what I can do."
            )
            return

        message = user_text.lower().strip()

        if message in ["hi", "hello", "hey"]:
            response = (
                "Hello! I am a traditional chatbot connected to Azure AI Language. "
                "Type help to see what I can do."
            )

        elif message == "help":
            response = (
                "Here are my capabilities:\n"
                "1. Say hello\n"
                "2. Explain my purpose\n"
                "3. Explain HCI\n"
                "4. Explain AI\n"
                "5. Reverse your text\n"
                "6. Analyze sentiment using Azure AI Language\n"
                "7. Say goodbye\n\n"
                "Try: hello, purpose, hci, ai, reverse chatbot, "
                "sentiment I love this class, or bye."
            )

        elif message == "purpose":
            response = (
                "My purpose is to show how a traditional rule-based chatbot can be "
                "connected to a cloud AI service. I still use rules for basic commands, "
                "but I use Azure AI Language for sentiment analysis."
            )

        elif message == "hci":
            response = (
                "HCI means Human-Computer Interaction. It studies how people use "
                "computer systems and how systems can be easier to use."
            )

        elif message == "ai":
            response = (
                "AI means Artificial Intelligence. It helps computers do tasks that "
                "usually need human thinking, such as understanding text."
            )

        elif message.startswith("reverse"):
            text_to_reverse = user_text[7:].strip()

            if text_to_reverse == "":
                response = "Please type something after reverse. Example: reverse chatbot"
            else:
                response = "Reversed text: " + text_to_reverse[::-1]

        elif message.startswith("sentiment"):
            text_to_analyze = user_text[9:].strip()
            response = analyze_sentiment(text_to_analyze)

        elif message in ["bye", "goodbye"]:
            response = "Goodbye! Thank you for chatting with me."

        else:
            response = (
                "Sorry, I do not understand that question. Please type help to see "
                "what I can answer."
            )

        await turn_context.send_activity(response)


def analyze_sentiment(text_to_analyze):
    if text_to_analyze == "":
        return "Please type a sentence after sentiment. Example: sentiment I am happy today."

    if TEXT_CLIENT is None:
        return (
            "Azure AI Language is not connected yet. Please set AZURE_LANGUAGE_ENDPOINT "
            "and AZURE_LANGUAGE_KEY, then restart the bot."
        )

    try:
        result = TEXT_CLIENT.analyze_sentiment([text_to_analyze])[0]

        return (
            f"Azure sentiment result: {result.sentiment}\n"
            f"Positive score: {result.confidence_scores.positive:.2f}\n"
            f"Neutral score: {result.confidence_scores.neutral:.2f}\n"
            f"Negative score: {result.confidence_scores.negative:.2f}"
        )

    except Exception as error:
        return (
            "I could not connect to Azure AI Language. Please check your endpoint, "
            f"key, and internet connection. Error: {str(error)}"
        )


BOT = AzureIntegratedChatbot()


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
