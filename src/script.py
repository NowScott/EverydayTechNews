import os
from zoneinfo import ZoneInfo  # Python 3.9+
from selenium import webdriver
from datetime import datetime , timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_all_news():
    # 设置 Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = Options()
    options.headless = True  # type: ignore # 在无头模式下运行
    driver = webdriver.Chrome(service=service, options=options)
    news_data = {}
    try:
        
        # 打开网页
        driver.get('https://digi.ithome.com/')
        # 抓取日榜新闻
        # 等待 JavaScript 加载新闻项目
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.bd.order#d-1'))
        )
        # 选择列表中的所有新闻项目
        news_items = driver.find_elements(By.CSS_SELECTOR, f'ul.bd.order#d-1 li a')
        news_data = []
        # 提取每个新闻的标题和链接，并存储到列表中
        for item in news_items:
            title = item.get_attribute('title')
            link = item.get_attribute('href')
            news_data.append({'title': title, 'link': link})
    finally:
        # 关闭浏览器
        driver.quit()
    return news_data

def save_news_to_markdown(now,new_news):
    yesterday = now - timedelta(days=1)
    year_month = now.strftime("%Y-%m")  # 年-月格式
    yesterday_year_month = yesterday.strftime("%Y-%m")
    day = now.strftime("%d")            # 日格式
    yesterday_day = yesterday.strftime("%d") 
    # 前一天的时间
    folder_path = f"news_archive/{year_month}"  # 文件夹路径
    yesterday_folder_path = f"news_archive/{yesterday_year_month}"
    # 如果文件夹不存在，则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    if not os.path.exists(yesterday_folder_path):
        os.makedirs(yesterday_folder_path)
    # 设置新闻文件路径
    month_news_filename = f"{folder_path}/00.md"
    today_news_filename = f"{folder_path}/{day}.md"
    yesterday_news_filename = f"{yesterday_folder_path}/{yesterday_day}.md"
    # 如果今日新闻文件不存在，创建文件并写入标题
    if not os.path.exists(today_news_filename):
        with open(today_news_filename, 'w') as f:
            f.write(f"# 今日新闻 - {now.strftime('%Y年%m月%d日')}\n")  
    # 如果昨日新闻文件不存在，创建文件并写入标题
    if not os.path.exists(yesterday_news_filename):
        with open(yesterday_news_filename, 'w') as f:
            f.write(f"# 今日新闻 - {yesterday.strftime('%Y年%m月%d日')}\n")       
    news_written_count = 0  # 设置计数器来跟踪写入的新闻条数
    with open(yesterday_news_filename, 'r') as f:
        yesterday_news = f.read()
    # 读取现有文件内容
    with open(month_news_filename, 'r+') as f:
        existing_month_news = f.read()
        for news in new_news:
            markdown_entry = f"- [{news['title']}]({news['link']})\n"
            # 如果新闻不存在于昨日新闻和本月新闻中，那么认定这是一条新的，添加到本月新闻和今日新闻中
            if markdown_entry not in yesterday_news and markdown_entry not in existing_month_news:
                f.write(markdown_entry)
                news_written_count += 1  # 每写入一条新闻，计数器加1
                # 同时也需要检查并可能添加到今日新闻文件
                with open(today_news_filename, 'a') as df:
                    df.write(markdown_entry)
    if news_written_count > 0:
        print(f"保存成功，本次更新了 {news_written_count} 条新闻。")
    else:
        print("保存失败，暂时没有新闻更新。")
                
if __name__ == '__main__':
    tz = ZoneInfo('Asia/Shanghai')
    now = datetime.now(tz)
    print("当前时间：", now.strftime("%Y-%m-%d %H:%M:%S %Z"))  # 打印当前的日期和时间以及时区信息
    # 调用函数爬取所有新闻榜单
    print("开始爬取所有新闻...")
    news = fetch_all_news()
    print("新闻爬取完成，共爬取到 {} 条新闻。".format(len(news)))
    # 保存新闻到Markdown文件
    print("开始保存新闻到Markdown文件...")
    save_news_to_markdown(now,news)



