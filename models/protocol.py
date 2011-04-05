from django.db import models
from bhp_research_protocol.models import PrincipalInvestigator, SiteLeader, FundingSource

class Protocol(models.Model):

    protocol_identifier = models.CharField(
        max_length=25, 
        null=True,
        )

    research_title = models.TextField(max_length=250)

    short_title = models.CharField(max_length=25)

    local_title = models.CharField(max_length=25, blank=True)
    
    prinicipal_investigator = models.ManyToManyField(PrincipalInvestigator)

    site_leader = models.ManyToManyField(SiteLeader)

    funding_source = models.ManyToManyField(FundingSource)
    
    date_registered = models.DateField(
        verbose_name = "Date registered with BHP",
        )

    date_opened = models.DateField(
        verbose_name = "Date opened",
        )

    description = models.TextField(
        max_length=500,
        )    

    def __unicode__(self):
        return '%s %s' % (self.protocol_identifier, self.local_title)
        
    class Meta:
        ordering = ['protocol_identifier']

