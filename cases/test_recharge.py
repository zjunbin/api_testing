#  coding utf-8
# @time      :2019/4/114:22
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :test_recharge.py
from common.doregex import *
from common.request import Request
from common.read_excel import ReadExcel
from common.readconfig import ReadConfig
from common.mysql import MySql
from common.mylog import MyLog
from ddt import ddt, data
import unittest
import json

read = ReadExcel()
data_case = read.read_excel('recharge')

@ddt
class Recharge(unittest.TestCase):

    def setUpClass(cls):
        cls.mylog = MyLog()

    def setUp(self):
        self.mysql = MySql()
        sql = 'SELECT * FROM future.member WHERE MobilePhone = "{}" '.format(getattr(contex, 'loanid_user'))
        sel_value = self.mysql.fet_one(sql)
        setattr(contex, 'LeaveAmount', sel_value['LeaveAmount'])

    def tearDown(self):
        self.mysql.mysql_close()

    @data(*data_case)
    def test_Recharge(self, item):
        global result
        if hasattr(contex, 'COOKIES'):
            COOKIES = getattr(contex, 'COOKIES')
        else:
            COOKIES = None
        params =json.loads(DoRegex().replace(item['params']))
        url = ReadConfig().get('url','url')+item['url']
        self.mylog.info('执行《{}》用例，执行参数是：{}'.format(item['title'], params))
        resp = Request(method=item['method'],url=url,data=params,cookies=COOKIES)
        if resp.cookies():
            setattr(contex,'COOKIES',resp.cookies())
        sql = 'SELECT * FROM future.member WHERE MobilePhone = "{}" '.format(getattr(contex, 'loanid_user'))
        sel_value = self.mysql.fet_one(sql)
        self.mylog.info('数据库查询结果：{}'.format(sel_value))
        try:
            self.assertEqual(resp.get_json()['code'],json.loads(item['excepted'])['code'])
            self.assertEqual(resp.get_json()['msg'],json.loads(item['excepted'])['msg'])
            if resp.get_json()['msg'] == '充值成功':
                self.assertEqual(float(sel_value['LeaveAmount']),float(getattr(contex, 'LeaveAmount')) + float(params['amount']))
            else:
                self.assertEqual(getattr(contex,'LeaveAmount'),sel_value['LeaveAmount'])
            result = 'Pass'
            self.mylog.info('执行《{}》用例，执行结果是：{}'.format(item['title'], result))
        except Exception as e:
            result = 'Failed'
            self.mylog.error('执行《{}》用例，执行结果是：{}'.format(item['title'], result))
            raise e
        finally:
            read.write_result('register', item['caseid'], resp.get_txt(), result)




