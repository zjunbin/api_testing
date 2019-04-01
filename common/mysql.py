#  coding utf-8
# @time      :2019/3/1815:07
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :mysql.py
import pymysql
from common.doregex import *
from common.readconfig import ReadConfig



class MySql:
    def __init__(self):
        conf = ReadConfig()
        host = conf.get('mysql', 'host')
        user = conf.get('mysql', 'user')
        password = conf.get('mysql', 'pwd')
        port = conf.getint('mysql', 'port')
        cursorclass = pymysql.cursors.DictCursor
        self.mysql = pymysql.connect(host=host, user=user, password=password, port=port,cursorclass= cursorclass)


    def fet_one(self, sql):
        cursor = self.mysql.cursor()
        try:
            cursor.execute(sql)
        except Exception as e:
            raise e
        return cursor.fetchone()

    def fet_all(self, sql):
        cursor = self.mysql.cursor()
        try:
            cursor.execute(sql)
        except Exception as e:
            raise e
        return cursor.fetchall()

    def mysql_close(self):
        return self.mysql.close()

if __name__ == '__main__':
    mysql = MySql()
    sql = 'SELECT * FROM future.member WHERE MobilePhone = "13822221114"'
    value =mysql.fet_one(sql)
    print(type(value))
    try:
        assert  value == None
        print('pass')
    except Exception as e:
        print('failed')


    print(type(None))

