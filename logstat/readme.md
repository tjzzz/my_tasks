##  logstat

基于df的logstat工具

支持一些指标开发,分析模块和一些挖掘功能


```
.
├── readers/               ## readers 解析日志
├── metrics/               ## 指标计算插件
├── conf/                  ## exp.yaml 不同实验配置文件
├── run.py                 ##  总run
├── utils.py

```


TOdo:

[x] 扩展配置文件的功能，能在配置文件运行一些简单的处理脚本（有时候一些很简单的处理不用再写个class)
比如一些通用的功能：filter，stat ===> MyCmd:'cmd1;cmd2'

[x] 对metric可以增加一个分stream的部分,即不是所有任务都是一次全跑,每次可以指定执行哪些metric. 当做不同的metric块

[x] 每个metric块下可能需要传入一些metric公用的参数。建立一个metric的父类，加上common_pars这个即可

[x] logstat 测试时候出问题了不是很好debug，在jupyter中可以较好的可视化。需要将logstat的配置能快速的生成对应的jupyter中的code。方便debug

[] 增加一个输出excel分析报表的模版，后续可以产生不同的分析报告



Update log

* 2019-12-3


* 2019.11.25
run.py增加argparse, 后续可以指定更多通用参数，不一定都在yaml文件里配置

* 更新下run入口，可以直接在jupyter中引用

```python
# e.g
from run import run
user_define_dict = {}
df_out = run('exp.yaml', 'stream_ana', user_define_dict)
```


* 2019.10.10  增加了不同的metric 块功能,可以一次测试指定的模块.因为调研的时候不可能一次性跑完所有分析流程
增加了公共参数选项
 
