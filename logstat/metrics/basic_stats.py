import sys
import os
from src.tools import get_list


def stats_missing():
    """
    统计英文发表数据中缺失的数据
    """
    college_list = get_list('college_list.txt')

    english_dict = {}
    english_data_dir = 'english_data/英文发表数据/'
    for year in ['2012', '2013', '2014', '2015', '2016', '2017', '2018']:
        data_dir = english_data_dir + year + '年各高校数据'
        for tmp_file in os.listdir(data_dir):
            if not tmp_file.startswith(year):
                continue
            tmp_year, col = tmp_file.replace('.txt', '').split('_')
            if year not in english_dict:
                english_dict[year] = []
            english_dict[year].append(col)
    #
    for year in english_dict:
        for col in college_list:
            if col not in english_dict[year]:
                print(str(year) + '\t' + col)
            

class BasicStats(object):


    def process(self, input):
        #
        stats_missing()

        ## in_file = 'final_res_with_english.csv'

        

