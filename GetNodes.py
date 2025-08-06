"""
某人的小脚本
目前支持的网站：
    1、v2raya.com
    2、clashnode.cc
这两个基本上就涵盖了网上能找到的绝大多数节点（非github)
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import base64
import datetime
import requests
import time
import sys
import re
import pytz

# 可调参数
TRY_LIM = 10 # 获取内容尝试次数
DEBUG = False # 是否开启调试模式
# browse
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0'
}
targets = []
urls : str = ""
output_file = "urls.txt"

def driver_init(choice : str):
    global driver
    if choice == '1':
        edge_options = webdriver.EdgeOptions()
        edge_options.add_argument('--headless')  # 无头模式
        edge_options.add_argument('--disable-gpu')
        driver = webdriver.Edge(options = edge_options)
    elif choice == '2':
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument('--headless')  # 无头模式
        firefox_options.add_argument('--disable-gpu')
        driver = webdriver.Firefox(options = firefox_options)
    elif choice == '3':
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options = chrome_options)
    else:
        if DEBUG: print('啊？什么意思？')
        sys.exit()

def time_init():
    global lt, tz, now, formatted_time, update_time, tm_mon, tm_mday
    lt = time.localtime(time.time())
    tz = pytz.timezone("Asia/Shanghai")
    now = datetime.datetime.now(tz)
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    update_time = "## Update Time: " + formatted_time + "\n```\n"
    tm_mon = str(lt.tm_mon) if lt.tm_mon >= 10 else '0' + str(lt.tm_mon)
    tm_mday = str(lt.tm_mday) if lt.tm_mday >= 10 else '0' + str(lt.tm_mday)

def urls_init():
    # Get share urls
    # Supported: clashnode.cc, v2raya.com
    # print("Get share urls...")
    # 1、freeclashnode.com
    # https://node.clashnode.cc/uploads/2025/01/0-20250121.txt
    for i in range(4):
        tmp = 'https://node.clashnode.cc/uploads/{0}/{1}/{3}-{0}{1}{2}.txt'.format(lt.tm_year, tm_mon, tm_mday, i)
        if DEBUG: print(tmp)
        targets.append(tmp)
    if DEBUG: print("freeclashnode.com Finished!")
    
    #2、v2raya.com
    web_url = 'https://v2raya.net/free-nodes/free-v2ray-node-subscriptions.html'
    # //*[@id="free_subscription_list"]/ul/li[1]/code/text()
    try_cnt = 1
    while try_cnt <= TRY_LIM:
        try:
            driver.get(web_url)
        except Exception as e:
            if DEBUG: print('[ERROR]', e)
            if DEBUG: print('尝试次数：', try_cnt)
            if DEBUG: print('重试...')
            time.sleep(1)
        else:
            for i in range(1, 14):
                targets.append(driver.find_element(By.XPATH, 
                    f'/html/body/div[2]/main/div[1]/article/div/ul/li[{i}]/code').text
                )
            break
    if try_cnt > TRY_LIM:
        if DEBUG: print('无法连接！')
        sys.exit(0)
    if DEBUG: print("v2raya.com Finished!")

def get_nodes():
    global urls

    # Get share content
    if DEBUG: print("Get share content...")
    j = 0
    for op in targets:
        if DEBUG: print(j, j / len(targets) * 100)
        j += 1
        # 使用 selenium 获取订阅链接内容
        try_cnt = 1
        while try_cnt <= TRY_LIM:
            try:
                driver.get(op)
            except Exception as e:
                if DEBUG: print('[ERROR]', e)
                if DEBUG: print('尝试次数：', try_cnt)
                if DEBUG: print('重试...')
                time.sleep(1)
            else:
                try_cnt = TRY_LIM + 25
                content = driver.find_element(By.TAG_NAME, "body").text
        
        # 对于未编码内容 - 直接加仓
        if content.find(':') != -1:
            urls += content
            continue
        
        # 对于b64编码 - 解码加仓
        # base64 解码填充
        pad_num = len(content) % 4
        content = content[:len(content)-pad_num]
        
        # base 64 解码
        add_ctt = base64.b64decode(content).decode('unicode_escape')
        urls += add_ctt
    
    urls_lst = list(set(urls.split('\n')))
    urls = ""
    for i in urls_lst:
        i = i.strip()
        if i != '':
            urls += i + '\n'
    urls = urls[:-1]

def write_file():
    global urls
    # B64 encode
    urls = urls.encode()
    urls = base64.b64encode(urls).decode('unicode_escape')
    with open("urls.txt", "w", encoding='utf-8') as f:
        f.write(urls)
        if DEBUG: print("urls.txt 已生成！")
    
    urls = update_time + urls + "\n```"
    if DEBUG: print(urls[:25])
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(urls)
        if DEBUG: print("README.md 已生成！")
    
    with open("index.html", "w", encoding='utf-8') as f:
        f.write(urls)
        if DEBUG: print("index.html 已生成！")

def main(args):
    global choice
    if len(args) > 1:
        choice = args[1]
    else:
        choice = input('''
        --- 选择浏览器 ---
        [1] - Microsoft Edge
        [2] - Firefox
        [3] - Google Chrome
        请选择浏览器（输入数字）: ''')
    driver_init(choice)
    time_init()
    urls_init()
    get_nodes()
    write_file()
    return 

if __name__ == "__main__":
    main(sys.argv)
    if DEBUG: print("Done!")