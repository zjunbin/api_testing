#  coding utf-8
# @time      :2019/3/1115:55
# @Author    :zjunbin
# @Email     :648060307@qq.com
# @File      :case_run.py
import HTMLTestRunnerNew
import unittest

from common import constants

from cases import test_login, test_loadadd, test_bidLoan, test_recharge,test_register,test_withdraw
suite = unittest.TestSuite()
loader = unittest.TestLoader()
suite.addTest(loader.loadTestsFromModule(test_register))
suite.addTest(loader.loadTestsFromModule(test_login))
suite.addTest(loader.loadTestsFromModule(test_recharge))
suite.addTest(loader.loadTestsFromModule(test_withdraw))
suite.addTest(loader.loadTestsFromModule(test_bidLoan))
suite.addTest(loader.loadTestsFromModule(test_loadadd))

# discover = unittest.defaultTestLoader.discover(start_dir=r'I:\PycharmProjects\api_testing\cases',pattern="test_*.py",top_level_dir=None)

with open(constants.result_path, 'wb') as file:
    run = HTMLTestRunnerNew.HTMLTestRunner(stream=file,
                                          verbosity=2,
                                          title='apitesting',
                                          description='20190402',
                                          tester='admin')
    run.run(suite)

