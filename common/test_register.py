#  coding utf-8
# @time      :2019/3/1513:35
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :test_register.py
import unittest
from common.read_excel import ReadExcel
from common.readconfig import ReadConfig
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
class TestRegister(unittest.TestCase):
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
        params = json.loads(item['params'])
        # 如果mobilephone 等于 phone ,那么去配置文件中获取初始手机号码
        if params['mobilephone'] == 'phone':
            value = int(self.conf.get('register', 'phone'))
            params['mobilephone'] = value
            # 手机号码使用之后将手机号码+1写会配置文件
            self.conf.set('register', 'phone', str(value + 1))
        self.mylog.debug('开始http请求')
        url = self.conf.get('url', 'url') + item['url']
        self.mylog.info('执行第《{}》条用例，参数是：{}'.format(item['caseid'], params))
        resp = Request(method=item['method'], url=url, data=params, cookies=COOKIES)
        if resp.get_cookies():
            COOKIES = resp.get_cookies()
        actual = resp.get_txt()
        try:
            self.assertEqual(actual, item['excepted'])
            sql = 'SELECT * FROM future.member WHERE MobilePhone = "{}"'.format(params['mobilephone'])
            if resp.get_json()['msg'] == '注册成功':  # 注册成功的用例查询数据库是否有改条数据
                check_db = self.mysql.fet_one(sql=sql)
                self.assertEqual(check_db['MobilePhone'],str(params['mobilephone']))
            result = 'Pass'
            self.mylog.info('《{}》用例执行通过'.format(item['title']))
        except Exception as e:
            result = 'Falied'
            self.mylog.info('{}:用例执行未通过'.format(item['title']))
            raise e
        finally:
            read.write_result('register', item['caseid'], actual, result)
            self.mylog.info('{}:测试结果写入完成'.format(item['title']))
