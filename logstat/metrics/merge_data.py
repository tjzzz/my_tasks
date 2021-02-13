#encoding=utf8
import os
import sys
import json
import numpy as np
import pandas as pd
import time
sys.path.append('src/')
from tools import cal_variation_coefficient

def cal_RTA(col_group_dict):
    """
    """
    # 1 先计算group的汇总
    group_dict = {}
    for a in col_group_dict:
        for b in col_group_dict[a]:
            num = col_group_dict[a][b]
            if b not in group_dict:
                group_dict[b] = 0
            group_dict[b] += num
    # 2 
    out_dict = {} # 每个学校一个list
    for col in col_group_dict:
        tmp_list = []
        for group in col_group_dict[col]:
            num = col_group_dict[col][group]
            group_num = group_dict[group]

            tmp_list.append(num * group_num)
        # 3 计算变异系数
        res = cal_variation_coefficient(tmp_list)
        out_dict[col] = res

    return out_dict



def trans_data(patent_data, window, year):
    """
    转换下数据格式
    """
    year_list = list(range(year - window+1, year + 1))

    year_dict = {}
    for key in patent_data:
        year, col = key.split('\t')
        group_dict = patent_data[key]
        if int(year) in year_list:
            if col not in year_dict:
                year_dict[col] = {}
            for group in group_dict:
                num = group_dict[group]
                if group not in year_dict[col]:
                    year_dict[col][group] = 0
                year_dict[col][group] += num
    #
    rta_out = cal_RTA(year_dict)
    return rta_out



class MergeData(object):

    def process(self, input):
        """
        控制变量
        """
        control_dict = input['control_dict']
        paper_dict = input['paper_dict']
        patent_dict = input['patent_dict']
        yy_dict = input['yy_dict']

        ff = open('final_res.csv', 'w')

        for key in control_dict:
            year, col = key.split('\t')
            if int(year) > 2017 or int(year) < 2012:
                continue
                
            last_year = int(year) - 1
            last_key = str(last_year) + '\t' + col
            #
            if last_key in yy_dict and last_key in control_dict and key in yy_dict:
                Yt = yy_dict[key]
                yt_1 = yy_dict[last_key]
                zz_control = control_dict[last_key]

                ## 计算concentration
                patent_3_dict = trans_data(patent_dict, 3, int(last_year))
                patent_5_dict = trans_data(patent_dict, 5, int(last_year))
                
                paper_3_dict = trans_data(paper_dict, 3, int(last_year))
                paper_5_dict = trans_data(paper_dict, 5, int(last_year))
                if col in patent_5_dict and col in paper_5_dict:
                    x_patent_3 = patent_3_dict[col]
                    x_patent_5 = patent_5_dict[col]
                    x_paper_3 = paper_3_dict[col]
                    x_paper_5 = paper_5_dict[col]

                    final_res = [year, col, Yt, yt_1 ] + zz_control + [x_patent_3, x_patent_5, x_paper_3, x_paper_5]
                    #print(final_res)
                    ff.write('\t'.join(map(str, final_res)) + '\n')
        ff.close()


        
        return {'control_dict': control_dict}
   
    