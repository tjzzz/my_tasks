#encoding=utf8
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait       #WebDriverWait注意大小写
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import math
import time

    
    
## 读入学校list
def get_list(in_file):
    col_list = []
    for line in open(in_file):
        col = line.strip().split('\t')[0]
        col_list.append(col)
    return col_list
 

class MyDriver(object):

    def __init__(self, url):
        self.driver = webdriver.Chrome('./chromedriver')
        self.driver.get(url)
    
    def cmd(self, xpath_cmd, act, act_attr=''):

        if act == 'clear':
            self.driver.find_element_by_xpath(xpath_cmd).clear()
        if act == 'send_keys':
            self.driver.find_element_by_xpath(xpath_cmd).send_keys(act_attr)
        if act == 'click':
            self.driver.find_element_by_xpath(xpath_cmd).send_keys(act_attr)


def get_dict(in_file):
	#
	query_dict = {}
	for line in open(in_file):
		items = line.strip().split('\t')
		k, v = items[0], items[1]
		k = k.replace(' ', '')
		query_dict[k] = v
	return query_dict

    

def run(ch_name, col, year_list):
    """
    ch_name: 学校的中文名
    col: 学校的英文名
    year_list: 要跑的年份list, 抓取摘要的直接一次性查询多年的，下载的时候批量下载就好(下载结果里有年份信息)
                ['2002-2012']
    """
    save_dir = '/Users/zhenzhenzheng/Desktop/wos_abstract/' + ch_name
    os.system('mkdir -p ' + save_dir)
    
    ## 1. 打开检索
    #capa = DesiredCapabilities.CHROME
    #capa["pageLoadStrategy"] = "none" #懒加载模式，不等待页面加载完毕

  #driver = webdriver.Chrome('../chromedriver_092_4515', desired_capabilities=capa)
    driver = webdriver.Chrome('../chromedriver_092_4515')
    url = 'http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&search_mode=GeneralSearch&SID=E2k366UzlPWpSC7G3X9&preferencesSaved='

    driver.get(url)
    #WebDriverWait(driver, 10).until(lambda x:x.find_element_by_xpath('//*[@id="searchCell2"]/span[1]/button'))  # 有检索按钮就可以停止
    #driver.execute_script("window.stop();") #停止当前页面加载，防止input框输入错误


    for year in year_list:
        # driver.find_element_by_xpath('//*[@id="reset-span"]/span[2]').click()

        ## 学校
        driver.find_element_by_xpath('//*[@id="value(input1)"]').clear()
        driver.find_element_by_xpath('//*[@id="value(input1)"]').send_keys(col)   
        ## 机构扩展
        #driver.find_element_by_xpath('//*[@id="select2-select1-container"]')  

        # 年份
        driver.find_element_by_xpath('//*[@id="value(input2)"]').clear()
        driver.find_element_by_xpath('//*[@id="value(input2)"]').send_keys(year)   
        
        ## 检索
        driver.find_element_by_xpath('//*[@id="searchCell2"]/span[1]/button').click()
        #WebDriverWait(driver, 10).until(lambda x:x.find_element_by_xpath('//*[@id="exportTypeName"]'))  # 总数
        #driver.execute_script("window.stop();") 


        # js="document.getElementById('resetForm').style.display='inline-block'"
        # driver.execute_script(js)
        # driver.find_element_by_xpath('//*[@id="reset-span"]/span[2]/span')
        # driver.find_element_by_id('resetForm').click()
        # driver.find_element_by_xpath('//*[@id="addSearchRow1"]/a').click()
        
        ## 获取总页数
        total_num = driver.find_element_by_xpath('//*[@id="pageCount.top"]').text
        #WebDriverWait(driver, 20).until(lambda x:x.find_element_by_xpath('//*[@id="exportTypeName"]'))  # 总数
        #driver.execute_script("window.stop();") 

        total_num = int(total_num)
        
        page_num = math.ceil(total_num / 10)

        print(col, total_num, page_num)
        
        
        
        for i in range(page_num):
            page = 10 * i + 1
            print(col, page)
            ## 指定page
            if page > 1:
                mm = '//*[@id="summary_navigation"]/nav/table/tbody/tr/td[2]/input'
                driver.find_element_by_xpath(mm).clear()
                time.sleep(1)
                #try:
                driver.find_element_by_xpath(mm).send_keys(str(page) + Keys.ENTER)
                #WebDriverWait(driver, 20).until(lambda x:x.find_element_by_xpath('//*[@id="exportTypeName"]'))  # 总数
                #driver.execute_script("window.stop();") 

                #except:
                #    driver.execute_script("window.stop()")
            
            ## 准备下载
            # 下载按钮， 1-500条，下载
            
            ## 导出至excel， 记录1-500， 记录内容选择全部
            mm_list = ['//*[@id="exportTypeName"]', 
                    #    '//*[@id="saveToMenu"]/li[3]/a',
                       '//*[@id="numberOfRecordsRange"]',
                       '//*[@id="exportButton"]']
            

            
            for i in range(len(mm_list)):
                mm = mm_list[i]
                print(mm)
                #try:
                driver.find_element_by_xpath(mm).click() 
                #except:
                #    driver.execute_script("window.stop()")
            
            ## 文件保存
            
    ## 一个学校的批量跑完后移动文件
    out_dir = '/Users/zhenzhenzheng/Downloads/'
    os.system('mv ' + out_dir + 'savedrecs* ' + save_dir + '/')



if __name__ == "__main__":

    year_list = ['2008-2020']   #['2004', '2005', '2006', '2007']
    ch_eng_name_dict = get_dict('../20191205_knowledgebase/english_data/col_english_name.txt')

    task = 1   # 1: 正常任务 2: 跑失败的那几个再重新跑

    for ch_name in ch_eng_name_dict:
        col = ch_eng_name_dict[ch_name]

        if col == '#N/A':
            continue
        
        try:
            run(ch_name, col, year_list)
        except:
            continue

        