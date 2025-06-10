# 找工作微信推送工作流
基于24365大学生就业平台进行爬取的岗位数据，使用GitHub中免费的action部署工作流，通过微信测试号平台实现推动至微信显示。24365平台能够聚合主流招聘平台，而且爬取不需要验权等相关复杂操作，故采用此接口。目前实现的功能是每日定点更新岗位数据并跳转到岗位列表。


## 主要参数介绍
```py
params = {
        "jobType": "03",#缺省为全部岗位，01为全职，02兼职，03为实习
        "areaCode": "",#地区代码可以自行尝试了解查看
        "jobName": 开发,#这里可以使用定义的列表，也可以直接传参。在main.py定义有job_types列表可自行填入想要爬取的岗位
        
```
更多可以自己在F12查看
![image](https://github.com/user-attachments/assets/6d6801fb-ce80-4239-a585-5338d7390daa)
```yml
on:
  schedule:
    # 可以选择多个时间段，要注意北京时间 12:00 对应 UTC 04:00。实际亲测有半小时的延迟，需要准点请自行调整
    - cron: '0 4 * * *'
    - cron: '0 13 * * *'
  workflow_dispatch:  # 允许手动触发
```

## 配置
要在微信测试号平台获取下面几个KEY `appID, appSecret, openId, job_template_id`
登录即可有前两个
![屏幕截图 2025-06-09 222742](https://github.com/user-attachments/assets/2237c3e9-edb1-4fa1-943b-1d8c45824848)
扫码关注
![屏幕截图 2025-06-09 222830](https://github.com/user-attachments/assets/e2cce580-c61d-4c23-ad87-4d9edd2e17c1)
配置模板job_template_id
示例：
```
职位1：{{job1Name.DATA}} 地区：{{job1Area.DATA}} 公司：{{job1Company.DATA}} 日期：{{job1Date.DATA}} 职位2：{{job2Name.DATA}} 地区：{{job2Area.DATA}} 公司：{{job2Company.DATA}} 日期：{{job2Date.DATA}} 职位3：{{job3Name.DATA}} 地区：{{job3Area.DATA}} 公司：{{job3Company.DATA}} 日期：{{job3Date.DATA}}
```
![屏幕截图 2025-06-09 222905](https://github.com/user-attachments/assets/a6a4f49d-4990-469b-8346-8c6004fb3300)
最后在 GitHub 仓库中，进入 "Settings" -> "Secrets and variables" -> "Actions"，新建secrets填入从微信获取到的变量：
* APP_ID：微信小程序 AppID
* APP_SECRET：微信小程序 AppSecret
* OPEN_ID：接收消息的用户 OpenID
* JOB_TEMPLATE_ID：微信模板消息 ID
