#  coding utf-8
# @time      :2019/3/1915:56
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :test_withdraw.py
from api_testing.common.request import Request
from api_testing.common.read_excel import ReadExcel
from api_testing.common.mysql import MySql
from api_testing.common.doregex import *
from ddt import ddt, data
from api_testing.common.mylog import MyLog
from api_testing.common.readconfig import ReadConfig
import unittest
import json

read = ReadExcel()
data_case = read.read_excel('withdraw')

@ddt
class Withdraw(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conf = ReadConfig()
        cls.mysql= MySql()
        cls.mylog = MyLog()


    def setUp(self):
        sql = 'SELECT * FROM future.member WHERE MobilePhone = "{}" '.format(getattr(contex,'withdraw_user'))
        value = MySql().fet_one(sql=sql)
        setattr(contex, 'LeaveAmount', value['LeaveAmount'])
        setattr(contex,'withdraw_user_id',value['Id'])

    @data(*data_case)
    def test_withdraw(self, item):
        result = None
        params = json.loads(DoRegex().replace(item['params'])) # 处理初始化数据
        if hasattr(contex, 'COOKIES'):  # 处理COOKIES
            COOKIES = getattr(contex, 'COOKIES')
        else:
            COOKIES = None
        self.mylog.info('执行第《{}》条用例，传入的参数是{}'.format(item['caseid'], params))
        url = self.conf.get('url','url') + item['url']
        resp = Request(method=item['method'], url=url, data=params, cookies=COOKIES)  # 开始HTTP请求
        if resp.get_cookies():
            setattr(contex, 'COOKIES', resp.get_cookies())
        sql = 'SELECT * FROM future.member WHERE Id = {} '.format(getattr(contex,'withdraw_user_id'))
        check_db = self.mysql.fet_one(sql=sql)
        res = resp.get_json()
        excepted = json.loads(item['excepted'])
        try:
            assert res['status'] ==excepted['status'] and res['code'] == excepted['code'] and res['msg'] == excepted['msg']
            if res['msg'] == '取现成功':
                self.assertEqual(float(getattr(contex,'LeaveAmount')),float(float(check_db['LeaveAmount']) + float(params['amount'])))
            elif res['msg'] == '充值成功':
                self.mylog.info('这是第{}条用例的前置条件'.format(item['caseid']+1))
            else:
                self.assertEqual(check_db['LeaveAmount'],getattr(contex,'LeaveAmount'))
            result = 'Pass'
            self.mylog.info('执行第《{}》条用例，运行结果为{}'.format(item['caseid'], result))
        except Exception as e:
            result = 'Falied'
            self.mylog.info('执行第《{}》条用例，运行结果为{}'.format(item['caseid'], result))
            raise e
        finally:
            self.mylog.info('写入测试结果，执行第《{}》条用例，运行结果为{}'.format(item['caseid'], result))
            read.write_result('withdraw', item['caseid'], resp.get_txt(), result)

