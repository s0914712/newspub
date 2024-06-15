import os
from openai import OpenAI
import plotly.express as px
import openai
import json
import psycopg2
from crawl import *
from linebot.models import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort, render_template
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from chatgpt import *
from pytrends.request import TrendReq
import kaleido
import pyimgur
pytrends = TrendReq(hl='en-US', tz=360)
chatgpt = ChatGPT()
gpt_cal=GPT_Cal()
gpt_news=GPT_News()
app = Flask(__name__)
Channel_Access_Token = '+rq5EEHCHR5pK6abD/3VuJZ8Q0iZxlb55AN6TzcBO6OC0f9buhiwdicHohpqPpnO8oHa0g/VHUl0AOz8q+yxkBoDmKSyuHZyQpUTQO8i93fI45O5CUdTnwiReYDSTKX+hUWM7Ye5uM0v4Zl61xz85gdB04t89/1O/w1cDnyilFU='
line_bot_api    = LineBotApi(Channel_Access_Token)
Channel_Secret  = '56f014f7e7e0c049940037987831171c'
client_id='a0f19779af81cc0'
handler = WebhookHandler(Channel_Secret)
conn = psycopg2.connect(
    database="dcsbhdut3v5fue",
    user="uq2rvdd232lmg",
    password="p328a4deb85279e7466144de758c11ac86611c3178e7188078552b18ec7190360",
    host="c97r84s7psuajm.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com",
    port=5432)
reply_msg=""
# handle request from "/callback" 
@app.route("/callback", methods=['POST'])
def glucose_graph(client_id, imgpath):
    im = pyimgur.Imgur(client_id)
    upload_image = im.upload_image(imgpath, title="Uploaded with PyImgur")
    return upload_image.link
def plot_graph(kw_list):
    pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d')
    data = pytrends.interest_over_time()
    data= data.reset_index()
    data = data.rename(columns={"data": "date"})
    fig = px.line(data, x="date", y=["海空戰力", "快艇"], title="關鍵字搜索量")
    fig.write_image("./figgure.png")
    img_url=glucose_graph(client_id,"./figgure.png")     
    return  img_url
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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if "關鍵字" in msg:
	kw_list = ["海空戰力", "快艇"]
	img_url=plot_graph(kw_list)	    
	line_bot_api.reply_message(event.reply_token,TextSendMessage(img_url))
    if "新聞" in msg:
        result = news_crawler()
        result2= CNAnews_crawler()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result+result2)
        )
    if "AI" in msg:
        OPENAI_API_KEY  = os.environ['APIKEY']
        chatgpt.add_msg(f"HUMAN:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))# new
    if "與會" in msg or "出席" in msg:
        gpt_cal.add_msg(f"HUMAN:{event.message.text}?\n")
        gcal_url =[]
        gcal_url = gpt_cal.get_response()
        for i in range(len(gcal_url)):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=gcal_url))# new
    if "擬答" in msg: 
        gpt_news.add_msg(f"HUMAN:{event.message.text}?\n")
        respon =[]
        respon = gpt_news.get_response()
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=respon))# new
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
        message_text_d=""
        table_columns = '(name,value)'
        #紀錄
        values=msg[2:]
        profile = line_bot_api.get_profile(event.source.user_id)
        record = (profile.display_name,values)
        name=profile.display_name
        Id=profile.user_id
        cursor = conn.cursor()
        cursor.execute("INSERT INTO userdata (name, userid) VALUES (%s, %s);",record)
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
    if "刪除" in msg:
        uid=msg[2:]
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM userdata WHERE name = '{uid}';")
        conn.commit()
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
    if "取消" in msg:
        profile = line_bot_api.get_profile(event.source.user_id)
        name=profile.display_name
        Id=profile.user_id
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM userdata WHERE name = '{profile.display_name}';")
        conn.commit()
        cursor.close()
    if "更新" in msg:
        line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text='hello',
            contents= {
          "type": "bubble",
          "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "修正狀態機器人",
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
                    "layout": "baseline",
                    "spacing": "sm",
                    "contents": [
                      {
                        "type": "text",
                        "text": "說明",
                        "color": "#aaaaaa",
                        "size": "sm",
                        "flex": 1
                      },
                      {
                        "type": "text",
                        "text": "按下面的按鈕就可以更改狀態",
                        "wrap": True,
                        "color": "#666666",
                        "size": "sm",
                        "flex": 5
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
                  "type": "message",
                  "label": "更改狀態：參座有空",
                  "text": "更改狀態：參座有空"
                }
              },
              {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                  "type": "message",
                  "label": "更改狀態：參座沒空",
                  "text": "更改狀態：參座沒空"
                }
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "margin": "sm"
              },
              {
                "type": "button",
                "action": {
                  "type": "message",
                  "label": "查詢",
                  "text": "查詢"
                }
              }
            ],
            "flex": 0
          }
        }))

    if "更改狀態：參座有空" in msg:
        uid="沒空"
        new_uid="有空"
        cursor = conn.cursor()
        cursor.execute(f"UPDATE userdata SET userid = '{new_uid}' WHERE userid = '{uid}';")
        conn.commit()
        cursor.close()
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"已更改狀態：{new_uid}") 
            )
    if "更改狀態：參座沒空" in msg:
        uid="沒空"
        new_uid="有空"
        cursor = conn.cursor()
        cursor.execute(f"UPDATE userdata SET userid = '{uid}' WHERE userid = '{new_uid}';")
        conn.commit()
        cursor.close()
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"已更改狀態：{uid}") 
            )
    if "？" in msg:
        line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text='hello',
            contents= {
          "type": "bubble",
          "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "掛號機器人，輸入 怎麼用 或?",
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
                    "layout": "baseline",
                    "spacing": "sm",
                    "contents": [
                      {
                        "type": "text",
                        "text": "說明",
                        "color": "#aaaaaa",
                        "size": "sm",
                        "flex": 1
                      },
                      {
                        "type": "text",
                        "text": "按下面的按鈕就可以掛號或取消",
                        "wrap": True,
                        "color": "#666666",
                        "size": "sm",
                        "flex": 5
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
                  "type": "message",
                  "label": "輸入：掛號+軍線",
                  "text": "掛號"
                }
              },
              {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                  "type": "message",
                  "label": "取消",
                  "text": "取消"
                }
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "margin": "sm"
              },
              {
                "type": "button",
                "action": {
                  "type": "message",
                  "label": "查詢",
                  "text": "查詢"
                }
              }
            ],
            "flex": 0
          }
}))
    if "怎麼用" in msg:
        line_bot_api.reply_message(
        event.reply_token,
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
                        "text": "查動態、查新聞、掛號、串聯GOOGLE日曆(給他行程)",
                        "wrap": True,
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
                        "text": "輸入：查詢 or 輸入：掛號+軍線"+"\n"+"ex:掛號683123",
                        "wrap": True,
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
              "uri": "https://liff.line.me/1645278921-kWRPP32q/?accountId=301crdbq"
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
    else:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='收到')
            )
        

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
