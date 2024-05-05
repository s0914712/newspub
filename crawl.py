import requests
from bs4 import BeautifulSoup


def news_crawler():
    base = "https://news.cnyes.com"
    url  = "https://news.cnyes.com/news/cat/headline"
    re   = requests.get(url)
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    }
    content = ""

    soup = BeautifulSoup(re.text, "html.parser")
    data = soup.find_all("a", {"class": "_1Zdp"})
    
    for index, d in enumerate(data):
        if index <8:
            title = d.text
            href  = base + d.get("href")
            content += "{}\n{}\n".format(title, href)
        else:
            break
        
    return content
