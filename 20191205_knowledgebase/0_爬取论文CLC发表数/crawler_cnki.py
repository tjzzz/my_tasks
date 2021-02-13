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

def clean_CLC():
    group_list = []
    for line in open('CLC_data_raw'):
        items = line.strip().split(' ')
        if len(items) < 2:
            continue
        clc = items[1].replace('[', '').replace(']', '').replace('{', '').replace('}', '')
        clc = clc.replace(' ', '')
        group_list.append(clc)
        #print(clc)
    
    return group_list


def save_page(driver, out_id):
    soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
    ff = open('./htmls/' + out_id + '.html', 'w')
    ff.write(str(soup))
    ff.close()
    
    
## 读入学校list
def get_list(in_file):
    col_list = []
    for line in open(in_file):
        col = line.strip().split('\t')[0]
        col_list.append(col)
    return col_list
 

def parser_iframe_result(driver):
    """
    """
    soup = bs4.BeautifulSoup(driver.page_source, "html.parser")        # 获取页面内容
    tmp = soup.find_all(attrs={"class":"pagerTitleCell"})
    if len(tmp) == 0:
        return 0, 0
    zz = tmp[0]
    res_num = zz.get_text().replace('\xa0', '').replace('找到','').replace('条结果', '')
    return 1, res_num

    
if __name__ == "__main__":


    year = sys.argv[1]
    select_class = 'class1'
    
    CLC_list = get_list('CLC_' + select_class + '.txt')
    col_list = get_list('college_list.txt')
    out_dir = 'out_' + select_class
    os.system('mkdir -p ' + out_dir)
    ## v3
    driver = webdriver.Chrome('./chromedriver')
    url = 'https://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCDB&crossDbcodes=CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD'
    driver.get(url)    # 打开网页
    driver.find_element_by_xpath('//*[@id="1_3"]/a').click()   # 点击专业检索
    
    
    for col in col_list:
        if os.path.exists(out_dir + '/' + year + '_' + col + '.txt'):
            continue
        ff = open(out_dir + '/' + year + '_' + col + '.txt', 'w')
        for group in CLC_list:
            cmd = 'YE=' + year + ' and AF=' + col + " and CLC=%'" + group +"'"
            #cmd2 = cmd.encode('utf-8').decode("unicode_escape")

            wait = WebDriverWait(driver, 10) #等待的最大时间20s
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="expertvalue"]')))

            driver.find_element_by_xpath('//*[@id="expertvalue"]').clear()
            driver.find_element_by_xpath('//*[@id="expertvalue"]').send_keys(cmd)

            driver.find_element_by_id("btnSearch").click()    # 点击检索

            
            wait.until(EC.presence_of_element_located((By.ID, "iframeResult")))

            iframe = driver.find_element_by_id("iframeResult")
            driver.switch_to.frame(iframe)  # 获取检索条数
            #save_page(driver, 'test2')
            flag = 0
            inter = 10
            i = 0
            while flag == 0 and i < inter:
                flag, res_num = parser_iframe_result(driver)
                os.system('sleep 2')
                i += 1

            if i == inter:
                print(year, col, group)

            driver.switch_to.default_content()

            #delay = random.randint(1, 3)
            #os.system('sleep ' + str(delay))
            out = '\t'.join(map(str, [year, col, group, res_num]))
            ff.write(out + '\n')
        ff.close()
