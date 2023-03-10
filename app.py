import os
import sys

from argparse import ArgumentParser
from flask import Flask, request, abort, send_file
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

from fsm import PTTMachine, states, transitions
from utils import send_text_message, send_image_message

webhook_netloc = 'https://line-bot-python-flask-wmdi.onrender.com'

machine = {}

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        send_text_message(event.reply_token, event.message.text)
    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        userID = event.source.user_id
        if userID not in machine:
            machine[userID] = PTTMachine(states=states, transitions=transitions, initial='init', auto_transitions=False, show_conditions=True)
        print(f"\nFSM STATE: {machine[userID].state}")
        print(f"REQUEST BODY: \n{body}")
        machine[userID].advance(event)
        if event.message.text.lower() == "show fsm":
            send_image_message(event.reply_token, webhook_netloc + "/show-fsm")
    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    arg_parser = ArgumentParser(usage='Usage: python ' + __file__ + ' [--port <port>] [--help]')
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
