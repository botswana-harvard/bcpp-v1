from bhp_base_model.classes import BaseListModel


class AliquotCondition(BaseListModel):
    
    def __unicode__(self):
        return "%s: %s" % ( self.short_name.upper() ,self.name)
    class Meta:
        ordering = ["short_name"]
        app_label = 'lab_aliquot_list' 
        db_table = 'bhp_lab_core_aliquotcondition'        
