#encoding=utf8
import os
import sys
import json
import numpy as np
import pandas as pd
import time

sys.path.append('src/')
from tools import get_list


		
class PatentIPC(object):

	def process(self, input):
		"""
		统计专利的合作数据：
		year + univ IPC
		"""
		college_list = input['college_list']

		if not os.path.exists('data.patent_IPC'):
			os.system('cat data/data_patent_col/* > data.patent_IPC')

		patent_dict = {}
		for line in open('data.patent_IPC'):
			items = line.strip().split('\t')
			year = items[0]
			if year == '申请':
				continue
			apply_year = year[:4]
			apply_person = items[1]
			IPC = items[2][:3]   # 大类A01 
			if IPC == '-':
				continue

			hit_college = []    # 可能多个
			for college in college_list:
				if college in apply_person:
					hit_college.append(college)
			#
			for college in hit_college:
				key = apply_year + '\t' + college
				if key not in patent_dict:
					patent_dict[key] = {}
				if IPC not in patent_dict[key]:
					patent_dict[key][IPC] = 0
				patent_dict[key][IPC] += 1

		return {'patent_dict': patent_dict}
	