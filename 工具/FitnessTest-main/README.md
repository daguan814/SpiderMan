# FitnessTest - 中小学体质测试数据生成系统

## 项目简介
这是一个用于生成中小学体质测试数据的Python系统，可以根据输入的性别、年级和目标分数，自动生成符合评分标准的具体体测项目数据。

连接服务器命令：
ssh -i "C:\Users\Administrator\Documents\id_rsa_macos" -L 3306:192.168.100.109:3306 shuijing@shuijingnas.xin -p 12222

目前计划：
1. 解耦service
2. 输出只需要一层结构，不需要success，不需要msg
3. 优化性能，将数据存入内存中，从内存中查找，不用每次查询。
4. 根据权重，自动算分数，并且放入json中 标准：
http://www.csh.moe.edu.cn/wtzx/bz/20141226/2c909e854a84301a014a8440b4d2000f.html

项目流程：
填入年龄性别、字段 -> 启动代码、输入比例 -> 
自动生成每个人的预估成绩 -> 根据预估成绩和年龄性别生成体测数据 ->
将体测数据填入表格