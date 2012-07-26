from django.contrib import admin
from bhp_bucket.models import RuleHistory


class RuleHistoryAdmin(admin.ModelAdmin):     
      
    list_display = ('action', 'model', 'predicate', 'rule', 'timestamp')
    
admin.site.register(RuleHistory, RuleHistoryAdmin)