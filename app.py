import os
import json
from crawl import *
from linebot.models import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort, render_template


app = Flask(__name__)

Channel_Access_Token = '+rq5EEHCHR5pK6abD/3VuJZ8Q0iZxlb55AN6TzcBO6OC0f9buhiwdicHohpqPpnO8oHa0g/VHUl0AOz8q+yxkBoDmKSyuHZyQpUTQO8i93fI45O5CUdTnwiReYDSTKX+hUWM7Ye5uM0v4Zl61xz85gdB04t89/1O/w1cDnyilFU='
line_bot_api    = LineBotApi(Channel_Access_Token)
Channel_Secret  = '56f014f7e7e0c049940037987831171c'
handler = WebhookHandler(Channel_Secret)


# handle request from "/callback" 
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body      = request.get_data(as_text=True)
    json_data = json.loads(body)
    msg = json_data['events'][0]['message']['text']      # 取得 LINE 收到的文字訊息
    tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
    line_bot_api.reply_message(tk,TextSendMessage(msg))  # 回傳訊息
    print(tk,msg)
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
    NUM=["123", 'xyz', 'zara', 'abc']
    if "新聞" in msg:
        result = news_crawler()
        result2= CNAnews_crawler()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result+result2)
        )
    if "掛號" in msg:
        NUM.append("掛號")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=NUM[3])
        )
    else:
        msg2=event.reply_token,                 
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg+msg2)
        )
        

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
