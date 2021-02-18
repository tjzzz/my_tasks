import sys
import numpy as np
import datetime


def get_list(in_file):
	"""
	"""
	query_list = []
	for line in open(in_file):
		qq = line.strip().split('\t')[0]
		if qq not in query_list:
			query_list.append(qq)
	return query_list

def get_dict(in_file):
	#
	query_dict = {}
	for line in open(in_file):
		items = line.strip().split('\t')
		k, v = items[0], items[1]
		query_dict[k] = v
	return query_dict
	
def cal_variation_coefficient(_list):
    """
    计算变异系数
    """
    avg = np.mean(_list)
    var = np.std(_list)
    
    return var / avg



def get_days(day0, day1, delta=1):
    """
    get multi days
    """
    day_list = []
    if '-' in day0:
        templ = '%Y-%m-%d'
    else:
        templ = '%Y%m%d'
    delta = datetime.timedelta(days=delta)  # 默认一天
    d1 = datetime.datetime.strptime(day0, templ).date()
    d2 = datetime.datetime.strptime(day1,templ).date()
    tmp = d1
    while tmp <= d2:
        day = tmp.strftime(templ)
        day_list.append(day)
        tmp += delta
    return day_list

