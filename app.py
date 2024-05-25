!pip uninstall psycopg2
import os
import json
from crawl import *
from linebot.models import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort, render_template
import psycopg2


app = Flask(__name__)

Channel_Access_Token = '+rq5EEHCHR5pK6abD/3VuJZ8Q0iZxlb55AN6TzcBO6OC0f9buhiwdicHohpqPpnO8oHa0g/VHUl0AOz8q+yxkBoDmKSyuHZyQpUTQO8i93fI45O5CUdTnwiReYDSTKX+hUWM7Ye5uM0v4Zl61xz85gdB04t89/1O/w1cDnyilFU='
line_bot_api    = LineBotApi(Channel_Access_Token)
Channel_Secret  = '56f014f7e7e0c049940037987831171c'
handler = WebhookHandler(Channel_Secret)
conn = psycopg2.connect(
    database="dcsbhdut3v5fue",
    user="uq2rvdd232lmg",
    password="p328a4deb85279e7466144de758c11ac86611c3178e7188078552b18ec7190360",
    host="c97r84s7psuajm.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com",
    port=5432)
keywords = ['掛號', '議題', '橘子']
# handle request from "/callback" 
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body      = request.get_data(as_text=True)
    json_data = json.loads(body)
    msg = json_data['events'][0]['message']['text']      # 取得 LINE 收到的文字訊息
    tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
    if(event.message.text[:3:] in keywords and len(event.message.text)>3):
        key=event.message.text[:3:]      
        profile = line_bot_api.get_profile(event.source.user_id)
        cursor=conn.cursor()      
        cursor.execute(f"SELECT message_text FROM group_buying_message WHERE keyword='{key}';")
        message_text = cursor.fetchone()
        cursor.execute(f"SELECT index,product_id,emoji_id FROM message_emoji WHERE mid=(SELECT mid FROM group_buying_message WHERE keyword='{key}');")
        rows = cursor.fetchall()
        emojis=[]
        #將資料一筆一筆寫入list中
        for row in rows:
            emojis.append({'index': row[0],'productId': row[1],'emojiId': row[2]})
            message_text_d="".join(message_text)
            cursor.execute(f"SELECT name,quantity FROM group_buying_user WHERE mid=(SELECT mid FROM group_buying_message WHERE keyword='{key}');")
            users = cursor.fetchall()
        for user in users:
            message_text_d=message_text_d+"".join(user[0])+" "+"".join(user[1])+"\n"
            message_text_d=message_text_d+profile.display_name+" "+event.message.text[4::]
            message=TextSendMessage(message_text_d,emojis)
            line_bot_api.reply_message(event.reply_token,message)
            cursor.execute(f"INSERT INTO group_buying_user (mid, uid, name, quantity) VALUES ((SELECT mid FROM group_buying_message WHERE keyword='{key}'),'{event.source.user_id}','{profile.display_name}','{event.message.text[4::]}' );")
            conn.commit()
            cursor.close()
    #line_bot_api.reply_message(tk,TextSendMessage(msg))  # 回傳訊息
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
        msg2=event.reply_token
        NUM.append(msg2)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=len(NUM))
        )
        

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
