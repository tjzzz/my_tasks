#encoding=utf8
import os
import sys
import json
import numpy as np
import pandas as pd
import time


        
class ControlVars(object):

    def process(self, input):
        """
        控制变量
        """
        data = pd.read_excel('data/控制变量整合.xlsx', sheet_name='整合')

        control_dict = {}
        for i in range(len(data)):
            case = data.iloc[i]
            year = case['年份']
            col  = case['大学名称']
            if '（' in col:
                col = col[:-4]
            key = str(year) + '\t' + col
            if key not in control_dict:
                control_dict[key] = [0, 0]
            control_dict[key][0] += case['size']
            control_dict[key][1] += case['rnd']
        return {'control_dict': control_dict}
   
    