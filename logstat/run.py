#encoding=utf8
import pandas as pd
import numpy as np
import yaml
import sys
import os
import json
## spark conf
from pyspark import SparkConf
from pyspark.sql import SparkSession, SQLContext
from datetime import datetime, timedelta


"""
PWD = os.path.dirname(os.path.abspath("__file__"))    ## 启动该任务在的位置
print(PWD)
print(__file__)            # 脚本的相对路径 xxx/run.py
print(os.path.split(os.path.realpath(__file__))[0])    ## 绝对路径
"""
## run.py 在的位置
#run_script_path = '/'.join(sys.argv[0].split('/')[:-1]) + '/'   # 相对路径
run_script_path = os.path.split(os.path.realpath(__file__))[0] + '/'
print('Logstat dir: ', run_script_path)
sys.path.append(run_script_path + 'readers/')
from utils import ExpConf
from utils import StreamTask
from readers_spark import ReadersSpark
import time
import string
import random
import argparse


def prepare_spark_confs(exp_conf, df_dict):
    '''
    准备spark相关的reader; 有spark相关的reader才配置spark
    '''
    conf = SparkConf()
    conf = conf.setMaster("local[*]")
    conf = conf.set("spark.executor.memory", "10g")
    conf = conf.set("spark.driver.memory", "10g")
    conf = conf.set("spark.excutor.maxResultSize", "10g")
    conf = conf.set("spark.driver.maxResultSize", "10g")
    #conf = conf.set("spark.sql.execution.arrow.enabled", "true")   # 性能优化
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    reader_instance = ReadersSpark(spark, df_dict)
    
    ## 打包 metric/*.py
    for metric_dir in exp_conf.metric_dir_list:
        suffix = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        my_tar = 'logstat_' + suffix  + '.tar.gz'
        cmd1 = 'mkdir -p logstat_tmp; cp ' + metric_dir + '/*.py logstat_tmp/ ; cp ' + run_script_path + '/src/*.py logstat_tmp/'
        print(cmd1)
        os.system(cmd1)
        
        cmd2 = 'cd logstat_tmp/ ; tar -czf ' + my_tar + ' *.py; mv ' + my_tar + ' ' + run_script_path
        #tar_cmd = 'cd ' + metric_dir  + '; tar -czf ' + my_tar + ' *.py; mv ' + my_tar + ' ' + run_script_path
        print(cmd2)
        os.system(cmd2)
        
        os.system('rm -rf logstat_tmp')
        spark.sparkContext.addPyFile(run_script_path + my_tar)
        
    return reader_instance, spark, my_tar


def run(exp_yaml_file, m_stream, user_input_dict):
    """
    run
    """
    exp_conf = ExpConf(exp_yaml_file, m_stream)
    
    df_dict = {}
    df_dict.update(exp_conf.conf)                       # conf里的一些公用参数
    df_dict.update(exp_conf.common_metric_pars_dict)    # stream增加一些公用的参数

    # 0 初始化
    task = StreamTask(exp_conf)

    ## reader-local
    for reader_instance in task.reader_instance_list:
        df_reader = reader_instance.fetch_record()
        df_dict.update(df_reader)
    ## reader-spark
    if len(exp_conf.spark_reader_list) > 0:

        spark_reader_instance, spark, my_tar = prepare_spark_confs(exp_conf, df_dict)
        df_dict.update({'spark': spark})     # 后续可以公用同一个spark
        for reader_name in exp_conf.spark_reader_list:
            df, df_name = eval('spark_reader_instance.' + reader_name + '()')
            df_dict[df_name] = df

    ## 2 metric
    df_out = {}
    fail_flag = 0
    df_out = task.process(df_dict)
    """
    try:
        df_out = task.process(df_dict)
    except Exception as err:
        fail_flag = 1
        print('Job Fail...... ', err)
        
    finally:  # 删除metric文件
        if len(exp_conf.spark_reader_list) > 0:
            print('delete logstat_xxx.tar.gz' + run_script_path)
            os.system('rm -rf ' + run_script_path + my_tar)
    
    if fail_flag:
        sys.exit('fail')
    """

    if 'spark' in df_out:
        df_out['spark'].stop()
    return df_out
        

if __name__ == '__main__':
    
    
    t0 = time.time()
    
    # exp_conf
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", help="指定实验exp的配置文件exp.yaml", required=True)
    parser.add_argument("-m", help="指定要运行的是哪个metric模块", required=True)
    parser.add_argument("-t", help="指定运行的日期，注意格式是2019-08-30", type=str)


    args = parser.parse_args()
    user_input_dict = vars(args)
    
    exp_yaml_file = user_input_dict['e']
    m_stream = user_input_dict['m']

    df_out = run(exp_yaml_file, m_stream, user_input_dict)
    
    print(time.time() - t0)
