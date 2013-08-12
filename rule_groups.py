from bhp_entry_rules.classes import RuleGroup, rule_groups, ScheduledDataRule, AdditionalDataRule, Logic
from bhp_registration.models import RegisteredSubject
from models import (SubjectVisit, ResourceUtilization, HivTestingHistory,
                    SexualBehaviour, HivCareAdherence, Circumcision, 
                    HivTestReview, ReproductiveHealth, MedicalDiagnoses)


class ResourceUtilizationRuleGroup(RuleGroup):

    out_patient = ScheduledDataRule(
        logic=Logic(
            predicate=(('out_patient', 'equals', 'no'), ('out_patient', 'equals', 'REF', 'or')),
            consequence='not_required',
            alternative='new'),
        target_model=['outpatientcare'])

    hospitalized = ScheduledDataRule(
        logic=Logic(
            predicate=(('hospitalized', 'equals', ''), ('hospitalized', 'equals', 0, 'or')),
            consequence='not_required',
            alternative='new'),
        target_model=['hospitaladmission'])

    class Meta:
        app_label = 'bcpp_subject'
        filter_model = (SubjectVisit, 'subject_visit')
        source_model = ResourceUtilization
rule_groups.register(ResourceUtilizationRuleGroup)


#Would probably be useful for T12 survey
# class SubjectDeathRuleGroup(RuleGroup):
# 
#     death = AdditionalDataRule(
#         logic=Logic(
#             predicate=('reason', 'equals', 'death'),
#             consequence='required',
#             alternative='not_required'),
#         target_model=['subjectoffstudy', 'subjectdeath'])
# 
#     class Meta:
#         app_label = 'bcpp_subject'
#         source_model = SubjectVisit
#         filter_model = (RegisteredSubject, 'registered_subject')
# rule_groups.register(SubjectDeathRuleGroup)


class HivTestingHistoryRuleGroup(RuleGroup):

    has_record = ScheduledDataRule(
        logic=Logic(
            predicate=('has_record', 'equals', 'Yes'),
            consequence='new',
            alternative='not_required'),
        target_model=['hivtestreview'])
    
    has_tested = ScheduledDataRule(
        logic=Logic(
            predicate=('has_tested', 'equals', 'Yes'),
            consequence='new',
            alternative='not_required'),
        target_model=['hivtested'])
    
    hiv_untested = ScheduledDataRule(
        logic=Logic(
            predicate=('has_tested', 'equals', 'No'),
            consequence='new',
            alternative='not_required'),
        target_model=['hivuntested'])
    
    other_record = ScheduledDataRule(
        logic=Logic(
            predicate=('other_record', 'equals', 'Yes'),
            consequence='new',
            alternative='not_required'),
        target_model=['hivresultdocumentation'])
    
    verbal_hiv_result = ScheduledDataRule(
        logic=Logic(
            predicate=('verbal_hiv_result', 'equals', 'POS'),
            consequence='new',
            alternative='not_required'),
        target_model=['hivcareadherence', 'positiveparticipant', 'hivhealthcarecosts', 'labourmarketwages'])
 
    verbal_response = ScheduledDataRule(
        logic=Logic(
            predicate=('verbal_hiv_result', 'equals', 'NEG'),
            consequence='new',
            alternative='not_required'),
        target_model=['futurehivtesting','stigma', 'stigmaopinion'])
    
    other_response = ScheduledDataRule(
        logic=Logic(
            predicate=(('verbal_hiv_result', 'ne', 'POS'), ('verbal_hiv_result', 'ne', 'NEG', 'or')),
            consequence='not_required',
            alternative='new'),
        target_model=['hivcareadherence', 'hivmedicalcare', 'positiveparticipant', 'hivhealthcarecosts', 'labourmarketwages', 'futurehivtesting', 'stigma', 'stigmaopinion'])


    class Meta:
        app_label = 'bcpp_subject'
        filter_model = (SubjectVisit, 'subject_visit')
        source_model = HivTestingHistory
rule_groups.register(HivTestingHistoryRuleGroup)


class HivTestReviewRuleGroup(RuleGroup):

    recorded_hiv_result = ScheduledDataRule(
        logic=Logic(
            predicate=('recorded_hiv_result', 'equals', 'POS'),
            consequence='new',
            alternative='not_required'),
        target_model=['hivcareadherence','positiveparticipant', 'hivhealthcarecosts', 'labourmarketwages'])

    recorded_hivresult = ScheduledDataRule(
        logic=Logic(
            predicate=('recorded_hiv_result', 'equals', 'NEG'),
            consequence='new',
            alternative='not_required'),
        target_model=['futurehivtesting','stigma', 'stigmaopinion'])
    
    other_responses = ScheduledDataRule(
        logic=Logic(
            predicate=(('recorded_hiv_result', 'ne', 'POS'), ('recorded_hiv_result', 'ne', 'NEG', 'or')),
            consequence='not_required',
            alternative='new'),
        target_model=['hivcareadherence', 'hivmedicalcare', 'positiveparticipant', 'hivhealthcarecosts', 'labourmarketwages', 'futurehivtesting', 'stigma', 'stigmaopinion'])

    class Meta:
        app_label = 'bcpp_subject'
        filter_model = (SubjectVisit, 'subject_visit')
        source_model = HivTestReview
rule_groups.register(HivTestReviewRuleGroup)



