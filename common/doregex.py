#  coding utf-8
# @time      :2019/3/149:44
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :doregex.py
import re
from api_testing.common.readconfig import ReadConfig

conf = ReadConfig()

class contex:
    normal_user = conf.getstr('test_user','normal_user')['user']
    normal_pwd = conf.getstr('test_user','normal_user')['pwd']
    admin_user = conf.getstr('test_user', 'admin_user')['user']
    admin_pwd = conf.getstr('test_user', 'admin_user')['pwd']
    loanid_user = conf.getstr('test_user', 'loanid_user')['user']
    loanid_pwd = conf.getstr('test_user', 'loanid_user')['pwd']
    withdraw_user = conf.getstr('test_user', 'withdraw_user')['user']
    withdraw_pwd = conf.getstr('test_user', 'withdraw_user')['pwd']
    title = conf.get('project','title')
    amount = conf.get('project','amount')
    sql = conf.get('sql','sql')


class DoRegex:
    def replace(self, data):
        res = re.findall('\$\{(.*?)\}', data)
        for item in res:
            value = getattr(contex, item)
            data = re.sub('\$\{(.*?)\}', value, data, count=1)
        return data

if __name__ == '__main__':
    # import json
    doRe = DoRegex()
    data = '{"memberId":"${normal_user}","title":"${new_title}","amount":"200000","loanRate":"18.0","loanTerm":"12","loanDateType":"0","repaymemtWay":"4","biddingDays":"5"}'
    value= doRe.replace(data)
    print(value)