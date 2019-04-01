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
        self.mylog.info('初始化项目名称：{}'.format(new_title2))


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
        self.mylog.info('执行《{}》条用例，用例参数：{}'.format(item['caseid'],params))
        resp = Request(method=item['method'],url=url,data=params,cookies=COOKIES)
        if resp.get_cookies():
            setattr(contex, 'COOKIES', resp.get_cookies())
        try:
            self.assertEqual(resp.get_txt(),item['excepted'])
            if resp.get_json()['msg'] == '加标成功':
                sql = 'SELECT * FROM future.loan  WHERE MemberID = "{}" and Title = "{}"'.format(
                    getattr(contex, 'normal_user_id'), params['title'])
                check_db = self.mysql.fet_one(sql=sql)
                self.assertEqual(check_db['Title'],params['title'])
                relust = 'Pass'
            elif resp.get_json()['msg'] == '登录成功':
                self.mylog.info('登录用户：{}'.format(params['admin_user']))
            else:
                sql = 'SELECT * FROM future.loan  WHERE MemberID = "{}" and Title = "{}"'.format(
                    getattr(contex, 'normal_user_id'), params['title'])
                check_db = self.mysql.fet_one(sql=sql)
                self.assertEqual(check_db,None)
            relust = 'Pass'
        except Exception as e:
            relust = 'Falied'
            self.mylog.error('第《{}》条用例执行失败，请检查数据或数据库结果'.format(item['caseid']))
            raise e
        finally:
            read.write_result('addloan',item['caseid'],resp.get_txt(),relust)
            self.mylog.info('第《》条用例执行完成'.format(item['caseid']))


