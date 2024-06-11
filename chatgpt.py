from prompt import Prompt
import os
from openai import OpenAI
from linebot.models import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort, render_template
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import uvicorn
import re
import urllib.parse
import ast
client = OpenAI()

client.api_key = os.getenv('APIKEY')

def is_url_valid(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def delete_strings(s):
    # Step 1: Delete all contents from '#' to the next '&' character
    s = re.sub(r'#[^&]*', '', s)

    # Step 2: If '&openExternalBrowser=1' is not at the end, add it
    if '&openExternalBrowser=1' != s:
        s += '&openExternalBrowser=1'
    return s


def create_gcal_url(
        title='看到這個..請重生',
        date='20230524T180000/20230524T220000',
        location='那邊',
        description=''):
    base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
    event_url = f"{base_url}&text={urllib.parse.quote(title)}&dates={date}&location={urllib.parse.quote(location)}&details={urllib.parse.quote(description)}"
    return event_url + "&openExternalBrowser=1"


def arrange_flex_message(gcal_url: str, action: dict) -> FlexSendMessage:
    return FlexSendMessage(alt_text='行事曆網址', contents={
        "type": "bubble",
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
                            "label": "WEBSITE",
                            "uri": gcal_url
                        }
                    },
                    action
                ],
            "flex": 0
        }
    })

class ChatGPT:
    def __init__(self):
        self.prompt = Prompt()
        self.model = os.getenv("OPENAI_MODEL", default = "gpt-4-1106-preview")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 500))

    def get_response(self):
        response = client.chat.completions.create(
            model=self.model,
            messages=self.prompt.generate_prompt(),
        )
        return response.choices[0].message.content

    def add_msg(self, text):
        self.prompt.add_msg(text)
class GPT_Cal:
    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", default = "gpt-3.5-turbo")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 500))
        self.text="2014年三月五日在台北美麗華餐廳與同事聚餐"
            #Source 你會幫我把內容都轉換為 google calendar 的邀請網址。
            #Message 我會給你任何格式的訊息，需要整理裡面的內容並對應上google calendar 的渲染方式，中文字需要編碼，
            #Channel 如果開頭有"國會組報告"，那"預"字後的文字會有時間，"時"字後面會有內容，例如：國會組報告，國防部陸常次預5/9日(週四)，1400時於辦公室主持無人機預算說明。這代表"5/9(週四)，1400時"時間是20240509T1400，於辦公室代表地點在"立委辦公室"，後面的主持無人機預算說明代表內容為"陸常次主持預算說明會"將內容整理成標題、時間、地點、描述。範例: ['無人機預算說明', '202400509T140000/202400509T2330000', '委員辦公室', '具體描述']，並且要能整理出對應標題、行事曆時間、地點，其餘內容整理完後放在描述裡面，現在是 2024年，如果有兩筆資料中間會以分號；區隔，如果沒有分號(；)請依照語意分成另外一筆。
            #Receiver 連結google行事曆表單需要點選的民眾。
            #Effect 最後透過陣列回傳。
    def get_response(self):
        text=self.text
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"""
            Source 你會幫我把內容都轉換為  google calendar 的邀請網址。
            Message 我會給你任何格式的訊息，需要整理裡面的內容並對應上google calendar 的渲染方式，中文字需要編碼，
            Channel 將內容整理成標題、時間、地點、描述。範例: ['與同事聚餐', '20240627T230000/20240627T233000', '美麗華', '具體描述']，並且要能整理出對應標題、行事曆時間、地點，其餘內容整理完後放在描述裡面，現在是 2024 年。
            Receiver 連結google行事曆表單需要點選的民眾。
            Effect 最後透過陣列回傳。
            {text}
            """}])
        first_choice = response.choices[0]
        processed_text: str = response.choices[0].message.content
        gcal_list: list = ast.literal_eval(processed_text)
        num_sentences = len(gcal_list)
        title = gcal_list[0] or 'TBC'
        date = gcal_list[1] or 'TBC'
        location = gcal_list[2] or 'TBC'
        desc = gcal_list[3] or 'TBC'
        gcal_url: str = create_gcal_url(title, date, location, desc)
        return gcal_url 

    def add_msg(self, text):
        self.text=text
