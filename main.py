import requests
from datetime import datetime
import json
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 导入配置文件
from config import appID, appSecret, openId, job_template_id

# 缓存文件路径
CACHE_FILE = "job_cache.json"

# 配置请求会话
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# 设置请求超时时间（秒）
TIMEOUT = 5

def load_cache():
    """加载缓存数据"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache_data):
    """保存缓存数据"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

def has_new_jobs(job_type, current_jobs):
    """检查是否有新的职位信息"""
    cache = load_cache()
    cached_jobs = cache.get(job_type, [])
    
    if not cached_jobs:
        return True
    
    # 获取当前职位信息的唯一标识（职位名称+公司+地区）
    current_job_ids = {f"{job['job_name']}_{job['company']}_{job['area']}" for job in current_jobs}
    cached_job_ids = {f"{job['job_name']}_{job['company']}_{job['area']}" for job in cached_jobs}
    
    # 如果有新的职位ID，说明有更新
    return bool(current_job_ids - cached_job_ids)

def get_access_token():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID.strip(), appSecret.strip())
    response = session.get(url, timeout=TIMEOUT).json()
    print(response)
    access_token = response.get('access_token')
    return access_token

def get_job_info(job_name):
    url = "https://www.ncss.cn/student/jobs/jobslist/ajax/"
    params = {
        "jobType": "03",
        "areaCode": "",
        "jobName": job_name,
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
        response = session.get(url, params=params, headers=headers, timeout=TIMEOUT)
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

def send_job_info(access_token, jobs, job_type):
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
        "url": f"https://www.ncss.cn/student/m/jobs/index.html?offset=1&limit=10&jobType=03&jobName={job_type}&categoryCode=&sourcesName=&ssgxName=&sourcesType=&monthPay=&recruitType=&property=&degreeCode=&keyUnits=&memberLevel=",
        "data": data
    }
    
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
    response = session.post(url, json=body, timeout=TIMEOUT).json()
    print(f"发送{job_type}岗位结果：", response)

def job_report():
    # 定义要搜索的岗位列表
    job_types = ["GIS", "前端", "产品经理"]
    
    # 1. 获取access_token
    access_token = get_access_token()
    if not access_token:
        print("获取access_token失败")
        return
    
    # 2. 遍历每个岗位类型
    for job_type in job_types:
        print(f"\n正在获取{job_type}岗位信息...")
        jobs = get_job_info(job_type)
        if jobs:
            print(f"获取到 {len(jobs)} 条{job_type}岗位招聘信息")
            
            # 检查是否有新的职位信息
            if has_new_jobs(job_type, jobs):
                print(f"发现{job_type}岗位新职位，准备发送消息...")
                # 3. 发送消息
                send_job_info(access_token, jobs, job_type)
                # 更新缓存
                cache = load_cache()
                cache[job_type] = jobs
                save_cache(cache)
            else:
                print(f"{job_type}岗位没有新的职位信息")
            
            # 减少延时时间
            time.sleep(1)
        else:
            print(f"未获取到{job_type}岗位招聘信息")

if __name__ == '__main__':
    # 立即执行一次
    job_report()
    
    # 设置定时任务，每天早上9点执行
    # schedule.every().day.at("09:00").do(job_report)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)