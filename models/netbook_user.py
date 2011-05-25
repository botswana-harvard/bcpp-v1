from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from bhp_common.models import MyBasicModel
from netbook import Netbook
class NetbookUser(MyBasicModel):
  
    netbook = models.ForeignKey(Netbook)    
    
    user = models.ForeignKey(User)
    
    start_date = models.DateField("Date assigned", 
        help_text=_("Format is YYYY-MM-DD"),
        )
    end_date = models.DateField("Date revoked", 
        null=True, 
        blank=True, 
        help_text = _("Leave blank if in use. Format is YYYY-MM-DD"),
        )

    def __unicode__(self):
        return "%s %s" % (self.user, self.netbook)
    def get_absolute_url(self):
        return "/bhp_netbook/netbookuser/%s/" % self.id  
    class Meta:
        unique_together=['netbook', 'user']
        ordering=['netbook']     
        app_label='bhp_netbook'   

