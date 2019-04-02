#  coding utf-8
# @time      :2019/3/2614:31
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :test_loadadd.py
from common.request import Request
from common.read_excel import ReadExcel
from common.readconfig import ReadConfig
from common.doregex import *
from common.mysql import MySql
from common.mylog import MyLog
from ddt import ddt,data
import unittest
import json

read = ReadExcel()
data_case = read.read_excel('addloan')

@ddt
class LoadAdd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mylog = MyLog()
        cls.mylog = MyLog()
        sql = 'SELECT Id FROM future.member WHERE MobilePhone = "{}"'.format(getattr(contex,'normal_user'))
        value = MySql().fet_one(sql)
        setattr(contex,'normal_user_id',str(value['Id']))

    def setUp(self):
        self.mysql = MySql()
        self.conf = ReadConfig()
        new_title = self.conf.get('project', 'new_title')
        new_title2 = new_title[:3] + str(int(new_title[3::1]) + 1)  # 加标成功后重新生成一个新的标名
        self.conf.set('project', 'new_title', new_title2)


    @data(*data_case)
    def test_loadadd(self,item):
        global relust
        if hasattr(contex,'COOKIES'):
            COOKIES = getattr(contex,'COOKIES')
        else:
            COOKIES = None
        url = self.conf.get('url','url')+item['url']
        params = json.loads(DoRegex().replace(item['params']))
        if item['caseid'] > 1:
            params['title'] = self.conf.get('project','new_title')
        resp = Request(method=item['method'],url=url,data=params,cookies=COOKIES)
        if resp.cookies():
            setattr(contex, 'COOKIES', resp.cookies())
        try:
            self.assertEqual(resp.get_txt(),item['excepted'])
            if resp.get_json()['msg'] == '加标成功':
                sql = 'SELECT * FROM future.loan  WHERE MemberID = "{}" and Title = "{}"'.format(
                    getattr(contex, 'normal_user_id'), params['title'])
                check_db = self.mysql.fet_one(sql=sql)
                self.mylog.info('数据库查询结果：{}'.format(check_db))
                self.assertEqual(check_db['Title'],params['title'])
                result = 'Pass'
                self.mylog.info('执行《{}》用例，执行结果是：{}'.format(item['title'], result))
            elif resp.get_json()['msg'] == '登录成功':
                self.mylog.info('登录成功')
            else:
                sql = 'SELECT * FROM future.loan  WHERE MemberID = "{}" and Title = "{}"'.format(
                    getattr(contex, 'normal_user_id'), params['title'])
                check_db = self.mysql.fet_one(sql=sql)
                self.mylog.info('数据库查询结果：{}'.format(check_db))
                self.assertEqual(check_db,None)
                result = 'Pass'
                self.mylog.info('执行《{}》用例，执行结果是：{}'.format(item['title'], result))
        except Exception as e:
            result = 'Falied'
            self.mylog.error('执行《{}》用例，执行结果是：{}'.format(item['title'], result))
            raise e
        finally:
            read.write_result('addloan',item['caseid'],resp.get_txt(),relust)
            self.mylog.info('《{}》用例，测试结果写入完成'.format(item['title']))



