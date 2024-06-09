from prompt import Prompt
import os
from openai import OpenAI
from linebot.models import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort, render_template
from linebot.models import MessageEvent, TextMessage, TextSendMessage
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
        self.prompt = Prompt()
        self.model = os.getenv("OPENAI_MODEL", default = "gpt-3.5-turbo")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 500))

    def get_response(self):
        text=self.prompt.generate_prompt()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"""
            Source 你會幫我把內容都轉換為 google calendar 的邀請網址。
            Message 我會給你任何格式的訊息，需要整理裡面的內容並對應上google calendar 的渲染方式，中文字需要編碼。
            Channel 將內容整理成標題、時間、地點、描述。範例: ['與同事聚餐', '20230627T230000/20230627T233000', '美麗華', '具體描述']，並且要能整理出對應標題、行事曆時間、地點，其餘內容整理完後放在描述裡面，現在是 2024年，如果有兩筆資料中間會以分號；區隔，如果沒有分號(；)請依照語意分成另外一筆。
            Receiver 連結google行事曆表單需要點選的民眾。
            Effect 最後透過陣列回傳。

            {text}
            """}])
        num_sentences = len(gcal_list)
        for i in range(num_sentences):
            title = gcal_list[i][0] or 'TBC'
            date = gcal_list[i][1] or 'TBC'
            location = gcal_list[i][2] or 'TBC'
            desc = gcal_list[i][3] or 'TBC'
            gcal_url: str = create_gcal_url(title, date, location, desc)
        return gcal_url

    def add_msg(self, text):
        self.prompt.add_msg(text)

# 從 Choice 物件中取得回應的內容


# 印出回應的內容


# 計算句子的數量




