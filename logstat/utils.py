#encoding=utf8
"""
author: zhengzhenzhen
"""

import yaml
import sys
import json
import os
from collections import OrderedDict
import inspect
import logging

PWD = os.path.split(os.path.realpath(__file__))[0] + '/'
sys.path.append(PWD + 'readers/')
sys.path.append(PWD + 'src/')





def get_class_name(module_name, metric_list):
    """
    通过 module_name找到该文件中包含的Class name， 这里只包含了一个类哈
    ('ArrayType', <class 'pyspark.sql.types.ArrayType'>)
    ('FloatType', <class 'pyspark.sql.types.FloatType'>)
    ('Metric', <class 'metric.Metric'>)
    ('PidStoreEventAll', <class 'pid_store_event_all.PidStoreEventAll'>)
    ('StringType', <class 'pyspark.sql.types.StringType'>)
    """
    module = __import__(module_name)
    class_name = '-'
    tmp_class_list = inspect.getmembers(module, inspect.isclass)
    ### 注意这个tmp_class_list中可能包含很多的类,只导入在conf里的即可
    for tmp in tmp_class_list:
        if tmp[0] in metric_list:
            class_name = tmp[1]    # 这里一个module_name 可能包含多个class，但是metric里面只有一个
    return class_name


class ExpConf(object):
    """
     获取实验的conf信息
    """
    def __init__(self, exp_conf, m_stream):
        """
        parser exp conf
        """
        #### simple version
        #exp_info = ordered_yaml_load(exp_conf)
        exp_info = yaml.load(open(exp_conf))
        self.common_metric_pars_dict = {}
        self.reader_list = []
        self.spark_reader_list = []   # 这里存了两个reader list
        
        # 基本配置 = exp conf
        self.conf = exp_info.get('conf', {})
        
        if 'conf' in exp_info:
            self.metric_dir_list = exp_info['conf']['metric_dir'].split(',')   # 可以支持多个文件夹目录

        logging.info('Your original exp conf: \n' + str(exp_info[m_stream]) + '\n')
        metric_list = []
        metric_pars_dict = []
        common_metric_pars_dict = {}
        for mm in exp_info[m_stream]:
            ## reader
            if isinstance(mm, dict):
                metric = list(mm.keys())[0]
                par_str = mm[metric]
                # yaml自带的格式
                if isinstance(par_str, dict):
                    metric_list.append(metric)
                    metric_pars_dict.append(par_str)
                else:  ##str 类型
                    par_str = par_str.replace(' ', '')   # save metric 对应的参数"k1:v1,k2:v2"
                    ## 1. reader
                    if metric == 'reader_spark':    ### spark的reader
                        self.spark_reader_list = par_str.split(',')   
                    elif metric == 'reader':        ### 本地 的reader
                        self.reader_list = par_str.split(',')
                    else:
                        par_dict = {}
                        for item in par_str.split(','):
                            k, v = item.split(':')
                            par_dict[k] = v  
                        if metric == 'Common':
                            self.common_metric_pars_dict = par_dict
                        else:  # 一般的metric
                            metric_pars_dict.append(par_dict)
                            metric_list.append(metric)
            else:  # 无参数
                metric_list.append(mm)
                metric_pars_dict.append({})
                
        self.metric_list = metric_list
        self.metric_pars_dict = metric_pars_dict
        

class StreamTask(object):
    """
        控制任务运行流程
    """
    def __init__(self, exp_conf):
        """
        """
        self.exp_conf = exp_conf
        metric_instance_name_list = self.import_metrics(exp_conf)
        self.metric_instance_name_list = metric_instance_name_list
        self.metric_list = exp_conf.metric_list  

    
    def import_metrics(self, exp_conf):
        """
        ### 主要是读取metrics
        """
        ### metrics/tools/ 一些小工具，默认直接读取
        metric_dir_list = exp_conf.metric_dir_list
        metric_list = exp_conf.metric_list
        
        file_list = []     # metric name list
        for metric_dir in metric_dir_list:
            file_name_list = os.listdir(metric_dir + '/')
            sys.path.append(metric_dir + '/')

            # 2 上传的metrics_dir下的文件list
            for file_name in file_name_list:
                if file_name.endswith('.py'):
                    file_list.append(file_name[:-3])

        metric_instance_name_list = []
        class_instance_dict = {}
        ## 扫描一遍所有的metric_dir, 只load exp.yaml中的
        for module_name in file_list:
            #try:   # 可能会存在非Metric的其他要导入的脚本
            #    module = __import__(module_name)
            #except:
            class_ = get_class_name(module_name, metric_list)
            if class_ == '-':
                continue

            class_name = class_.__name__
            if class_name in metric_list or module_name in metric_list:
                module = __import__(module_name)
                class_ = getattr(module, class_name)
                class_instance_dict[class_name] = class_
        ### 可能会有复用的metric，每次重新生成instance
        for class_name in metric_list:
            instance = class_instance_dict[class_name]()
            metric_instance_name_list.append([class_name, instance])

        return metric_instance_name_list


    def process(self, df_dict):
        """
        map / reduce process. 保证all_metric_dict 实时更新
        """
        out_dict = df_dict.copy()

        for i in range(len(self.metric_list)):
            metric = self.metric_list[i]
            metric_instance = self.metric_instance_name_list[i][1]
            logging.info('====In process... Metric = ' + metric)
            
            metric_pars = self.exp_conf.metric_pars_dict[i]
            if len(metric_pars) > 0:
                output = metric_instance.process(out_dict, metric_pars)  
            else:
                output = metric_instance.process(out_dict)   # 可能是多个key

            if output is not None:  # 可能没return
                out_dict.update(output)
        return out_dict
    
    
    ### todo 多任务并行
    def process_multitasks(self, df_dict, dag_task_list):
        """
        """
        return {}
