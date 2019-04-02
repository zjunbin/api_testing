#  coding utf-8
# @time      :2019/3/1513:35
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :test_register.py
import unittest
from common.read_excel import ReadExcel
from common.readconfig import ReadConfig
from common.doregex import *
from common.request import Request
from common.mylog import MyLog
from common.mysql import MySql
from ddt import ddt, data
import json

read = ReadExcel()
data_case = read.read_excel('register')
conf = ReadConfig()

COOKIES = None


@ddt
class Register(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conf = ReadConfig()
        cls.mylog = MyLog()

    def setUp(self):
        self.mysql = MySql()

    def tearDown(self):
        self.mysql.mysql_close()

    @data(*data_case)
    def test_register(self, item):
        global COOKIES, result
        params = json.loads(DoRegex().replace(item['params']))
        # 如果mobilephone 等于 phone ,那么去配置文件中获取初始手机号码
        if params['mobilephone'] == 'phone':
            value = int(self.conf.get('register', 'phone'))
            params['mobilephone'] = value
            # 手机号码使用之后将手机号码+1写会配置文件
            self.conf.set('register', 'phone', str(value + 1))
        url = self.conf.get('url', 'url') + item['url']
        resp = Request(method=item['method'], url=url, data=params, cookies=COOKIES)
        if resp.cookies():
            COOKIES = resp.cookies()
        actual = resp.get_txt()
        try:
            self.assertEqual(actual, item['excepted'])
            sql = 'SELECT * FROM future.member WHERE MobilePhone = "{}"'.format(params['mobilephone'])
            if resp.get_json()['msg'] == '注册成功':  # 注册成功的用例查询数据库是否有改条数据
                check_db = self.mysql.fet_one(sql=sql)
                self.mylog.info('数据库查询结果：{}'.format(check_db))
                self.assertEqual(check_db['MobilePhone'],str(params['mobilephone']))
            result = 'Pass'
            self.mylog.info('执行《{}》用例，执行结果是：{}'.format(item['title'], result))
        except Exception as e:
            result = 'Falied'
            self.mylog.error('执行《{}》用例，执行结果是：{}'.format(item['title'], result))
            raise e
        finally:
            read.write_result('register', item['caseid'], actual, result)
            self.mylog.info('《{}》用例，测试结果写入完成'.format(item['title']))

