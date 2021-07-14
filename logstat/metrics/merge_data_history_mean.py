#encoding=utf8
import os
import sys
import json
import numpy as np
import pandas as pd
import math
import time
from src.tools import cal_variation_coefficient, get_dict


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

            tmp_list.append(num / group_num)
        # 3 计算变异系数
        res = cal_variation_coefficient(tmp_list)
        out_dict[col] = res

    return out_dict



def trans_data(patent_data, window, year):
    """
    计算前window年的集中度的均值
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


def cal_wide_deep_history(patent_dict, year_patent_dict, col, last_year, window):
    """
    计算深度和广度
    """
    year_list = list(range(last_year - window+1, last_year + 1))

    info = {}
    for year in year_list:
        last_key = str(year) + '\t' + col
        if last_key in patent_dict:
            tmp_info = patent_dict[last_key]
            for key in tmp_info:
                if key not in info:
                    info[key] = 0
                info[key] += tmp_info[key]

    _list = list(info.values())
    _list = np.array(_list)
    wide = sum(_list > 0)
    ##
    _list = []
    for group in info:
        _list.append(info[group] / year_patent_dict[group])

    deep = sum(_list) / len(_list)   # 所有类的均值当做平均深度

    ## BHG的占比
    top_list = ['B', 'H', 'G']
    sum_top = 0
    for key in info:
        if key[0] in top_list:
            sum_top += info[key]
    sum_all = sum(info.values())
    if sum_all == 0:
        top_rate = 0
    else:
        top_rate = sum_top / sum_all

    return [wide, deep, top_rate]

def cal_distribution_similarity(patent_dict, paper_dict, tmp_col, last_year, window, IPC_CLC_mapping):
    """
    计算两个的匹配度
    """
    patent_info = {}
    paper_info = {}
    year_list = list(range(last_year - window+1, last_year + 1))
    for key in patent_dict:
        year, col = key.split('\t')
        if int(year) in year_list and col == tmp_col:
            for group in patent_dict[key]:
                if group not in patent_info:
                    patent_info[group] = 0
                patent_info[group] += patent_dict[key][group]
    
    for key2 in paper_dict:
        year, col = key2.split('\t')
        if int(year) in year_list and col == tmp_col:
            for group in paper_dict[key2]:
                if group not in paper_info:
                    paper_info[group] = 0
                paper_info[group] += paper_dict[key2][group]

    ########
    new_patent_info = {}
    for key in patent_info:
        new_key = IPC_CLC_mapping[key]
        new_patent_info[new_key] = patent_info[key]
    #
    sum_patent = sum(new_patent_info.values())
    sum_paper = sum(paper_info.values())

    key_list = [chr(letter) for letter in range(65, 91)]
    if sum_patent == 0:
        patent_list = len(key_list) * [0]
    else:
        patent_list = [new_patent_info.get(key, 0) / sum_patent for key in key_list]

    if sum_paper == 0:
        paper_list = len(key_list) * [0]
    else:
        paper_list = [paper_info.get(key, 0) / sum_paper for key in key_list]
    ## 计算余弦相似度
    tmp = [(patent_list[i] - paper_list[i])**2 for i in range(len(paper_list))]
    distance = math.sqrt(sum(tmp))

    return distance

def get_year_history_data(patent_dict, last_year, window):
    """
    计算每年不分col的汇总数据
    """
    year_list = list(range(last_year - window+1, last_year + 1))

    new_dict = {}
    col_list = []
    uniq_year = []
    for key in patent_dict:
        year, col = key.split('\t')
        if int(year) not in year_list:
            continue

        if col not in col_list:
            col_list.append(col)
        if year not in uniq_year:
            uniq_year.append(year)
       
        for group in patent_dict[key]:
            num = patent_dict[key][group]
            if group not in new_dict:
                new_dict[group] = 0
            new_dict[group] += num
    #
    year_num = len(uniq_year)
    for group in new_dict:
        new_dict[group] = new_dict[group]/ len(col_list) / year_num
    return new_dict


class MergeDataWithHistoryMean(object):

    def process(self, input, par_dict):
        """
        合并最终的所有Y和X
        yy_dict: {key: {'A': num, 'U': num}}
        patent_dict: {key: {IPC: num}}
        paper_dict: {key: {CLC: num}}
        control_dict: {key: [size, rnd]}
        """
        control_dict = input['control_dict']
        paper_dict = input['paper_dict']
        patent_dict = input['patent_dict']
        yy_dict = input['yy_dict']

        IPC_CLC_mapping = get_dict('english_data/IPC_CLC_mapping')
        out_dir = par_dict.get('out_dir', 'final_res.csv')
        ff = open(out_dir, 'w')

        wide_deep_col = ['wide', 'deep', 'top_rate']
        title_list = ['year', 'col', 'yt', 'yt_1', 'yt_A', 'yt_U', 'yt_fenmu', 'size', 'rnd', 'patent1', 'patent3', 'patent5', 'paper1', 'paper3', 'paper5'] + \
            ['patent_' + item + '1' for item in wide_deep_col] + \
                ['paper_' + item + '1' for item in wide_deep_col] + \
            ['patent_' + item + '3' for item in wide_deep_col] + \
                ['paper_' + item + '3' for item in wide_deep_col] + \
            ['patent_' + item + '5' for item in wide_deep_col] + \
                ['paper_' + item + '5' for item in wide_deep_col] + ['match_distance1', 'match_distance3', 'match_distance5']

        ff.write('\t'.join(title_list) + '\n')
        for key in control_dict:
            year, col = key.split('\t')
            if int(year) > 2017 or int(year) < 2008:
                continue
                
            last_year = int(year) - 1
            last_key = str(last_year) + '\t' + col
            #
            if last_key in yy_dict and last_key in control_dict and key in yy_dict \
                and last_key in paper_dict and last_key in patent_dict:
                num_A = yy_dict[key]['A']
                num_U = yy_dict[key]['U']
                Yt = num_A + num_U     # 该year+col分表的专利合作数


                yt_1 = yy_dict[last_key]['A'] + yy_dict[last_key]['U']
                #yt_1 = yy_dict[last_key]
                zz_control = control_dict[last_key]
                Yt_fenmu = sum(patent_dict[key].values())   # 该year+col分表的专利总数

                ## 计算深度和广度
                year_patent_dict3 = get_year_history_data(patent_dict, last_year, 3)
                year_paper_dict3 = get_year_history_data(paper_dict, last_year, 3) 
                year_patent_dict5 = get_year_history_data(patent_dict, last_year, 5)
                year_paper_dict5 = get_year_history_data(paper_dict, last_year, 5)

                patent_wide_deep1 = cal_wide_deep_history(patent_dict, year_patent_dict3, col, last_year, 1)
                paper_wide_deep1 = cal_wide_deep_history(paper_dict, year_paper_dict3, col, last_year, 1)
                patent_wide_deep3 = cal_wide_deep_history(patent_dict, year_patent_dict3, col, last_year, 3)
                paper_wide_deep3 = cal_wide_deep_history(paper_dict, year_paper_dict3, col, last_year, 3)
                patent_wide_deep5 = cal_wide_deep_history(patent_dict, year_patent_dict5, col, last_year, 5)
                paper_wide_deep5 = cal_wide_deep_history(paper_dict, year_paper_dict5, col, last_year, 5)

                ## 计算匹配度
                match_distance1 = cal_distribution_similarity(patent_dict, paper_dict, col, last_year, 1, IPC_CLC_mapping)
                match_distance3 = cal_distribution_similarity(patent_dict, paper_dict, col, last_year, 3, IPC_CLC_mapping)
                match_distance5 = cal_distribution_similarity(patent_dict, paper_dict, col, last_year, 5, IPC_CLC_mapping)

                ## 计算concentration
                patent_1_dict = trans_data(patent_dict, 1, int(last_year))
                patent_3_dict = trans_data(patent_dict, 3, int(last_year))
                patent_5_dict = trans_data(patent_dict, 5,  int(last_year))
                
                paper_1_dict = trans_data(paper_dict, 1, int(last_year))
                paper_3_dict = trans_data(paper_dict, 3, int(last_year))
                paper_5_dict = trans_data(paper_dict, 5, int(last_year))
                if col in patent_5_dict and col in paper_5_dict:
                    x_patent_1 = patent_1_dict[col]
                    x_patent_3 = patent_3_dict[col]
                    x_patent_5 = patent_5_dict[col]
                    x_paper_1 = paper_1_dict[col]
                    x_paper_3 = paper_3_dict[col]
                    x_paper_5 = paper_5_dict[col]

                    final_res = [year, col, Yt, yt_1, num_A, num_U, Yt_fenmu] + zz_control + [x_patent_1, x_patent_3, x_patent_5, x_paper_1, x_paper_3, x_paper_5] + \
                        patent_wide_deep1 + paper_wide_deep1 + patent_wide_deep3 + paper_wide_deep3 + patent_wide_deep5 + paper_wide_deep5 + [match_distance1, match_distance3, match_distance5]
                    #print(final_res)
                    ff.write('\t'.join(map(str, final_res)) + '\n')
        ff.close()


        
        return {'control_dict': control_dict}
   
    