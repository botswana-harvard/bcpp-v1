from django.db.models import get_model
from model_rule import ModelRule


class ScheduledModelRule(ModelRule):
    
    def __init__(self, **kwargs):
        
        super(ScheduledModelRule, self).__init__(**kwargs)
        
        self._RAW_PREDICATE = 0
        self._CONSEQUENT_ACTION = 1
        self._ALTERNATIVE_ACTION = 2

        # extract the predicate from the logic. Note that we will
        # need to update this later with the current instance
        self.unresolved_predicate = self.logic[self._RAW_PREDICATE]
        
        # extract the actions from the logic
        self._consequent_action = self.logic[self._CONSEQUENT_ACTION]
        self._alternative_action = self.logic[self._ALTERNATIVE_ACTION]
        
    
    def run(self, instance, app_label):

        self.visit_model_instance = getattr(instance, self.visit_model_fieldname)
        
        # call super to build predicate, etc
        super(ScheduledModelRule, self).run(instance, app_label)
                
                       
        ScheduledEntryBucket = get_model('bhp_entry', 'scheduledentrybucket')
        ContentTypeMap = get_model('bhp_content_type_map', 'contenttypemap')
        # run the rule for each target model in the list
        for target_model in self._target_models:
            
            contenttypemap = ContentTypeMap.objects.get(app_label = target_model._meta.app_label,
                                                        model = target_model._meta.object_name.lower())
            if ScheduledEntryBucket.objects.filter(entry__content_type_map = contenttypemap):
                self._eval(instance, target_model)  
            else:
                raise ValueError('Cannot determine target model for bucket rule, %s' % (target_model,))
        
    def _eval(self, instance, target_model):

        """ evaluate predicate and update status if true """
    
        ScheduledEntryBucket = get_model('bhp_entry', 'scheduledentrybucket')

        if eval(self._predicate):
            ScheduledEntryBucket.objects.update_status( 
                model = target_model,
                visit_model_instance = getattr(instance, self.visit_model_fieldname),
                action = self._consequent_action,
                )
            #RuleHistory.objects.create(rule = self, 
            #                   model = target_model._meta.object_name.lower(), 
            #                   predicate = self._predicate, 
            #                   action = self._consequent_action)             
        else:
            ScheduledEntryBucket.objects.update_status( 
                model = target_model,
                visit_model_instance = getattr(instance, self.visit_model_fieldname),
                action = self._alternative_action,
                )
            #RuleHistory.objects.create(rule = self, 
            #                   model = target_model._meta.object_name.lower(), 
            #                   predicate = self._predicate, 
            #                   action = self._alternative_action)          
        
