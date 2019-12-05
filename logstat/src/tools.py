import sys
import numpy as np


def get_list(in_file):
	"""
	"""
	query_list = []
	for line in open(in_file):
		qq = line.strip().split('\t')[0]
		if qq not in query_list:
			query_list.append(qq)
	return query_list

def cal_variation_coefficient(_list):
    """
    计算变异系数
    """
    avg = np.mean(_list)
    var = np.std(_list)
    
    return var / avg