class MedicalCareRuleGroup(RuleGroup):

    medical_care = ScheduledDataRule(
        logic=Logic(
            predicate=('medical_care', 'equals', 'Yes'),
            consequence='new',
            alternative='not_required'),
        target_model=['hivmedicalcare'])

    class Meta:
        app_label = 'bcpp_subject'
        filter_model = (SubjectVisit, 'subject_visit')
        source_model = HivCareAdherence
rule_groups.register(MedicalCareRuleGroup)


class SexualBehaviourRuleGroup(RuleGroup):
    
    partners = ScheduledDataRule(
        logic=Logic(
            predicate=('last_year_partners', 'lt', 2),
            consequence='not_required',
            alternative='new'),
        target_model=['monthssecondpartner', 'monthsthirdpartner'])
    
    last_year_partners = ScheduledDataRule(
        logic=Logic(
            predicate=('last_year_partners', 'eq', 2),
            consequence='not_required',
            alternative='new'),
        target_model=['monthsthirdpartner'])
    
    more_partners = ScheduledDataRule(
        logic=Logic(
            predicate=('last_year_partners', 'gt', 2),
            consequence='new',
            alternative='not_required'),
        target_model=['monthsrecentpartner', 'monthssecondpartner', 'monthsthirdpartner'])

    ever_sex_two = ScheduledDataRule(
        logic=Logic(
            predicate=(('ever_sex', 'equals', 'No'),('ever_sex', 'equals', 'Don\'t want to answer', 'or')),
            consequence='not_required',
            alternative='new'),
        target_model=['monthsrecentpartner', 'monthssecondpartner', 'monthsthirdpartner'])
    
    class Meta:
        app_label = 'bcpp_subject'
        filter_model = (SubjectVisit, 'subject_visit')
        source_model = SexualBehaviour
rule_groups.register(SexualBehaviourRuleGroup)


class MaleCircumcisionRuleGroup(RuleGroup):

    gender = ScheduledDataRule(
        logic=Logic(
            predicate=('gender', 'equals', 'f'),
            consequence='not_required',
            alternative='new'),
        target_model=['circumcision', 'circumcised', 'uncircumcised'])

    class Meta:
        app_label = 'bcpp_subject'
        filter_model = (SubjectVisit, 'subject_visit')
        source_model = RegisteredSubject
rule_groups.register(MaleCircumcisionRuleGroup)


class CircumcisionRuleGroup(RuleGroup):

    circumcised = ScheduledDataRule(
        logic=Logic(
            predicate=('circumcised', 'equals', 'Yes'),
            consequence='new',
            alternative='not_required'),
        target_model=['circumcised'])
    
    uncircumcised = ScheduledDataRule(
        logic=Logic(
            predicate=('circumcised', 'equals', 'No'),
            consequence='new',
            alternative='not_required'),
        target_model=['uncircumcised'])

    class Meta:
        app_label = 'bcpp_subject'
        filter_model = (SubjectVisit, 'subject_visit')
        source_model = Circumcision
rule_groups.register(CircumcisionRuleGroup)


class FemaleReproductiveRuleGroup(RuleGroup):

    gender = ScheduledDataRule(
        logic=Logic(
            predicate=('gender', 'equals', 'm'),
            consequence='not_required',
            alternative='new'),
        target_model=['reproductivehealth', 'pregnancy', 'nonpregnancy'])

    class Meta:
        app_label = 'bcpp_subject'
        filter_model = (SubjectVisit, 'subject_visit')
        source_model = RegisteredSubject
rule_groups.register(FemaleReproductiveRuleGroup)


class ReproductiveRuleGroup(RuleGroup):

    menopause = ScheduledDataRule(
        logic=Logic(
            predicate=('menopause', 'equals', 'Yes'),
            consequence='not_required',
            alternative='new'),
        target_model=['pregnancy'])
    
    currently_pregnant = ScheduledDataRule(
        logic=Logic(
            predicate=('currently_pregnant', 'equals', 'Yes'),
            consequence='new',
            alternative='not_required'),
        target_model=['pregnancy'])
    
    pregnant = ScheduledDataRule(
        logic=Logic(
            predicate=('currently_pregnant', 'equals', 'No'),
            consequence='new',
            alternative='not_required'),
        target_model=['nonpregnancy'])
    

    class Meta:
        app_label = 'bcpp_subject'
        filter_model = (SubjectVisit, 'subject_visit')
        source_model = ReproductiveHealth
rule_groups.register(ReproductiveRuleGroup)


class MedicalDiagnosesRuleGroup(RuleGroup):

    heart_attack_record = ScheduledDataRule(
        logic=Logic(
            predicate=('heart_attack_record', 'equals', 'Yes'),
            consequence='new',
            alternative='not_required'),
        target_model=['heartattack'])

    cancer_record = ScheduledDataRule(
        logic=Logic(
            predicate=('cancer_record', 'equals', 'Yes'),
            consequence='new',
            alternative='not_required'),
        target_model=['cancer'])
    
    tb_record = ScheduledDataRule(
        logic=Logic(
            predicate=('tb_record', 'equals', 'Yes'),
            consequence='new',
            alternative='not_required'),
        target_model=['tubercolosis'])
    
    sti_record = ScheduledDataRule(
        logic=Logic(
            predicate=('sti_record', 'equals', 'Yes'),
            consequence='new',
            alternative='not_required'),
        target_model=['sti'])

    class Meta:
        app_label = 'bcpp_subject'
        filter_model = (SubjectVisit, 'subject_visit')
        source_model = MedicalDiagnoses
rule_groups.register(MedicalDiagnosesRuleGroup)
