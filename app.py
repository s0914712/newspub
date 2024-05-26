import os
import json
import psycopg2
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
    if "新聞" in msg:
        result = news_crawler()
        result2= CNAnews_crawler()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result+result2)
        )
    if "查詢" in msg:
         message_text_d=""
   
         cursor = conn.cursor()
        #cursor.execute("INSERT INTO userdata (name, userid) VALUES (%s, %s);", ("小明", "a123456"))
         cursor.execute("SELECT * FROM userdata;")#選擇資料表userdata
         rows = cursor.fetchall() #讀出所有資料
         conn.commit()
         for row in rows:   #將讀到的資料全部print出來
              message_text_d=message_text_d+""+str(row[0])+" "+""+str(row[1])+str(row[2])+"\n"
        
         line_bot_api.reply_message(
         event.reply_token,
         TextSendMessage(message_text_d) 
            )
         cursor.close()
    if "掛號" in msg:
        table_columns = '(name,value)'
        #紀錄
        values=msg[2:]
        profile = line_bot_api.get_profile(event.source.user_id)
        record = (profile.display_name,values)
        name=profile.display_name
        Id=profile.user_id
        cursor = conn.cursor()
        cursor.execute("INSERT INTO userdata (name, userid) VALUES (%s, %s);",record)
        
        conn.commit()
        line_bot_api.reply_message(event.reply_token,profile)
    if "刪除" in msg:
        uid=msg[2:]
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM userdata WHERE name = '{uid}';")
        conn.commit()
        cursor.execute("SELECT * FROM userdata;")#選擇資料表userdata
        rows = cursor.fetchall() #讀出所有資料
        conn.commit()
        cursor.close()
    if "更新" in msg:
        uid=msg[2:4]
        new_uid=msg[4:6]
        cursor = conn.cursor()
        cursor.execute(f"UPDATE userdata SET userid = '{new_uid}' WHERE userid = '{uid}';")
        conn.commit()
        cursor.close()
        line_bot_api.reply_message(
         event.reply_token,
         TextSendMessage(uid+"  "+new_uid) 
            )
    else:
        line_bot_api.push_message(event.reply_token, 
        FlexSendMessage(
        alt_text='hello',
        contents={ 
          "type": "bubble",
          "hero": {
            "type": "image",
            "url": "https://ocacnews.net/articleImages/202212/M2_0CE27D18-7BDD-5AEE-565B-CA45D4B96A79.png",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
              "type": "uri",
              "uri": "https://line.me/"
            }
          },
          "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "動態查詢機器人",
                "weight": "bold",
                "size": "xl"
              },
              {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "spacing": "sm",
                "contents": [
                  {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                      {
                        "type": "text",
                        "text": "功能",
                        "color": "#aaaaaa",
                        "size": "sm",
                        "flex": 1
                      },
                      {
                        "type": "text",
                        "text": "查動態、查新聞、掛號",
                        "wrap": true,
                        "color": "#666666",
                        "size": "sm",
                        "flex": 5
                      }
                    ]
                  },
                  {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                      {
                        "type": "text",
                        "text": "使用方法",
                        "color": "#aaaaaa",
                        "size": "sm",
                        "align": "start"
                      },
                      {
                        "type": "text",
                        "text": "輸入：查詢   or 輸入：掛號+軍線",
                        "wrap": true,
                        "color": "#666666",
                        "size": "sm",
                        "flex": 5,
                        "margin": "none",
                        "action": {
                          "type": "message",
                          "label": "action",
                          "text": "範例：查詢"
                        }
                      }
                    ]
                  }
                ]
              }
            ]
      },
      "footer": {
       "type": "box",
       "layout": "vertical",
       "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "style": "link",
            "height": "sm",
            "action": {
              "type": "uri",
              "label": "CALL",
              "uri": "https://line.me/"
            }
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [],
            "margin": "sm"
          }
        ],
        "flex": 0
      }
    }))
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='收到')
            )
        

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
