import time
import random
import pandas as pd
import requests
import requests_html
import configparser
import speech_recognition as sr
import pyaudio
import wave
import urllib

from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pydub import AudioSegment

class UnCaptcha:
    def __init__(self):
        self.file_path = "data/"
        
    def download_mp3(self, url):
        urllib.request.urlretrieve(url, self.file_path + "audio.mp3")

    def convert_wav_to_mp3(self):
        sound = AudioSegment.from_mp3(self.file_path + "audio.mp3")
        sound.export(self.file_path + "captcha.wav", format="wav")

    def detect_content(self):
        r = sr.Recognizer()
        WAV = sr.AudioFile(self.file_path + 'captcha.wav')
        with WAV as source:
            audio = r.record(source)
        dict_result = r.recognize_google(audio, show_all=True)
        result = dict_result["alternative"][0]['transcript']
        return result

    def run_val(self, url):
        self.download_mp3(url)
        self.convert_wav_to_mp3()
        result = self.detect_content()
        return result


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
        self.uc = UnCaptcha()

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
        val_status = "??????????????????"
        if query_key != "nan":
            session = requests_html.HTMLSession()
            try:
                r = session.get(self.normal_url + query_key)
                result = r.html.xpath("/html/body/div[7]/div/div[7]/div[1]/div/div/div/div")[0].text.split(" ")[1]
            except:
                result = r.html.xpath('/html/body/div[7]/div/div[10]/div/div[2]/div[1]/div/div/p[1]')[0].text
                result = "???????????????????????????"
            try:
                r_title = session.get(self.allintitle_url + query_key)
                result_title = r_title.html.xpath("/html/body/div[7]/div/div[7]/div[1]/div/div/div/div")[0].text.split(" ")[1]
            except:
                result_title = r_title.html.xpath('/html/body/div[7]/div/div[10]/div/div[2]/div[1]/div/div/p[1]')[0].text
                result_title = "???????????????????????????"
            try:
                self.df[self.normal_result_column].iloc[row] = int(result.replace(",",""))
            except Exception:
                self.df[self.normal_result_column].iloc[row] = int(result)
            try:    
                self.df['Unnamed: 3'].iloc[row] = int(result_title.replace(",",""))
            except Exception:
                self.df['Unnamed: 3'].iloc[row] = int(result_title)

        else:
            result = "??????"
            result_title = "??????"
            self.df[self.normal_result_column].iloc[row] = result
            self.df['Unnamed: 3'].iloc[row] = result_title
        return result, result_title, val_status

    def captcha_press_val(self):
        xf = self.driver.find_element_by_xpath("/html/body/div[1]/form/div/div/div/iframe")
        self.driver.switch_to.frame(xf)
        driver_iframe = self.driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[1]/div/div/span/div[1]')
        driver_iframe.click()
    
    def captcha_press_speech(self):
        self.driver.switch_to.default_content()
        xf2 = self.driver.find_element_by_xpath('/html/body/div[2]/div[4]/iframe')
        self.driver.switch_to.frame(xf2)
        driver_if2 = self.driver.find_element_by_xpath("/html/body/div/div/div[3]/div[2]/div[1]/div[1]/div[2]/button")
        driver_if2.click()
    
    def captcha_result(self):
        status = "error"
        while status == "error":
            url = self.driver.find_element_by_xpath("/html/body/div/div/div[7]/a").get_attribute('href')
            try:
                result = self.uc.run_val(url)
                status = "seccess"
            except Exception:
                result = 1
                status = "error"
            capture_input = self.driver.find_element_by_xpath("/html/body/div/div/div[6]/input")
            capture_input.send_keys(result)
            self.driver.find_element_by_xpath("/html/body/div/div/div[8]/div[2]/div[1]/div[2]/button").click()
            time.sleep(0.2)     

    def error_webdriver(self, driver, url ,query_key):
        val_status = "??????????????????"
        try:
            driver.get(url + query_key)
            list_result = driver.find_element_by_xpath("/html/body/div[7]/div/div[7]/div[1]/div/div/div/div").text.split(" ")
            result = list_result[1]
            if result == "?????????":
                result = list_result[0]
        except:
            bool_value = 0
            while bool_value == 0:
                # print("xxxxx???????????????xxxxx")
                val_status = "???????????????"
                try:
                    time.sleep(0.1)
                    self.captcha_press_val()
                    time.sleep(0.1)
                    self.captcha_press_speech()
                    time.sleep(0.1)
                    self.captcha_result()
                except Exception:
                    pass

                # ???????????????????????????????????????????????????????????????????????????
                time.sleep(5)
                try:
                    # driver.get(url + query_key)
                    try:
                        result = driver.find_element_by_xpath("/html/body/div[7]/div/div[7]/div[1]/div/div/div/div").text.split(" ")[1]
                        bool_value = 1
                    except:
                        no_search = driver.find_element_by_xpath('/html/body/div[7]/div/div[10]/div/div[2]/div[1]/div/div/p[1]').text
                        if "???????????????????????????" in no_search:
                            result = 0
                            bool_value = 1
                except:
                    pass
        return result, val_status
    
    def selenium_connection(self, query_key, row):
        if query_key != "nan":
            result, val_status = self.error_webdriver(self.driver, self.normal_url, query_key)
            try:
                self.df[self.normal_result_column].iloc[row] = int(result.replace(",",""))
            except Exception:
                self.df[self.normal_result_column].iloc[row] = int(result)
            result_title, val_status = self.error_webdriver(self.driver, self.allintitle_url, query_key)
            try:
                self.df['Unnamed: 3'].iloc[row] = int(result_title.replace(",",""))
            except Exception:
                self.df['Unnamed: 3'].iloc[row] = int(result_title)
        else:
            result = "??????"
            result_title = "??????"
            self.df[self.normal_result_column].iloc[row] = result
            self.df['Unnamed: 3'].iloc[row] = result_title
        return result, result_title, val_status
        

    def run(self):
        r = 2
        data = self.df[self.query_column_name][2:]
        total = len(data)
        temp = 0
        for i in data:
            temp += 1
            # print("====?????????====>", i)
            try:
                ip_status = "????????????"
                result, result_title, val_status = self.first_request_connection(i, r)
            except:
                ip_status = "????????????"
                result, result_title, val_status = self.selenium_connection(i, r)
            r += 1

            print('\r' + '[Progress]:[%s%s]%.2f%%; ????????????:%.2f???|?????????:%s |??????:%s|allintitle:%s???IP??????:%s - ????????????:%s???' % (
                '???' * int(temp * 20 / total),
                ' ' * (20 - int(temp * 20 / total)),
                float(temp / total * 100),
                time.time() - t1,
                i,
                result,
                result_title,
                ip_status,
                val_status),
                end=''
            )

        self.df.to_excel("data/output.xlsx")
        

if __name__ == '__main__':
    print("begin")
    df = pd.read_excel("data/input.xlsx", sheet_name="SEO???????????????")
    df.columns
    uc = UnCaptcha()
    config = configparser.ConfigParser()
    config.read('conf/env.cfg', encoding = 'utf8')
    file_path = config['File']['file_path']
    sheet_name = config['File']['sheet_name']
    # query_column_name = config['File']['query_column_name']
    # normal_result_column = config['File']['normal_result_column']
    query_column_name = df.columns[1]
    normal_result_column = df.columns[2]
    cq = CrawlerQuery(file_path, sheet_name, query_column_name, normal_result_column)
    t1 = time.time()
    cq.run()
    print("????????????", round(time.time() -t1,2), "???" )
    print("?????????????????????data??????????????????output.xlsx??????")

