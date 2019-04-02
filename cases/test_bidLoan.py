#  coding utf-8
# @time      :2019/3/2010:57
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :test_bidLoan.py
from common.read_excel import ReadExcel
from common.request import Request
from common.doregex import *
from common.mysql import MySql
from common.readconfig import ReadConfig
from common.mylog import MyLog
from decimal import Decimal
import json
from ddt import ddt, data
import unittest

read = ReadExcel()
data_case = read.read_excel('bidLoan')


@ddt
class BidLoan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conf = ReadConfig()
        cls.mylog = MyLog()
        options = conf.getoptions('test_user')
        for item in options:
            memberId_sql = 'SELECT Id from future.member WHERE MobilePhone = "{0}"'.format(
                conf.getstr('test_user', item)['user'])
            cls.mylog.info('初始化用户数据sql:{}'.format(memberId_sql))
            memberId = MySql().fet_one(memberId_sql)
            setattr(contex, item + '_id', str(memberId['Id']))
            cls.mylog.info('获取到{}，的id是{}'.format(conf.getstr('test_user', item)['user'], memberId['Id']))
            new_title = conf.get('project', 'title')
            # 加标成功后重新生成一个新的标名
            conf.set('project', 'title', new_title[:4] + str(int(new_title[4::1]) + 1))

    def setUp(self):
        self.mysql = MySql()
        sql = DoRegex().replace(conf.get('sql', 'sql'))
        val = self.mysql.fet_one(sql)
        if val:  # 将借款标id写入到contex中
            setattr(contex, 'loanid', str(val['Id']))
            sql1 = DoRegex().replace(conf.get('sql', 'sql1'))
            sel_value = self.mysql.fet_one(sql1)
            if sel_value['投资人账号余额']:  # 下面将 投资改标的 以投资金额， 投资人信息 写入到contex类
                setattr(contex, '投资人账号余额', sel_value['投资人账号余额'])
                Balance = int(sel_value['借款金额']) - int(sel_value['已投资总额'])
                setattr(contex, '剩余可投金额', Balance)
                setattr(contex, '已投资总额', sel_value['已投资总额'])
                self.mylog.info('投资人账号余额:{},已投资总额:{}，剩余可投金额:{}'.format(getattr(contex, '投资人账号余额'), getattr(contex, '已投资总额'),
                                                           getattr(contex, '剩余可投金额')))

    @data(*data_case)
    def test_bidLoan(self, item):
        global result, check_db
        # 处理登录用户的COOKIES
        if hasattr(contex, 'COOKIES'):
            COOKIES = getattr(contex, 'COOKIES')
        else:
            COOKIES = None
        params = json.loads(DoRegex().replace(item['params']))

        if item['caseid'] == 2:
            params['title'] = self.conf.get('project','title')


        self.mylog.info('测试数据请求初始化{}'.format(params))
        if item['title'] == '投资金额大于标的余额':  # 执行投资金额大于标的余额的用例
            Balance = getattr(contex, '剩余可投金额') + Decimal(1000)
            params['amount'] = Balance
            url = self.conf.get('url', 'url') + item['url']
            resp = Request(method=item['method'], url=url, data=params, cookies=COOKIES)
            if resp.get_json()['msg'] == '加标成功':
                new_title = self.conf.get('project', 'title')
                new_title2 = new_title[:4] + str(int(new_title[4::1]) + 1)  # 加标成功后重新生成一个新的标名
                self.conf.set('project', 'title', new_title2)
            excepted = json.loads(item['excepted'])
            actual = resp.get_json()
            try:
                assert actual['status'] == excepted['status'] and actual['code'] == excepted['code']
                result = 'Pass'
                self.mylog.info('{}用例执行结果：{}'.format(item['title'], result))
            except Exception as e:
                result = 'Failed'
                self.mylog.info('{}用例执行结果：{}'.format(item['title'], result))
                self.mylog.error(e)
                raise e
            finally:
                read.write_result('bidLoan', item['caseid'], resp.get_txt(), result)
        elif item['title'] == '将标投满':  # 执行该用例将标注满
            Balance = getattr(contex, '剩余可投金额')
            params['amount'] = Balance
            url = self.conf.get('url', 'url') + item['url']
            resp = Request(method=item['method'], url=url, data=params, cookies=COOKIES)
            if resp.cookies():
                setattr(contex, 'COOKIES', resp.cookies())
            try:
                self.assertEqual(resp.get_txt(), item['excepted'])
                result = 'Pass'
                # self.mylog.info('{}用例执行结果：{}'.format(item['title'], result))
            except Exception as e:
                result = 'Failed'
                # self.mylog.info('{}用例执行结果：{}'.format(item['title'], result))
                # self.mylog.error(e)
                raise
            finally:
                read.write_result('bidLoan', item['caseid'], resp.get_txt(), result)
        else:  # 执行其他用例
            url = self.conf.get('url', 'url') + item['url']
            resp = Request(method=item['method'], url=url, data=params, cookies=COOKIES)
            if resp.cookies():
                setattr(contex, 'COOKIES', resp.cookies())
            try:
                self.assertEqual(resp.get_txt(), item['excepted'])
                result = 'Pass'
                self.mylog.info('《{}》用例执行结果：{}'.format(item['title'], result))
            except Exception as e:
                result = 'Failed'
                self.mylog.info('《{}》用例执行结果：{}'.format(item['title'], result))
                self.mylog.error(e)
                raise
            finally:
                read.write_result('bidLoan', item['caseid'], resp.get_txt(), result)

    def tearDown(self):
        self.mysql.mysql_close()


