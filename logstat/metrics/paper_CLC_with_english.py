#encoding=utf8
import os
import sys
import json
import numpy as np
import pandas as pd
import time


def get_english_num():
	"""
	读取英文的发表数
	"""
	from src.tools import get_dict
	mapping_dict = get_dict('english_data/english_CLC_mapping')

	english_dict = {}
	english_data_dir = 'english_data/英文发表数据/'
	year_list = list(range(2004, 2021))
	year_list = [str(year) for year in year_list]
	for year in year_list:
		data_dir = english_data_dir + year + '年各高校数据'
		for tmp_file in os.listdir(data_dir):
			if not tmp_file.startswith(year):
				continue
			tmp_year, col = tmp_file.replace('.txt', '').split('_')
			
			for line in open(data_dir + '/' + tmp_file):
				if '记录' in line or 'records' in line:
					continue
				items = line.strip().split('\t')
				# print(items)
				eng_group = items[0]
				count = int(items[1])

				#####
				if eng_group not in mapping_dict:
					print(tmp_year, col, eng_group)
					continue
				ch_group = mapping_dict[eng_group]
				key = str(int(year) - 2) + '\t' + col
				if key not in english_dict:
					english_dict[key] = {}
				if ch_group not in english_dict[key]:
					english_dict[key][ch_group] = 0
				english_dict[key][ch_group] += count
	return english_dict



		
class PaperCLCWithEnglish(object):

	def process(self, input):
		"""
		2021-02-13 在原有论文的基础上添加英文的发表数
		"""
		if not os.path.exists('data.paper'):
			os.system('cat out_class1/* > data.paper')

		paper_dict =  {}
		for line in open('data.paper'):
			items = line.strip().split('\t')
			year, col, clc = items[:3]
			if len(items) == 3:
				num = 0
			else:
				num = int(items[3].replace(',', ''))
			key = str(int(year) - 2) + '\t' + col    # 论文发表日实际申请日按照2年前算
			if key not in paper_dict:
				paper_dict[key] = {}
			if clc not in paper_dict[key]:
				paper_dict[key][clc] = 0
			paper_dict[key][clc] += num
		### 添加english
		print('add english data')
		english_dict = get_english_num()
		for key in paper_dict:
			for clc in paper_dict[key]:
				paper_dict[key][clc] += english_dict.get(key, {}).get(clc, 0)

		return {'paper_dict': paper_dict}
	