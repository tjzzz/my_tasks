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

#PWD = os.path.dirname(os.path.abspath("__file__"))
PWD = os.path.split(os.path.realpath(__file__))[0] + '/'
sys.path.append(PWD + 'readers/')
sys.path.append(PWD + 'src/')



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
        exp_info = yaml.load(open(exp_conf), Loader=yaml.FullLoader)
        self.common_metric_pars_dict = {}
        self.reader_list = []
        self.spark_reader_list = []   # 这里存了两个list
        

        par_exp = exp_info.get('conf', {})
        self.conf = par_exp
        
        if 'conf' in exp_info:
            self.metric_dir_list = exp_info['conf']['metric_dir'].split(',')   # 可以支持多个文件夹目录

        print('Your exp conf: \n', exp_info[m_stream], '\n')
        metric_list = []
        metric_pars_dict = {}
        common_metric_pars_dict = {}
        for mm in exp_info[m_stream]:
            ## reader
            if isinstance(mm, dict):
                metric = list(mm.keys())[0]
                par_str = mm[metric]    # save metric 对应的参数"k1:v1,k2:v2"
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
                        metric_pars_dict[metric] = par_dict
                        metric_list.append(metric)
            else:
                metric_list.append(mm)
                
        self.metric_list = metric_list
        self.metric_pars_dict = metric_pars_dict
        


def get_class_name(module_name, metric_list):
    """
    通过 module_name找到该文件中包含的Class name， 这里只包含了一个类哈
    """
    # print('get_class_name', module_name )
    module = __import__(module_name)
    class_name = '-'
    tmp_class_list = inspect.getmembers(module, inspect.isclass)
    ### 注意这个tmp_class_list中可能包含很多的类,只导入在conf里的即可
    for tmp in tmp_class_list:
        if tmp[0] in metric_list:
            class_name = tmp[1]    # 这里一个module_name 可能包含多个class，但是metric里面只有一个
    return class_name




class StreamTask(object):
    """
    任务运行流程. 主要针对on_task_end类型的
    """
    def __init__(self, exp_conf):
        """
        """
        self.exp_conf = exp_conf
        metric_instance_name_dict = self.import_metrics(exp_conf)
        self.metric_instance_name_dict = metric_instance_name_dict
        self.metric_list = exp_conf.metric_list  

    
    def import_metrics(self, exp_conf):
        """
        ### 主要是读取metrics
        """
        ## 1 reader
        reader_info = yaml.load(open(PWD + '/readers/reader.yaml'), Loader=yaml.FullLoader)
        reader_instance_list = []
        for reader in exp_conf.reader_list:
            reader_file_name = reader_info['Readers'][reader]
            module = __import__(reader_file_name)
            class_ = getattr(module, reader)
            reader_instance = class_()
            reader_instance_list.append(reader_instance)
        #
        self.reader_instance_list = reader_instance_list
        
        
        ##
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

        metric_instance_name_dict = {}

        for tmp in metric_list:
            metric_instance_name_dict[tmp] = ''

        for module_name in file_list:
            class_ = get_class_name(module_name, exp_conf.metric_list)
            if class_ == '-':
                continue

            class_name = class_.__name__
            if class_name in metric_list or module_name in metric_list:

                module = __import__(module_name)
                class_ = getattr(module, class_name)
                instance = class_()
                metric_instance_name_dict[class_name] = instance


        return metric_instance_name_dict



    def process(self, df_dict):
        """
        map / reduce process. 保证all_metric_dict 实时更新
        """
        out_dict = df_dict.copy()
        for metric in self.metric_list:
            if metric in self.metric_instance_name_dict and self.metric_instance_name_dict[metric] != '':
                metric_instance = self.metric_instance_name_dict[metric]
                print('====In process... Metric = ', metric)
                if metric in self.exp_conf.metric_pars_dict:
                    metric_pars = self.exp_conf.metric_pars_dict[metric]
                    output = metric_instance.map(out_dict, metric_pars)  
                else:
                    output = metric_instance.map(out_dict)   # 可能是多个key
                #print('output', output)
                if output is not None:  # 可能没return
                    out_dict.update(output)
        return out_dict








