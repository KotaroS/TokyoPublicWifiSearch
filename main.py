import os
import sys
import wifispot
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, LocationMessage,
    CarouselColumn, CarouselTemplate, URITemplateAction,
    TemplateSendMessage
)

app = Flask(__name__)

# 環境変数からchannel_secret・channel_access_tokenを取得
channel_secret = os.environ['LINE_CHANNEL_SECRET']
channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    ido = float(event.message.latitude)
    keido = float(event.message.longitude)
    app.logger.info("Request body: " + ido + "," + keido)
    spots = wifispot.getWifiSpot(ido, keido)

    columns = [
        CarouselColumn(
            title=column.get("name"),
            text=column.get("ssid"),
            actions=[
                URITemplateAction(
                    label=column.get("name"),
                    uri="https://maps.google.com/maps?q=" + column.get("ido") + "," + column.get("keido")
                )
            ]
        ) for column in spots
    ]
    messages = TemplateSendMessage(
        alt_text="お近くの公衆Wifiスポットを提供します",
        template=CarouselTemplate(columns=columns)
    )
    
    line_bot_api.reply_message(
        event.reply_token,
        messages=messages)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.type == "message":
         line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text='位置情報を送ってもらうと近くの公衆Wifiスポットをリプライします'),
                    TextSendMessage(text='line://nv/location'),
                ]
            )

if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)