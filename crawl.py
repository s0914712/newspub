from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
headers = {
    	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
	}
def news_crawler():
    r = requests.get('https://www.cna.com.tw/search/hysearchws.aspx?q=海軍', headers=headers)
    base_url='https://www.cna.com.tw'
    soup = BeautifulSoup(r.text, 'html.parser')
    anime_items = soup.select('li')
    wrap = soup.find("img").get("alt")
    #print(wrap)
    all_title = []
    for i in anime_items:
      try:
          all_title.append(i.find("img").get("alt"))
          news_list_url = base_url + i.find("a").get("href")
          all_title.append("\n")
          all_title.append(news_list_url)
          all_title.append("\n")
      except:
        continue
    msg = ""
    msg = "".join(map(str,all_title[69:96]))
    url = "https://www.ettoday.net/news/focus/%E8%BB%8D%E6%AD%A6/%E5%8F%B0%E7%81%A3/"
    response = requests.get(url)
    bs = BeautifulSoup(response.text, "html.parser")
    result = bs.find_all("h3")
    all_title = []
    for i in result:
  	try:
      	   all_title.append(i.find("a").get("title"))
           all_title.append(i.find("a").get("href"))
   	except:
      	   continue
	   print(all_title)
    return msg.append(all_title)

  
