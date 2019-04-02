#  coding utf-8
# @time      :2019/3/1915:56
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :test_withdraw.py
from common.request import Request
from common.read_excel import ReadExcel
from common.mysql import MySql
from common.doregex import *
from ddt import ddt, data
from common.mylog import MyLog
from common.readconfig import ReadConfig
from decimal import Decimal
import unittest
import json

read = ReadExcel()
data_case = read.read_excel('withdraw')

@ddt
class Withdraw(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conf = ReadConfig()
        cls.mylog = MyLog()


    def setUp(self):
        sql = 'SELECT * FROM future.member WHERE MobilePhone = "{}" '.format(getattr(contex,'withdraw_user'))
        self.mysql = MySql()
        value = self.mysql.fet_one(sql=sql)
        setattr(contex, 'LeaveAmount', value['LeaveAmount'])
        setattr(contex,'withdraw_user_id',value['Id'])

    def tearDown(self):
        self.mysql.mysql_close()

    @data(*data_case)
    def test_withdraw(self, item):
        result = None
        params = json.loads(DoRegex().replace(item['params'])) # 处理初始化数据
        if hasattr(contex, 'COOKIES'):  # 处理COOKIES
            COOKIES = getattr(contex, 'COOKIES')
        else:
            COOKIES = None
        url = self.conf.get('url','url') + item['url']
        self.mylog.info('执行《{}》用例，执行参数是：{}'.format(item['title'],params))
        resp = Request(method=item['method'], url=url, data=params, cookies=COOKIES)  # 开始HTTP请求
        if resp.cookies():
            setattr(contex, 'COOKIES', resp.cookies())
        sql = 'SELECT * FROM future.member WHERE Id = {} '.format(getattr(contex,'withdraw_user_id'))
        check_db = self.mysql.fet_one(sql=sql)
        self.mylog.info('数据库查询结果：{}'.format(check_db))
        res = resp.get_json()
        excepted = json.loads(item['excepted'])
        try:
            assert res['status'] ==excepted['status'] and res['code'] == excepted['code'] and res['msg'] == excepted['msg']
            if res['msg'] == '取现成功':
                self.assertEqual(getattr(contex,'LeaveAmount')-check_db['LeaveAmount'],Decimal(params['amount']))
            elif res['msg'] == '充值成功':
                print('这是第{}条用例的前置条件'.format(item['caseid']+1))
            else:
                self.assertEqual(check_db['LeaveAmount'],getattr(contex,'LeaveAmount'))
            result = 'Pass'
            self.mylog.info('执行《{}》用例，执行结果是：{}'.format(item['title'], result))
        except Exception as e:
            result = 'Falied'
            self.mylog.info('执行《{}》用例，执行结果是：{}'.format(item['title'], result))
            raise e
        finally:
            read.write_result('withdraw', item['caseid'], resp.get_txt(), result)
            self.mylog.info('《{}》用例，测试结果写入完成'.format(item['title']))