class GPT_News:
    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", default = "gpt-3.5-turbo")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 500))
        self.text=""
            #Source 你會幫我把內容都轉換為 google calendar 的邀請網址。
            #Message 我會給你任何格式的訊息，需要整理裡面的內容並對應上google calendar 的渲染方式，中文字需要編碼，
            #Channel 如果開頭有"國會組報告"，那"預"字後的文字會有時間，"時"字後面會有內容，例如：國會組報告，國防部陸常次預5/9日(週四)，1400時於辦公室主持無人機預算說明。這代表"5/9(週四)，1400時"時間是20240509T1400，於辦公室代表地點在"立委辦公室"，後面的主持無人機預算說明代表內容為"陸常次主持預算說明會"將內容整理成標題、時間、地點、描述。範例: ['無人機預算說明', '202400509T140000/202400509T2330000', '委員辦公室', '具體描述']，並且要能整理出對應標題、行事曆時間、地點，其餘內容整理完後放在描述裡面，現在是 2024年，如果有兩筆資料中間會以分號；區隔，如果沒有分號(；)請依照語意分成另外一筆。
            #Receiver 連結google行事曆表單需要點選的民眾。
            #Effect 最後透過陣列回傳。
    def get_response(self):
        text=self.text
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"""
            Source 你是一位政府機關的回應客服人員 會幫我把內容都進行修飾，回應給政府機關上層使他們了解真相
            Message 你會收到一個連結，需要對於連結內的文字內容做出回應
            Channel 將連結內容整理成"基調"與"補充說明"兩段，內容需要200字以上，"基調"是對於這整篇文章的大意，分成兩段，每段不超過75個字，"補充說明" ：內容分成三段，第一段是說明消息來源，第二段是說名事情經過，第三段式政府機關的後續處置。#例如收到"https://www.msn.com/zh-tw/news/national/%E6%B5%B7%E8%BB%8D%E6%96%B0%E5%85%B5%E4%B8%8D%E9%9B%86%E5%90%88%E8%BA%B2%E5%AF%A2%E5%AE%A4-%E8%BE%B1%E7%BD%B5%E5%A3%AB%E5%AE%98%E9%95%B7%E4%B8%89%E5%AD%97%E7%B6%93-%E8%AA%8D%E7%BD%AA%E7%8D%B2%E7%B7%A9%E5%88%91/ar-BB1niuWq?ocid=BingNewsSearch"：
            #基調："郭員為犯刑法公然侮辱長官罪，經地方法院判決處有期徒刑三個月。本案經調查屬實，處以相關處分，且該員已停止訓練"，補充說明：一、軍事訓練二兵莊豐斌於民國112年3月8日進入高雄海軍新兵訓練中心服役，進行常備役軍事訓練（於112年6月15日因病停止訓練）。吳丹為高雄海軍新兵訓練中心中士班長，王賢詰則為高雄海軍新兵訓練中心士官長班長，均為莊豐斌之直屬長官。於112年5月28日20時許，部隊集合時，因莊豐斌未步出高雄海軍新兵訓練中心寢室配合部隊集合，遭到糾舉心生不滿辱罵幹部，函送憲兵隊偵辦。二、橋頭地院審理後依陸海空軍刑法之公然侮辱長官罪，處徒刑3月，緩刑2年，須支付公庫6萬元。
            #另一個例子是收到"https://udn.com/news/story/10930/8021742"的連結，回復內容如下：一、海巡署依據海岸巡防法(108年版)，主要任務為處浬海域執法、民用船舶、公務船舶等非軍用船舶之活動與維持海上秩序。二、海軍主要任務為制海，處理軍用船舶活動，臺灣周遭海上應變區內不明或可疑海上目標之傳報以及情資支援，由雙方共同聯繫協調，三、海軍和海巡權責分配，24浬以外屬海軍海偵艦負責，12至24浬屬海軍港偵艦任務範圍，12浬內則屬海巡及岸巡任務範圍。海軍另有近岸港巡艇，也須擔負防務。昨日海象許可，相關水域都應有在航艦艇。
            
            Effect 最後透過二段或三段式文字回傳。
            {text}
            """}])
        processed_text: str = response.choices[0].message.content
        return processed_text 
    def add_msg(self, text):
        self.text=text
# 從 Choice 物件中取得回應的內容


# 印出回應的內容

# 計算句子的數量




