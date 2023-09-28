from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import os, json, requests

line_bot_api = LineBotApi(os.environ['LINEBOT_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINEBOT_SECRET'])
discord_webhook = os.environ['DISCORD_WEBHOOK']
# line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
# line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
# working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)

# domain root
@app.route('/')
def home():
    return 'Hello, World!'

# @app.route("/")
# def root():
#     return 'OK'

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Check token and/or secret")
        abort(400)
    return 'OK'

def create_request_data(event, text=None) -> dict:
    profile = line_bot_api.get_group_member_profile(event.source.group_id,event.source.user_id)
    
    request_data = {
        "content":text,
        "username":profile.display_name + " from LINE",
        "avatar_url":profile.picture_url
    }

    return request_data

def get_binary_data(event) -> str:
    content = line_bot_api.get_message_content(event.message.id)
    file = b""
    for chunk in content.iter_content():
        file += chunk
    return file

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    request_data = create_request_data(event, event.message.text)
    requests.post(url=discord_webhook, data=request_data)

# @line_handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     global working_status
#     if event.message.type != "text":
#         return

#     if event.message.text == "說話":
#         working_status = True
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text="我可以說話囉，歡迎來跟我互動 ^_^ "))
#         return

#     if event.message.text == "閉嘴":
#         working_status = False
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text="好的，我乖乖閉嘴 > <，如果想要我繼續說話，請跟我說 「說話」 > <"))
#         return

#     if working_status:
#         chatgpt.add_msg(f"HUMAN:{event.message.text}?\n")
#         reply_msg = chatgpt.get_response().replace("AI:", "", 1)
#         chatgpt.add_msg(f"AI:{reply_msg}\n")
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text=reply_msg))


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    request_data = create_request_data(event)
    file = get_binary_data(event)
    requests.post(url=discord_webhook, data=request_data, files={'media.jpg':file})

@handler.add(MessageEvent, message=VideoMessage)
def handle_image(event):
    request_data = create_request_data(event)
    file = get_binary_data(event)
    requests.post(url=discord_webhook, data=request_data, files={'media.mp4':file})

@handler.add(MessageEvent, message=AudioMessage)
def handle_image(event):
    request_data = create_request_data(event)
    file = get_binary_data(event)
    requests.post(url=discord_webhook, data=request_data, files={'media.mp3':file})

@handler.add(MessageEvent, message=FileMessage)
def handle_image(event):
    request_data = create_request_data(event)
    file_name = event.message.file_name
    file = get_binary_data(event)
    requests.post(url=discord_webhook, data=request_data, files={file_name:file})


if __name__ == "__main__":
    app.run()
