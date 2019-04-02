#  coding utf-8
# @time      :2019/3/1811:53
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :test_login.py
from common.read_excel import ReadExcel
from common.mylog import MyLog
from common.request import Request
from common.doregex import *
from common.readconfig import ReadConfig
from ddt import ddt, data, unpack
import unittest
import json

data_list = ReadExcel().read_excel('login')


@ddt
class Login(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conf = ReadConfig()

    @data(*data_list)
    @unpack
    def test_longin(self, caseid, method, params, excepted, url, title):
        global result
        params = json.loads(DoRegex().replace(params))
        url = self.conf.get('url', 'url') + url
        self.mylog.info('执行《{}》用例，执行参数是：{}'.format(title, params))
        resp = Request(method=method, url=url, data=params)
        try:
            self.assertEqual(resp.get_txt(), excepted)
            result = 'Pass'
            self.mylog.info('执行《{}》用例，执行结果是：{}'.format(title, params))
        except Exception as e:
            result = 'Failed'
            self.mylog.error('执行《{}》用例，执行结果是：{}'.format(title, params))
            raise e
        finally:
            ReadExcel().write_result('login', caseid=caseid, actual=resp.get_txt(), result=result)
            self.mylog.info('《{}》用例，测试结果写入完成'.format(title))

