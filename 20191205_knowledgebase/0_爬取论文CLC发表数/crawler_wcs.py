#encoding=utf8
import os
import sys
import bs4
import random
import urllib
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait       #WebDriverWait注意大小写
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


    
    
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
    year_list: 要跑的年份list  比如['2004', '2005']
    """
    for year in year_list:
        out_dir = '/Users/zhenzhenzheng/Desktop/tmp_data/' + year + '_' + ch_name + '.txt'
        if os.path.exists(out_dir):
            continue

        driver = webdriver.Chrome('./chromedriver')
    

        #url = 'http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&search_mode=GeneralSearch&SID=D2ZOTJvwnhxwTXK8Gvf&preferencesSaved='
        url = 'http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&search_mode=GeneralSearch&SID=F1Xfrsfak9dydUBdD4p&preferencesSaved='
        driver.get(url)    # 打开网页

        # driver.find_element_by_xpath('//*[@id="reset-span"]/span[2]').click()

        ## 学校
        driver.find_element_by_xpath('//*[@id="value(input1)"]').clear()
        driver.find_element_by_xpath('//*[@id="value(input1)"]').send_keys(col)   
        ## 机构扩展
        #driver.find_element_by_xpath('//*[@id="select2-select1-container"]')  

        ## 年份
        driver.find_element_by_xpath('//*[@id="value(input2)"]').clear()
        driver.find_element_by_xpath('//*[@id="value(input2)"]').send_keys(year)   
        
        ## 检索
        driver.find_element_by_xpath('//*[@id="searchCell2"]/span[1]/button').click()


        # js="document.getElementById('resetForm').style.display='inline-block'"
        # driver.execute_script(js)
        # driver.find_element_by_xpath('//*[@id="reset-span"]/span[2]/span')
        # driver.find_element_by_id('resetForm').click()
        # driver.find_element_by_xpath('//*[@id="addSearchRow1"]/a').click()

        try:
            driver.find_element_by_xpath('//*[@id="page"]/div[1]/div[26]/div[2]/div/div/div/div[2]/div[3]/div[4]/span/div[1]').click()  
            driver.find_element_by_xpath('//*[@id="save_what_all_bottom"]').click()  
            driver.find_element_by_xpath('//*[@id="save"]').click()  

            try_num  = 0
            max_try_num = 3
            if try_num < max_try_num:
                #print('try_num= ', try_num)
                time.sleep(3)
                if os.path.exists('/Users/zhenzhenzheng/Downloads/analyze.txt'):
                    os.system('mv /Users/zhenzhenzheng/Downloads/analyze.txt ' + out_dir)
                    try_num = 3
                else:
                    try_num += 1

            driver.quit()

            if try_num == max_try_num and (not os.path.exists(out_dir)):
                print('fail', year, ch_name, col)
            else:
                print('ok', year, ch_name, col)
        except:
            driver.quit()
            print('fail', year, ch_name, col)





if __name__ == "__main__":

    year_list = ['2007']   #['2004', '2005', '2006', '2007']
    ch_eng_name_dict = get_dict('../english_data/col_english_name.txt')

    task = 1   # 1: 正常任务 2: 跑失败的那几个再重新跑

    if task == 1:
        for ch_name in ch_eng_name_dict:
            col = ch_eng_name_dict[ch_name]

            if col == '#N/A':
                continue

            run(ch_name, col, year_list)
            

    if task == 2:  # 重跑fail的那几个
        for line in open('2004_2007_missing_col'):
            fail, year, ch_name = line.strip().split(' ')
            col = ch_eng_name_dict[ch_name]
            if col == '#N/A':
                continue
            #print('run', year, ch_name, col)
            run(ch_name, col, [year])

        