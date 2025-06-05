import requests
from datetime import datetime
import json
import time

# 导入配置文件
from config import appID, appSecret, openId, job_template_id



def get_access_token():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID.strip(), appSecret.strip())
    response = requests.get(url, verify=False).json()
    print(response)
    access_token = response.get('access_token')
    return access_token

def get_job_info():
    url = "https://www.ncss.cn/student/jobs/jobslist/ajax/"
    params = {
        "jobType": "03",
        "areaCode": "",
        "jobName": "GIS",
        "industrySectors": "",
        "memberLevel": "",
        "recruitType": "",
        "offset": 1,
        "limit": 10,
        "keyUnits": "",
        "degreeCode": "",
        "sourcesName": "",
        "sourcesType": "",
        "_": int(time.time() * 1000)
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("flag"):
                jobs = []
                for job in data["data"]["list"]:
                    job_name = job.get("jobName", "")
                    area_code_name = job.get("areaCodeName", "")
                    sources_name_ch = job.get("sourcesNameCh", "")
                    publish_timestamp = job.get("publishDate", None)
                    
                    if publish_timestamp:
                        publish_date = datetime.fromtimestamp(publish_timestamp / 1000).strftime('%Y-%m-%d')
                    else:
                        publish_date = "未知日期"
                    
                    jobs.append({
                        "job_name": job_name,
                        "area": area_code_name,
                        "company": sources_name_ch,
                        "publish_date": publish_date
                    })
                return jobs
        return None
    except Exception as e:
        print(f"获取招聘信息失败: {str(e)}")
        return None

def send_job_info(access_token, jobs):
    if not jobs:
        return
    
    # 只取前3条职位信息
    jobs = jobs[:3]
    
    # 构建消息数据
    data = {}
    for i, job in enumerate(jobs, 1):
        data.update({
            f"job{i}Name": {
                "value": job['job_name']
            },
            f"job{i}Area": {
                "value": job['area']
            },
            f"job{i}Company": {
                "value": job['company']
            },
            f"job{i}Date": {
                "value": job['publish_date']
            }
        })
    
    body = {
        "touser": openId.strip(),
        "template_id": job_template_id.strip(),
        "url": "https://www.ncss.cn/student/m/jobs/index.html?offset=1&limit=10&jobType=03&jobName=gis&categoryCode=&sourcesName=&ssgxName=&sourcesType=&monthPay=&recruitType=&property=&degreeCode=&keyUnits=&memberLevel=",
        "data": data
    }
    
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
    response = requests.post(url, json.dumps(body), verify=False).json()
    print("发送结果：", response)

def job_report():
    # 1. 获取access_token
    access_token = get_access_token()
    # 2. 获取招聘信息
    jobs = get_job_info()
    if jobs:
        print(f"获取到 {len(jobs)} 条招聘信息")
        # 3. 发送消息
        send_job_info(access_token, jobs)
    else:
        print("未获取到招聘信息")

if __name__ == '__main__':
    # 立即执行一次
    job_report()
    
    # 设置定时任务，每天早上9点执行
    # schedule.every().day.at("09:00").do(job_report)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)