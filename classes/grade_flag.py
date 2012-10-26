from lab_grading.classes import GradeFlag as BaseGradeFlag
from bhp_lab_tracker.classes import lab_tracker


class GradeFlag(BaseGradeFlag):

    def __init__(self, reference_list, result_item, **kwargs):
        test_code = result_item.test_code
        gender = result_item.result.order.aliquot.receive.registered_subject.gender
        dob = result_item.result.order.aliquot.receive.registered_subject.dob
        reference_datetime = result_item.result.order.aliquot.receive.receive_datetime
        subject_identifier = result_item.result.order.aliquot.receive.registered_subject.subject_identifier
        hiv_status = kwargs.get('hiv_status', None)
        if not hiv_status:
            subject_identifier, hiv_status, reference_datetime = lab_tracker.get_value(self.get_lab_tracker_group_name(), subject_identifier, reference_datetime)
        if not hiv_status:
            raise TypeError('hiv_status cannot be None.')
        super(GradeFlag, self).__init__(reference_list, test_code, gender, dob, reference_datetime, hiv_status)

    def get_lab_tracker_group_name(self):
        """Returns a group name to use when filtering on values in the lab_tracker class.

        See :mode:bhp_lab_tracker"""
        return 'HIV'
