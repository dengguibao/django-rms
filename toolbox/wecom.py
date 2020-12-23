#! /usr/bin/python
#_*_coding:utf-8 _*_
import argparse
import json
import sys
if sys.version_info[0] == 2:
    import urllib as request
else:
    from urllib import request


class WeCom:

    def __init__(self, secret, corp_id, agent_id):
        self.secret = secret
        self.corp_id = corp_id
        self.agent_id = agent_id
        self.domain = 'https://qyapi.weixin.qq.com'

    def get_token(self):
        url = '{domain}/cgi-bin/gettoken?corpid={corpid}&corpsecret={secret}'.format(
            domain=self.domain,
            corpid=self.corp_id,
            secret=self.secret
        )
        res = request.urlopen(url)
        if res.getcode() == 200:
            return json.loads(res.read().decode())
        else:
            return None

    def send_msg(self, access_token, content, to_user='@all', to_part='', to_tag=''):
        if to_user != '@all' and to_part == '' and to_tag == '':
            return

        d = {
           "touser": to_user,
           "toparty": to_part,
           "totag": to_tag,
           "msgtype": "text",
           "agentid": self.agent_id,
           "text": {
               "content": content
           },
           "safe": 0
        }
        url = '{domain}/cgi-bin/message/send?access_token={token}'.format(
            domain=self.domain,
            token=access_token
        )
        json_data = json.dumps(d, ensure_ascii=False, encoding='utf-8').replace('\\n','n').replace('\\r','r')
        # print(json_data)
        res = request.urlopen(url, data=json_data)
        if res.getcode in (200, 201):
            return json.loads(res.read().decode())
        else:
            return


if __name__ == '__main__':
    av = sys.argv[1:]
    if not len(av):
        av.append('-h')

    parser = argparse.ArgumentParser(description='WeCom(Wechat Business version) send message program')
    # parser.add_argument('--app-id', type=str, required=True, help='app id')
    parser.add_argument('--secret', type=str, required=True, help='secret')
    parser.add_argument('--company-id', type=str, required=True, help='login wecom control panel, click "my company" menu, found this arg')
    parser.add_argument('--agent-id', type=int, required=True, help='login wecom control panel, click app manage,found this arg')
    parser.add_argument('--content', type=str, required=True, help='message content')
    parser.add_argument('--to-user', type=str, default='@all', help='message send to user, default is all of user, multi part use "|" split.')
    parser.add_argument('--to-part', type=str, help='message to part name, if receive user is all, ignore this, multi part use "|" split.')
    parser.add_argument('--to-tag', type=str, help='message tag name, if receive user is all, ignore this, multi part use "|" split.')
    args = parser.parse_args(av)

    # APP_ID = args.app_id
    SECRET = args.secret
    CORP_ID = args.company_id
    AGENT_ID = args.agent_id
    TO_USER = args.to_user
    TO_PART = args.to_part
    TO_TAG = args.to_tag
    CONTENT = args.content

    wx = WeCom(SECRET, CORP_ID, AGENT_ID)
    token_data = wx.get_token()
    token = None
    if token_data and 'access_token' in token_data:
        token = token_data['access_token']

    if token:
        wx.send_msg(token, CONTENT, TO_USER, TO_PART, TO_TAG)
