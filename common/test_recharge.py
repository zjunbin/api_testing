#  coding utf-8
# @time      :2019/3/1910:19
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :test_recharge.py
from common.read_excel import ReadExcel
from common.request import Request
from common.doregex import *
from common.mysql import MySql
from common.mylog import MyLog
from ddt import ddt, data
import unittest
import json

read = ReadExcel()
data_case = read.read_excel('recharge')


@ddt
class Recharge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conf = ReadConfig()
        cls.mylog = MyLog()

    def setUp(self):
        self.mysql = MySql()
        sql = 'SELECT * FROM future.member WHERE MobilePhone = "{}" '.format(getattr(contex, 'loanid_user'))
        value = self.mysql.fet_one(sql=sql)
        setattr(contex, 'LeaveAmount', value['LeaveAmount'])
        setattr(contex, 'loanid_user_id', value['Id'])

    def tearDown(self):
        self.mysql.mysql_close()

    @data(*data_case)
    def test_recharge(self, item):
        '''通过反射查看是否有COOKIES的值'''
        global result
        if hasattr(contex, 'COOKIES'):
            COOKIES = getattr(contex, 'COOKIES')
        else:
            COOKIES = None
        params = item['params']
        '''通过读取配置文件替换params中的用户名或密码，并序列化'''
        params = json.loads(DoRegex().replace(params))
        self.mylog.info('执行第《{}》条用例，传入的参数是{}'.format(item['caseid'], params))
        url = self.conf.get('url', 'url') + item['url']
        resp = Request(method=item['method'], url=item['url'], data=params, cookies=COOKIES)
        '''登陆成功后将获取到的值通过反射写入到配置类中'''
        if resp.get_cookies():
            setattr(contex, 'COOKIES', resp.get_cookies())
        res = resp.get_json()
        excepted = json.loads(item['excepted'])
        #  充值成功的进行数据库校验
        sql = 'SELECT * FROM future.member WHERE Id = "{}"'.format(getattr(contex, 'loanid_user_id'))
        sel_value = self.mysql.fet_one(sql=sql)
        try:
            assert res['code'] == excepted['code'] and res['status'] == excepted['status'] and res['msg'] == excepted[
                'msg']
            if res['msg'] == '充值成功':  # 充值成功 判断充值后的金额是否等于充值前的金额加锁充值金额
                self.assertEqual(float(sel_value['LeaveAmount']),
                                 float(getattr(contex, 'LeaveAmount')) + float(params['amount']))
            else:  # 充值失败  金额不变
                self.assertEqual(sel_value['LeaveAmount'], getattr(contex, 'LeaveAmount'))
            result = 'Pass'
            self.mylog.info('执行第《{}》条用例，运行结果为{}'.format(item['caseid'], result))
        except Exception as e:
            result = 'Failed'
            self.mylog.info('执行第《{}》条用例，运行结果为{}'.format(item['caseid'], result))
            raise e
        finally:
            read.write_result('recharge', item['caseid'], resp.get_txt(), result)
            self.mylog.info('写入测试结果，执行第《{}》条用例，运行结果为{}'.format(item['caseid'], result))
