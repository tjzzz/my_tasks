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

    
if __name__ == "__main__":


    #year = '2012'
    #col = 'Beijing University of Technology'
    
    #ch_eng_name_dict = get_dict('../english_data/col_english_name.txt')

    #for ch_name in ch_eng_name_dict:
    #    col = ch_eng_name_dict[ch_name]
    for line in open('../english_data/2012_2018_missing_col'):
        year, ch_name, col = line.strip().split('\t')
        if year != '2018':
            continue

        if col == '#N/A':
            continue
        #for year in ['2008', '2009', '2010', '2011']:
        if 1:
            
            out_dir = '/Users/zhengzhenzhen/Desktop/tmp_data/' + year + '_' + ch_name + '.txt'
            if os.path.exists(out_dir):
                continue

            driver = webdriver.Chrome('./chromedriver')
        

            url = 'http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&search_mode=GeneralSearch&SID=D2ZOTJvwnhxwTXK8Gvf&preferencesSaved='
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
                    if os.path.exists('/Users/zhengzhenzhen/Downloads/analyze.txt'):
                        os.system('mv /Users/zhengzhenzhen/Downloads/analyze.txt ' + out_dir)
                        try_num = 3
                    else:
                        try_num += 1

                driver.quit()

                if try_num == max_try_num and (not os.path.exists(out_dir)):
                    print('fail', year, ch_name)
                else:
                    print('ok', year, ch_name)
            except:
                driver.quit()
                print('fail', year, ch_name)


                

                