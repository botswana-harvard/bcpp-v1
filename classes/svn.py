import os, pysvn
from django.contrib import messages
from bhp_netbook.models import Netbook, SvnHistory

class Svn(object):

    def update_svn(self, **kwargs):

        client = pysvn.Client()
        folders = os.listdir('/home/django/source/bhp041_new')
        
        # update mochudi

        netbooks = Netbook.objects.filter(name='s014')
        for netbook in netbooks:
            for prefix in ['mochudi_', 'bhp_', 'lab_']:
                retries = 3    
                counter = 0
                for fld in [fld for fld in folders if fld[0:len(prefix)] == prefix]:
                    if SvnHistory.objects.filter(netbook=netbook, repo=fld):
                        svn_history = SvnHistory.objects.get(netbook=netbook, repo=fld)
                    else:
                        svn_history = SvnHistory.objects.create(netbook=netbook, repo=fld)    
                    svn  = client.update(fld)
                    if not svn[0].number == -1:
                        messages.add_message(request, messages.SUCCESS, '%s revision %s', (fld, svn[0].number))                                              
                    svn_history.last_revision_number = svn[0].number
                    svn_history.last_revision_date = svn[0].date                    
                    svn_history.save()
                    if svn[0].number == -1:
                        svn  = client.update(fld)                
                        if not svn[0].number == -1:
                            messages.add_message(request, messages.SUCCESS, '%s revision %s', (fld, svn[0].number))                                              
                        svn_history.last_revision_number = svn[0].number
                        svn_history.last_revision_date = svn[0].date                                            
                        svn_history.save()
                        if svn[0].number == -1:
                            svn  = client.update(fld)                
                            if not svn[0].number == -1:
                                messages.add_message(request, messages.SUCCESS, '%s revision %s', (fld, svn[0].number))                                              
                            svn_history.last_revision_number = svn[0].number
                            svn_history.last_revision_date = svn[0].date                    
                            svn_history.save()
                            if svn[0].number == -1:
                                pass
                                #raise ValueError, 'Cannot update repo %s' % (fld,)
                


