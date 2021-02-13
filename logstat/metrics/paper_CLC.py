#encoding=utf8
import os
import sys
import json
import numpy as np
import pandas as pd
import time


        
class PaperCLC(object):

    def process(self, input):
        """
        统计
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
        	key = str(int(year) - 1) + '\t' + col
        	if key not in paper_dict:
        		paper_dict[key] = {}
        	if clc not in paper_dict[key]:
        		paper_dict[key][clc] = 0
        	paper_dict[key][clc] += num

        return {'paper_dict': paper_dict}
    