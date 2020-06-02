import requests
import re
import time
import urllib3

urllib3.disable_warnings()

proxies = {
    'http': 'http://172.31.10.84:2345',
    'https': 'http://172.31.10.84:2345'
}

req_headers = {
    'Accept-Encoding': 'gzip, deflate',
    'Accept': 'application/json, text/javascript, */*; q=0.01,',
    'Connection': 'Keep-Alive',
    'Host': 'eva.customer.10086.cn',
    'Origin': 'https://eva.customer.10086.cn',
    #'Referer': 'https://eva.customer.10086.cn/survey/QnrTomatoOrange.html?token=covfnGb69714&&questionnaireId=2019112714550104601052001&&tokenflag=3f43a658',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
s = requests.session()
s.headers.update(req_headers)
if len(proxies):
    s.proxies = proxies


def submit_poll(url):
    r = s.get(url, verify=False)
    if '请求超时' in r.text:
        return '%s 链接已超时' % url

    jump302_url = r.url
    args = get_url_args(jump302_url)

    post_data = {
        "questionList": {
            "qnrSuggestion": "",
            "questionList": [
                {
                    "score": 10,
                    "questionId": "2019112714221718701051001",
                    "questionTitle": "故障维修整体满意度",
                    "answerOrder": 1,
                    "surveyObjType": "0",
                    "suggestion": "",
                    "surveyLables": ""
                },
                {
                    "score": 10,
                    "questionId": "2019112714472810201052001",
                    "questionTitle": "上门及时性",
                    "answerOrder": 2,
                    "surveyObjType": "0",
                    "suggestion": "",
                    "surveyLables": "上门快,上门准时,有提前预约时间"
                },
                {
                    "score": 10,
                    "questionId": "2019112714481805801051001",
                    "questionTitle": "故障解决专业性",
                    "answerOrder": 3,
                    "surveyObjType": "0",
                    "suggestion": "",
                    "surveyLables": "故障解决快,现场干净整洁"
                },
                {
                    "score": 10,
                    "questionId": "2019112714504311401052001",
                    "questionTitle": "维修人员服务",
                    "answerOrder": 4,
                    "surveyObjType": "0",
                    "suggestion": "",
                    "surveyLables": "服务态度好,答疑指导耐心,工装整洁大方"
                },
                {
                    "score": "",
                    "questionId": "2019112714514659501053001",
                    "questionTitle": "维修完成后是否测速",
                    "suggestion": "",
                    "surveyLables": "是",
                    "surveyObjType": "0",
                    "answerOrder": 5
                }
            ]
        },
        "serNum": '',
        "channelId": '',
        "serType": '',
        "prvo": '',
        "servalue": '',
        "detailsUrl": '/survey/detailsofTomatoOrange.html?taskSheetId='
    }

    post_data['qnrId'] = args['questionnaireId']
    post_data['h5PageUrlWeb'] = 'https://eva.customer.10086.cn/surv/QnrTomatoOrange.html?questionnaireId=%s' % args['questionnaireId']
    post_data['token'] = args['token']

    print(post_data)
    req_headers['Referer'] = jump302_url
    s.headers.update(req_headers)
    r = s.post(
        'https://eva.customer.10086.cn/surveyH5Response/dynamicQuestion',
        json=post_data,
        verify=False
    )
    if r.status_code == 200:
        del req_headers['Referer']
        return 'msg:success, status_code:%s, url:%s' % (r.status_code, url)
        #return r.content
    else:
        return 'msg:failed, status_code:%s, url:%s' % (r.status_code, url)


def get_url_args(url):
    args = url.split('?')[1].replace('&&', '&').split('&')
    data = {}
    for i in args:
        x = i.split('=')
        data[x[0]] = x[1]
    return data


if __name__ == "__main__":
    # 提前10分钟
    pre_time = 10
    # 文件名
    file_name = 'data.txt'
    # 日期时间格式
    fmt = '%Y/%m/%d %H:%M'

    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.read().replace('	', '|')

    lines = re.sub(' +', ' ', lines)
    if not len(lines):
        exit('file is empty')

    lines = lines.split('\n')
    while True:
        if not len(lines):
            exit('done')

        for line in lines:
            if line.strip() == ' ':
                continue
            x = line.split('|')
            now = int(time.time())
            end_date = time.mktime(time.strptime(x[0], fmt))
            #print (end_date-now)
            if end_date-now <= pre_time*60:
                r = submit_poll(x[1])
                print(r)
                # print(line)
                lines.pop(0)
