
## 2021-07-10 特征添加历史3年的均值，历史5年的均值

logstat -e exp.yaml -m add_history_202107

增加英文数据的爬取时间，当前是2008-2020， 增加2004-2007的数据，这样即使用历史5年的数据，最终数据也还是09-17

英文paper爬取 crawl_wcs.py

## 2021-02 更新添加英文版数据

- 更新college_list 为按照控制变量来的118个
- 增加X: 深度、广度指标， Y改为合作占比统一量纲



(1) 数据准备
- 更新 PaperCLCWithEnglish
- cal_RTA bug fix

```
## 准备数据
ye -e exp.yaml -m merge_english_202102
```





(2)
- add `run_model/`


(3) 基础统计

- X的相关系数矩阵
- X，y的描述统计
- 




---
## old


1. patent_data 

专利数据分为两部分:

（1）合作数据-
之前有处理过的
/Users/zhengzhenzhen/zzz/zzz/项目tasks/yezi_paper/

* all_raw_data 原始excel数据
* step1_data  简单清洗成txt文本
* step2_clean_data   提取主要特征 


(2) 各自发表数据


2. 论文发表数据


抓取了知网 https://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCDB&crossDbcodes=CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD
专业检索目录下 `YE=$year and AF=$college and CLC=%中图分类号`
