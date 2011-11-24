import os
from datetime import datetime
from django.contrib import messages
from bhp_common.models import MyModelAdmin
from bhp_nmap.utils import all_uphosts
from bhp_netbook.classes import Svn
from models import Netbook


def netbook_uphosts(modeladmin, request, queryset):

    all_hosts = all_uphosts(network='192.168.11.0/24')    
    for netbook in Netbook.objects.all():
        if netbook.name in all_hosts.keys():        
            netbook.is_alive = True
            netbook.last_seen = datetime.today()
        else:
            netbook.is_alive = False                        
        netbook.save()            
        
netbook_uphosts.short_description = "Refresh list of active netbooks"

def netbook_update_svn(modeladmin, request, queryset):
    
    netbook_name = os.gethostname()
    svn = Svn()
    svn.update_svn(request=request, netbook_name=netbook_name)
    messages.add_message(request, messages.SUCCESS, 'Local svn repositories have been updated')                      

netbook_update_svn.short_description = "Update local svn repositories"
