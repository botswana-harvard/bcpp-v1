from lab_grading.classes import GradeFlag


class ClinicGradeFlag(GradeFlag):

    def __init__(self, reference_list, result_item, **kwargs):
        """Extracts parameters from lab_clinic_api.ResultItem, which has a different structure to that in lab_result_item.ResultItem."""
        test_code = result_item.test_code
        gender = result_item.result.order.aliquot.receive.registered_subject.gender
        dob = result_item.result.order.aliquot.receive.registered_subject.dob
        reference_datetime = result_item.result.order.aliquot.receive.receive_datetime
        subject_identifier = result_item.result.order.aliquot.receive.registered_subject.subject_identifier
        kwargs = {'hiv_status':result_item.result.order.aliquot.receive.registered_subject.hiv_status}
        super(ClinicGradeFlag, self).__init__(
            subject_identifier,
            reference_list,
            test_code,
            gender,
            dob,
            reference_datetime,
            **kwargs)

    def get_lab_tracker_group_name(self):
        """Returns a group name to use when filtering on values in the lab_tracker class.

        See :mode:bhp_lab_tracker"""
        return 'HIV'
