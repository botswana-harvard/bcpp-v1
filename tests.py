'''
Created on Oct 19, 2012

@author: sirone
'''
from django.utils import unittest
from models import ResultItem, TestCode, TestCodeGroup, Receive, Order, Aliquot, Result
from bhp_registration.models import RegisteredSubject
from lab_result_item.classes import ResultItemFlag
from test_case_data import *
import pdb


class ResultItemTestCase(unittest.TestCase):
    def __init__(self):
        pass

    # def setUp(self):
        # self.item = ResultItem.objects.create(subject_identifier="xxx", receive_identifier="xxxxx")
    def test_print_no_returned(self):
        return self.test_data.count()

    def test_Haemaglobin_grade_flag(self):      
#            for flag_args in TRUE_G1_ASSERTIONS:
#                grade = self.get_result_item_flag(flag_args)
#                self.assertTrue(grade == 1,"TRUE_G1 "+str(flag_args['result_value'])+" FAILED. Returned Grade="+str(grade))
#            print "--------------------------------------------------------------------"
            for flag_args in FALSE_G1_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertFalse(grade == 1,"FALSE_G1 "+str(flag_args['result_value'])+" FAILED. Returned Grade="+str(grade))
#            print "--------------------------------------------------------------------"
            for flag_args in TRUE_G2_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertTrue(grade == 2,"TRUE_G2 "+str(flag_args['result_value'])+" FAILED. Returned Grade="+str(grade))
#            print "--------------------------------------------------------------------"
            for flag_args in FALSE_G2_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertFalse(grade == 2,"FALSE_G2 "+str(flag_args['result_value'])+" FAILED. Returned Grade="+str(grade))
#            print "--------------------------------------------------------------------"
            for flag_args in TRUE_G3_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertTrue(grade == 3,"TRUE_G3 "+str(flag_args['result_value'])+" FAILED. Returned Grade="+str(grade))
#            print "--------------------------------------------------------------------"
            for flag_args in FALSE_G3_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertFalse(grade == 3,"FALSE_G3 "+str(flag_args['result_value'])+" FAILED. Returned Grade="+str(grade))
#            print "--------------------------------------------------------------------"
            for flag_args in TRUE_G4_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertTrue(grade == 4,"TRUE_G4 "+str(flag_args['result_value'])+" FAILED. Returned Grade="+str(grade))
#            print "--------------------------------------------------------------------"
            for flag_args in FALSE_G4_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertFalse(grade == 4,"FALSE_G4 "+str(flag_args['result_value'])+" FAILED. Returned Grade="+str(grade))
#            print "--------------------------------------------------------------------"

    def get_result_item_flag(self,flag_args):
        result_item = ResultItem()
        subject = RegisteredSubject()
        test_code = TestCode()
        test_code.pk = 3 #TODO : Query this value from DB
        #test_code_temp = TestCode.objects.filter(code='HGB')
        #test_code.pk = test_code_temp[0].pk
        #print test_code_temp[0].pk
        test_code_group = TestCodeGroup()
        #test_code_group_temp = TestCodeGroup.objects.filter(code='HGB')
        test_code_group.code = 301#TODO : Query this value from DB
        test_code_group.pk = 1
        test_code.test_code_group = test_code_group
        result_item.result_item_value_as_float = flag_args['result_value']
        test_code.code = flag_args['test_code']
        test_code.display_decimal_places = 1
        test_code.units = 'g/dL'
        result_item.test_code = test_code
        result_item.result_item_datetime = flag_args['datetime_drawn']
        subject.dob = flag_args['dob']
        subject.gender = flag_args['gender']
        subject.hiv_status = flag_args['hiv_status']                
        receive = Receive()
        receive.registered_subject = subject
        aliquot = Aliquot()
        aliquot.receive = receive
        order = Order()
        order.aliquot = aliquot
        result = Result()
        result.order = order
        result_item.result = result
        #pdb.set_trace()
        reference_range, reference_flag, grade_range, grade_flag = ResultItemFlag().calculate(result_item)
        return result_item.grade_flag
    
    def main(self):
        rs = ResultItemTestCase()
        rs.test_Haemaglobin_grade_flag()
        
    if __name__ == '__main__':
            main()