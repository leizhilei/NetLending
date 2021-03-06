 # Ajax提取网页内容
import datetime
import time
import requests
from requests import HTTPError
from redis import StrictRedis
def mk_url_headers():
    url = 'https://www.wdzj.com/plat-center/platReview/getPlatReviewList' #请求的url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Host': 'www.wdzj.com',
        'Referer': 'https://www.wdzj.com/dangan/dianping/',
        'Origin': 'https://www.wdzj.com',
        'X - Requested - With': 'XMLHttpRequest',
        'Cookie': '__jsluid_s=aca8e48eaa7f8a46ce1060077b1001a0; _ga=GA1.2.1130660300.1601685935; _gid=GA1.2.1073006868.1601685935; gr_user_id=05c39165-24aa-4493-931b-61aa576fde81; __jsluid_h=0afbbede0da8a03fe1bd018c7b93a6f5; wdzj_session_source=https%253A%252F%252Fwww.wdzj.com%252Fdangan%252Fdianping%252F%2523nogo; WDZJptlbs=1; Hm_lvt_9e837711961994d9830dcd3f4b45f0b3=1601899188,1601901919,1601949816,1602030373; Hm_lpvt_9e837711961994d9830dcd3f4b45f0b3=1602030373; gr_session_id_1931ea22324b4036a653ff1d3a0b4693=3174d01a-3b2c-47ef-ad8a-174863f7371d; gr_session_id_1931ea22324b4036a653ff1d3a0b4693_3174d01a-3b2c-47ef-ad8a-174863f7371d=true'
    }
    return url, headers

def get_info(page):
    body = {
        'currentPage': page,
        'pageSize': '20',
        'orderType': '0',
        'reviewEvaluation': "",
        'tagName': ""
    }
    url, headers = mk_url_headers()
    try:
        response = requests.post(url, headers=headers, data=body)#用request请求连接，注意看前台的Request Method是get还是post
        if response.status_code == 200:  #如果状态码是200，代表请求成功
            return response.json()   #则直接调用json()方法将内容解析为JSON返回
    except requests.ConnectionError as e:
        print('Error', e.args)       #如果发生异常，直接捕获并输出异常信息

def get_info1(page):
    body = {
        'currentPage': page,
        'pageSize': '20',
        'orderType': '1',
        'reviewEvaluation': "",
        'tagName': ""
    }
    url, headers = mk_url_headers()
    try:
        response = requests.post(url, headers=headers, data=body)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)




def parse_page(json):
    try:
        if json:
            items = json.get('data').get('pagination').get('list') #用json.get方法取到Preview中的列表
            for item in items:    #循环取列表中的内容
                info = {}        #定义一个字典，将取到的内容都存入到字典中
                info['name'] = item.get('reviewUserName')
                timeStamp = (item.get('reviewDate'))/1000      #时间戳转化时间，主要时间戳的变化，这里要除以1000
                dateArray = datetime.datetime.fromtimestamp(timeStamp)
                otherStyleTime = dateArray.strftime("%Y-%m-%d")
                info['time'] =otherStyleTime
                info['website'] = item.get('platName')
                info['recommend'] = item.get('reviewEvaluation')
                info['impression'] = item.get('tagList')

                replys=item.get('replyList')  #获取到回复列表
                if replys:
                    # print(type(replys))
                    replyLists = []
                    for reply in replys:     #遍历回复列表，将所有回复内容加入到回复列表中
                        # print(reply)
                        replyLists.append(reply.get('reviewUserName')+':'+reply.get('reviewContent'))
                    replyLists="".join(replyLists)    #将列表转化为字符串
                    info['replyList']=replyLists
                # info['comment'] = pq(item.get('reviewContent')).text()
                info['comment'] = item.get('reviewContent')
                info['useful'] = item.get('useful')
                info['useless'] = item.get('noUseful')
                yield info
    except HTTPError as e:
        print('Error',e.args)


def insert(result):
    redis = StrictRedis(host='localhost', port=6379, db=0)
    redis.hmset(result['name'],result)   #hmset(name,mapping),向键名为name的散列表中批量添加映射
def insert1(result):
    redis = StrictRedis(host='localhost', port=6379, db=1)
    redis.hmset(result['name'], result)  # hmset(name,mapping),向键名为name的散列表中批量添加映射
if __name__ == '__main__':
    # for page in range(4092,5000):    #循环遍历取5000页信息
    #     print('正在爬取最新点评第',page,'页')
    #     infomation = get_info(page) #发送url,headers,body信息，请求网页内容
    #     results=parse_page(infomation)   #提取想要的信息
    #     for result in results:
    #         print(result['name'])
    #         insert(result)
    #         # time.sleep(3)

    for page in range(2349, 5000):
        print('正在爬取给力点评第',page,'页')
        infomation = get_info1(page)
        results=parse_page(infomation)
        for result in results:
            print(result['name'])
            insert1(result)
            # time.sleep(1)


