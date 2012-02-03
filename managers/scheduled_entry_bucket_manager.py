from datetime import datetime
from django.db import models
from django.db.models import ForeignKey, get_model, Q
from django.db.models.base import ModelBase
from bhp_content_type_map.models import ContentTypeMap
from bhp_entry.models import Entry
from bhp_entry.managers import BaseEntryBucketManager


class ScheduledEntryBucketManager(BaseEntryBucketManager):

    def get_scheduled_forms_for(self, **kwargs ):
    
        """Return a queryset of ScheduledEntryBucket objects for the given subject and appointment.
        
        Note that ScheduledEntryBucket objects are linked to a subject's appointment 
        for visit_instance = '0'; that is, the first appointment for 
        a timepoint/visit. """
        
        entry_category = kwargs.get("entry_category", 'clinic')
        registered_subject = kwargs.get("registered_subject")
        if not registered_subject:
            raise TypeError("Manager get_schedule_forms_for expected registered_subject. Got None.") 
        appt_0 = kwargs.get("appointment")
        visit_code = kwargs.get("visit_code")        
        if not visit_code:
            raise TypeError("Manager get_schedule_forms_for expected visit_code. Got None.")
        if appt_0:    
            # get the scheduled crfs based on the appt for visit_instance = '0'   
            scheduled_entry_bucket = super(ScheduledEntryBucketManager, self).filter(
                                                registered_subject = registered_subject, 
                                                appointment = appt_0,
                                                entry__entry_category = entry_category,
                                                ).order_by('entry__entry_order')
        else:
            scheduled_entry_bucket = super(ScheduledEntryBucketManager, self).none()         
            
        return scheduled_entry_bucket


    def add_for_visit(self, **kwargs):
        
        """ Add entries to the scheduled_entry_bucket for a given visit_model. 
        
        
        for example, 
        
        class VisitAdmin(MyRegisteredSubjectModelAdmin):

            form = VisitForm

            def save_model(self, request, obj, form, change):

                ScheduledEntryBucket.objects.add_for_visit(
                    visit_model_instance = obj,
                    )                
                    
                return super(VisitAdmin, self).save_model(request, obj, form, change)                                                
                
            search_fields = ('appointment__registered_subject__subject_identifier',)        
        
        """

        visit_model_instance = kwargs.get('visit_model_instance')

        # confirm visit_model_instance has a "appointment" field/model attribute
        if 'appointment' not in [f.name for f in visit_model_instance._meta.fields if f.name=='appointment']:
            raise AttributeError, "ScheduledEntryBucketManager expects model %s to have attribute \'appointment\'." % visit_model_instance._meta.object_name  
        
        registered_subject = visit_model_instance.appointment.registered_subject

        if kwargs.get('subject_visit_model'):
            raise ValueError('subject_visit_model has been changed to \'visit_model_instance\', please read comment in ScheduledEntryBucketManager.add_for_visit() and correct.')


        # scheduled entries are only added if visit instance is 0
        if visit_model_instance.appointment.visit_instance == '0':
        
            filled_datetime = datetime.today()
            report_datetime = visit_model_instance.report_datetime
                            
            # fetch entries required for this the visit definition of this visit_model_instance.appointment
            entries = Entry.objects.filter(visit_definition=visit_model_instance.appointment.visit_definition)

            for entry in entries:

                # calculate due date -- "needs work"
                due_datetime = entry.visit_definition.get_upper_window_datetime(report_datetime)                                

                # check if entry.entry_form.model has been keyed for this registered_subject, timepoint
                # if so, set report date and status accordingly

                # scheduled forms have a foreign key to a visit_model_instance
                # model must have field of value visit_model_instance_field, otherwise ignore
                visit_model_instance_field = [fk for fk in [f for f in entry.content_type_map.model_class()._meta.fields if isinstance(f,ForeignKey)] if fk.rel.to._meta.module_name == visit_model_instance._meta.module_name]                        
                if visit_model_instance_field:
                    qset = Q(**{visit_model_instance_field[0].name:visit_model_instance})
                    if not super(ScheduledEntryBucketManager, self).filter(
                                    registered_subject = registered_subject, 
                                    appointment = visit_model_instance.appointment, 
                                    entry = entry):                        
                        # not in bucket, but should be, so add to bucket
                        super(ScheduledEntryBucketManager, self).create(
                                registered_subject=registered_subject,
                                appointment = visit_model_instance.appointment,
                                entry = entry,
                                current_entry_title = entry.content_type_map.model_class()._meta.verbose_name,
                                fill_datetime = filled_datetime,
                                due_datetime = due_datetime,                      
                                )
                
                    if entry.content_type_map.model_class().objects.filter(qset):
                        report_datetime = visit_model_instance.report_datetime
                        # add to bucket, if not already added, or update
                        if super(ScheduledEntryBucketManager, self).filter(
                                    registered_subject = registered_subject, 
                                    appointment = visit_model_instance.appointment, 
                                    entry = entry):
                            # already in bucket, so get bucket entry
                            s = super(ScheduledEntryBucketManager, self).get(
                                        registered_subject = registered_subject, 
                                        appointment = visit_model_instance.appointment, 
                                        entry = entry)
                            # update report_date
                            s.report_datetime = report_datetime
                            # update status if NEW only, (may be queried or something)
                            if s.entry_status == 'NEW':
                                s.entry_status = 'KEYED'
                            # save
                            s.save()

    def update_status(self, **kwargs):

        """Update bucket status, etc for a given entry in bucket. 
        
        
        for example
        
        
        def save_model(self, request, obj, form, change):
            
            ScheduledEntryBucket.objects.update_status(
                model = obj,
                visit_model_instance = obj.visit,
                )
                            
            return super(MyVisitModelAdmin, self).save_model(request, obj, form, change)
            
        def delete_model(self, request, obj):

            ScheduledEntryBucket.objects.update_status(
                model = obj,
                action = 'delete',
                visit_model_instance = obj.visit,
                )
                
            return super(MyVisitModelAdmin, self).delete_model(request, obj)         
        
        """    

        # need to determine the visit model instance and the content_type_map value for this Entry 
        # coming from 'admin' is model instance
        # coming from 'forms' is a model

        self.set_visit_model_instance(**kwargs)  
        self.set_content_type_map(**kwargs)
        if kwargs.get('subject_visit_model'):
            raise AttributeError('subject_visit_model should be \'visit_model_instance\', please correct call to update_status')
        action = kwargs.get('action', 'add_change')
        comment = kwargs.get('comment', '----')
        model_filter_qset = kwargs.get('model_filter_qset')
        # have content_type_map and visit_mode_instance, so good to go from here...
        if self.visit_model_instance:
            # get visit definition for visit_model_instance attached to this model
            visit_definition = self.visit_model_instance.appointment.visit_definition
            # get Entry using visit_definition and content_type_map 
            entry = Entry.objects.filter(visit_definition = visit_definition, content_type_map = self.content_type_map)        
            # check if entry.content_type_map.model has been keyed for this registered_subject, timepoint
            # if so, set report date and status accordingly
            report_datetime = self.visit_model_instance.report_datetime
            registered_subject = self.visit_model_instance.appointment.registered_subject
            appointment = self.visit_model_instance.appointment.__class__.objects.get(
                registered_subject = registered_subject, 
                visit_definition__code = self.visit_model_instance.appointment.visit_definition.code, 
                visit_instance = '0')
            # update

            if super(ScheduledEntryBucketManager, self).filter(registered_subject = registered_subject, appointment = appointment, entry = entry):
                # already in bucket, so get bucket entry
                scheduled_entry_bucket = super(ScheduledEntryBucketManager, self).get(registered_subject = registered_subject, appointment = appointment, entry = entry)
                # update entry_status if NEW no matter what, to indictate perhaps that it was modified
                status = self.get_status(
                    action = action, 
                    report_datetime = report_datetime, 
                    entry_status = scheduled_entry_bucket.entry_status, 
                    entry_comment = comment
                    )
                # uncommented the if condition below 03/02/2012    
                if not (scheduled_entry_bucket.entry_status.lower() == 'keyed' and action.lower() == 'not_required'):
                    scheduled_entry_bucket.report_datetime = status['report_datetime']
                    scheduled_entry_bucket.entry_status = status['entry_status']
                    scheduled_entry_bucket.entry_comment = status['entry_comment']                
                    scheduled_entry_bucket.close_datetime = status['close_datetime']                
                    scheduled_entry_bucket.modified = datetime.today()
                    scheduled_entry_bucket.save()                    
                if scheduled_entry_bucket.entry_status.lower() == 'keyed' and action.lower() == 'not_required':
                    scheduled_entry_bucket.report_datetime = status['report_datetime']
                    scheduled_entry_bucket.entry_comment = 'NOT REQUIRED!'                
                    scheduled_entry_bucket.close_datetime = status['close_datetime']                
                    scheduled_entry_bucket.modified = datetime.today()
                    scheduled_entry_bucket.save()                    

