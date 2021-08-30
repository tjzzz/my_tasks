#encoding=utf8
import os
import sys
import json
import numpy as np
import pandas as pd
import time


def get_list(in_file):
    """
    """
    query_list = []
    for line in open(in_file):
        qq = line.strip().split('\t')[0]
        if qq not in query_list:
            query_list.append(qq)
    return query_list
        
class ExtractCompanyName:

    def __init__(self):
        self.data_dir = "/Users/zhenzhenzheng/zzz/task_projects/DATA/专利大专院校数据19850101-20191031_申请人中至少一个是大专院校/"


    def process(self, input):
        """
        统计大学数据中，与138所大学合作的公司都有哪些
        """
        year = input['year']
        college_list = get_list('/Users/zhenzhenzheng/zzz/task_projects/DATA/college_list_138')

        file_list = os.listdir(self.data_dir)
        for tmp_file in file_list:
            if tmp_file.startswith(year):

                df = pd.read_excel(self.data_dir + tmp_file)
                tmp_list = df['申请人'].to_list()

                for item in tmp_list:
                    item_list = item.split(';')
                    if len(item_list) < 2:
                        continue
                    flag1 = 0
                    flag2 = 0
                    for col in item_list:
                        if col in college_list:
                            flag1 = 1
                            break
                    if flag1 == 1:  # 至少包含138中的大学
                        for col in item_list:
                            if col not in college_list and '大学' not in col and '学院' not in col:
                                print(col.replace(' ', ''))


if __name__ == "__main__":

    cube = ExtractCompanyName()
    conf = {
        'year': '2019'
        }
    cube.process(conf)
    