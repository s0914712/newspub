import os
from crawl import *
from linebot.models import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort, render_template


app = Flask(__name__)

Channel_Access_Token = 'SCr6Fgr66ZAhirGJ8SEeUwcofJVaQUeM4IgE1U5vzq1aTtfszwX+PzZpGdLEzO0M8oHa0g/VHUl0AOz8q+yxkBoDmKSyuHZyQpUTQO8i93eNCv+9ZchpR5vvBPxCkQbji/oZ4c6bpaVeQsGBe6F/ygdB04t89/1O/w1cDnyilFU='
line_bot_api    = LineBotApi(Channel_Access_Token)
Channel_Secret  = '56f014f7e7e0c049940037987831171c'
handler = WebhookHandler(Channel_Secret)


# handle request from "/callback" 
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body      = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# handle text message
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text

    if "新聞" in msg:
        result = news_crawler()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
        )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
