import time
import random
import pandas as pd
import requests
import requests_html
import configparser

from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class CrawlerQuery:
    def __init__(self, file_path, sheet_name, query_column_name, normal_result_column):
        self.normal_url = "https://www.google.com/search?q="
        self.allintitle_url = "https://www.google.com/search?q=allintitle%3A+" 
        self.file_name = file_path
        self.sheet_name = sheet_name
        self.query_column_name = query_column_name
        self.normal_result_column = normal_result_column
        self.df = self.read_file()
        self.driver = self.init_driver()

    def read_file(self):
        df = pd.read_excel(self.file_name,sheet_name=self.sheet_name)
        df = df.fillna("nan")
        return df

    def init_driver(self):
        chrome_options = webdriver.ChromeOptions()
        ua = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        chrome_options.add_argument("user-agent={}".format(ua))
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)
        return driver

    def first_request_connection(self, query_key, row):
        if query_key != "nan":
            session = requests_html.HTMLSession()
            try:
                r = session.get(self.normal_url + query_key)
                result = r.html.xpath("/html/body/div[7]/div/div[7]/div[1]/div/div/div/div")[0].text.split(" ")[1]
            except:
                result = r.html.xpath('/html/body/div[7]/div/div[10]/div/div[2]/div[1]/div/div/p[1]')[0].text
                result = "找不到符合搜尋字詞"
            try:
                r_title = session.get(self.allintitle_url + query_key)
                result_title = r_title.html.xpath("/html/body/div[7]/div/div[7]/div[1]/div/div/div/div")[0].text.split(" ")[1]
            except:
                result_title = r_title.html.xpath('/html/body/div[7]/div/div[10]/div/div[2]/div[1]/div/div/p[1]')[0].text
                result_title = "找不到符合搜尋字詞"
    
            self.df[self.normal_result_column].iloc[row] = result
            self.df['Unnamed: 3'].iloc[row] = result_title

        else:
            self.df[self.normal_result_column].iloc[row] = "空值"
            self.df['Unnamed: 3'].iloc[row] = "空值"

    def error_webdriver(self, driver, url ,query_key):
        try:
            driver.get(url + query_key)
            result = driver.find_element_by_xpath("/html/body/div[7]/div/div[7]/div[1]/div/div/div/div").text.split(" ")[1]
        except:
            bool_value = 0
            while bool_value == 0:
                print("xxxxx請完成驗證xxxxx")
                # 如果跳出驗證，需手動驗證，這時需要挑出畫面，並等待
                time.sleep(5)
                try:
                    # driver.get(url + query_key)
                    try:
                        result = driver.find_element_by_xpath("/html/body/div[7]/div/div[7]/div[1]/div/div/div/div").text.split(" ")[1]
                        bool_value = 1
                    except:
                        no_search = driver.find_element_by_xpath('/html/body/div[7]/div/div[10]/div/div[2]/div[1]/div/div/p[1]').text
                        if "找不到符合搜尋字詞" in no_search:
                            result = "找不到符合搜尋字詞"
                            bool_value = 1
                except:
                    pass
        return result
    
    def selenium_connection(self, query_key, row):
        if query_key != "nan":

            result = self.error_webdriver(self.driver, self.normal_url, query_key)
            self.df[self.normal_result_column].iloc[row] = result
            result_title = self.error_webdriver(self.driver, self.allintitle_url, query_key)
            self.df['Unnamed: 3'].iloc[row] = result_title
        else:
            self.df[self.normal_result_column].iloc[row] = "空值"
            self.df['Unnamed: 3'].iloc[row] = "空值"

    def run(self):
        r = 2
        for i in tqdm(self.df[self.query_column_name][2:]):
            print("====關鍵字====>", i)
            try:
                print("IP尚未被鎖")
                self.first_request_connection(i, r)
            except:
                print("IP開始備鎖")
                self.selenium_connection(i, r)
        r+=1
        self.df.to_excel("data/output.xlsx")
        

if __name__ == '__main__':
    print("begin")
    config = configparser.ConfigParser()
    config.read('conf/env.cfg', encoding = 'utf8')
    file_path = config['File']['file_path']
    sheet_name = config['File']['sheet_name']
    query_column_name = config['File']['query_column_name']
    normal_result_column = config['File']['normal_result_column']

    cq = CrawlerQuery(file_path, sheet_name, query_column_name, normal_result_column)
    t1 = time.time()
    cq.run()
    print("總計時間", round(time.time() -t1,2), "秒" )
    print("執行完畢，請到data資料夾中打開output.xlsx文件")

