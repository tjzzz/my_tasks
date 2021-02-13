#encoding=utf8
import yaml
import sys
import os
import json
import importlib
import math


from datetime import datetime, timedelta
import logging
logging.basicConfig(level=logging.INFO)   # 默认的Metric用的INFO, 各自metric中可以定义debug显示
import traceback


"""
PWD = os.path.dirname(os.path.abspath("__file__"))    ## 启动该任务在的位置
print(__file__)            # 脚本的相对路径 xxx/run.py
print(os.path.split(os.path.realpath(__file__))[0])    ## 绝对路径
"""
## run.py 在的位置
#run_script_path = '/'.join(sys.argv[0].split('/')[:-1]) + '/'   # 相对路径
run_script_path = os.path.split(os.path.realpath(__file__))[0] + '/'
PWD = os.path.dirname(os.path.abspath("__file__"))    ## 启动该任务在的位置
logging.info('Logstat dir: ' +  run_script_path)
from utils import ExpConf
from utils import StreamTask

import time
import string
import random
import argparse


def prepare_spark_confs(exp_conf):
    '''
    准备spark相关的reader; 有spark相关的reader才配置spark
    '''
    from conf.spark_conf import import_spark
    spark = import_spark()
    
    ## 打包
    suffix = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    my_tar = 'logstat_' + suffix  + '.tar.gz'
    os.system('mkdir -p logstat_tmp')
    for metric_dir in exp_conf.metric_dir_list:
        # upload 主要文件 metric_dir, src, readers
        cmd1 = 'cp ' + metric_dir + '/*.py logstat_tmp/'
        os.system(cmd1)
        
    cmd1 = 'cp ' + run_script_path + '/src/*.py logstat_tmp/ ; cp ' + run_script_path + '/readers/*.py logstat_tmp/'
    logging.info(cmd1)
    os.system(cmd1)
    
    cmd2 = 'cd logstat_tmp/ ; tar -czf ' + my_tar + ' *.py; mv -f ' + my_tar + ' ' + run_script_path
    logging.info(cmd2)
    os.system(cmd2)
    
    os.system('rm -rf logstat_tmp')
    spark.sparkContext.addPyFile(run_script_path + my_tar)
        
    return spark, my_tar


def run_task(df_dict, exp_conf, task):
    logging.info('start to run ....... day=' + df_dict.get('run_day', '-'))
    ## logging.info('User final exp conf is ' +  str(df_dict))

    if len(exp_conf.spark_reader_list) > 0 and 'fetch_spark' not in exp_conf.spark_reader_list:
        spark = df_dict['spark']
        print('run task:  ', spark, exp_conf.spark_reader_list)
        spark_data_df, spark_df_name_list = get_all_readers(spark, df_dict, exp_conf.spark_reader_list)
        df_dict.update(spark_data_df)
        df_dict.update({'spark_df_name_list': spark_df_name_list})

    logging.info('User final exp conf is ' +  str(df_dict))

    ## 2 metric
    df_out = {}
    fail_flag = 0
    
    try:
        df_out = task.process(df_dict)
    except Exception as err:
        fail_flag = 1
        print('Job Fail...... ', err)
        traceback.print_exc()      # 定位出错的地方
            
    del df_dict

    if 'spark' in df_out:
        df_out['spark'].stop()

    return df_out, fail_flag


def run(exp_yaml_file, m_stream, user_input_dict):
    """
    input:
        exp_yaml_file: the conf file
        m_stream: the task stream to run 
        user_input_dict: user define other parameters
    """

    ## 1. exp 配置信息更新
    df_dict = {}
    exp_conf = ExpConf(exp_yaml_file, m_stream)
    df_dict.update(exp_conf.conf)                       # conf里的一些公用参数
    df_dict.update(exp_conf.common_metric_pars_dict)    # stream增加一些公用的参数
    df_dict['LOGSTAT_DIR'] = run_script_path    # 加入当前logstat的根目录

    ## 从外面直接调用run传入user_input_dict的
    df_dict.update(user_input_dict)
    # 2.check spark 日志是否ready


    # 3 初始化
    task = StreamTask(exp_conf)
    if len(exp_conf.spark_reader_list) > 0:
        spark, my_tar = prepare_spark_confs(exp_conf)
        df_dict.update({'spark': spark})        # 后续可以公用同一个spark

    ## 4. run 
    df_out, fail_flag = run_task(df_dict, exp_conf, task)


    # 删除metric tar包
    if len(exp_conf.spark_reader_list) > 0:
        print('delete ' + my_tar + ' ' + run_script_path)
        os.system('rm -rf ' + run_script_path + my_tar)

        
    return df_out

        
def parse_args():
    """
    解析传入的参数，对于不同的项目传入的参数可能不同,若没指定可以在exp.yaml中进行配置，或者使用-set 通用模式
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", help="指定实验exp的配置文件exp.yaml,可参照exp/exp.yaml", required=True)
    parser.add_argument("-m", help="指定要运行的是哪个metric模块", required=True)
    
    parser.add_argument("-d", help="指定运行的日期，格式是2019-08-30或者20190830", type=str)
    parser.add_argument("-brand", help="brand", type=str)
    parser.add_argument("-city", help="city", type=str)
    parser.add_argument("-site", help="site", type=str)
    parser.add_argument("-set", help="用户在run的时候指定的其他参数-set day:xx,job_name:xx,brand:xx,city:xx,")
    args = parser.parse_args()

    user_input_dict = {}
    tmp_info = vars(args)
    for key in tmp_info:
        if tmp_info[key] is not None:
            if key == 'set':
                kv_list = tmp_info['set'].split(',')
                for kv in kv_list:
                    k, v = kv.split(':')
                    user_input_dict[k] = v
            else:
                user_input_dict[key] = tmp_info[key]

    
    return user_input_dict


if __name__ == '__main__':
    
    t0 = time.time()
    user_input_dict = parse_args()      # exp_conf

    exp_yaml_file = user_input_dict['e']
    m_stream = user_input_dict['m']
    df_out = run(exp_yaml_file, m_stream, user_input_dict)
    
    logging.info('run time ' + str(time.time() - t0))
