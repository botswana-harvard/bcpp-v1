from django.db import models
from bhp_common.models import MyBasicListModel


class AliquotCondition(MyBasicListModel):
    
    def __unicode__(self):
        return "%s: %s" % ( self.short_name.upper() ,self.name)
    class Meta:
        ordering = ["short_name"]
        app_label = 'bhp_lab_aliquot' 
        db_table = 'bhp_lab_core_aliquotcondition'        
