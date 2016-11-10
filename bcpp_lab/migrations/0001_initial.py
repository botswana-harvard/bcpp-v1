# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-10 02:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_extensions.db.fields
import django_revision.revision_field
import edc_base.model.fields.custom_fields
import edc_base.model.fields.hostname_modification_field
import edc_base.model.fields.userfield
import edc_base.model.fields.uuid_auto_field
import edc_base.model.models.url_mixin
import edc_base.model.validators.date
import edc_protocol.validators
import edc_sync.model_mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bcpp_subject', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectRequisition',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('user_created', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user created')),
                ('user_modified', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(default='mac2-2.local', editable=False, help_text='System field. (modified on create only)', max_length=50)),
                ('hostname_modified', edc_base.model.fields.hostname_modification_field.HostnameModificationField(editable=False, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('id', edc_base.model.fields.uuid_auto_field.UUIDAutoField(blank=True, editable=False, help_text='System auto field. UUID primary key.', primary_key=True, serialize=False)),
                ('consent_version', models.CharField(default='?', editable=False, max_length=10)),
                ('panel_name', models.CharField(max_length=25)),
                ('requisition_identifier', models.CharField(editable=False, max_length=50, unique=True, verbose_name='Requisition Id')),
                ('requisition_datetime', models.DateTimeField(verbose_name='Requisition Date')),
                ('drawn_datetime', models.DateTimeField(blank=True, help_text='If not drawn, leave blank. Same as date and time of finger prick in case on DBS.', null=True, verbose_name='Date / Time Specimen Drawn')),
                ('is_drawn', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='Yes', help_text='If No, provide a reason below', max_length=3, verbose_name='Was a specimen drawn?')),
                ('reason_not_drawn', models.CharField(blank=True, choices=[('collection_failed', 'Tried, but unable obtaining sample from patient'), ('absent', 'Patient did not attend visit'), ('refused', 'Patient refused'), ('no_supplies', 'No supplies')], max_length=25, null=True, verbose_name='If not drawn, please explain')),
                ('specimen_identifier', models.CharField(editable=False, max_length=50, null=True, unique=True, verbose_name='Specimen Id')),
                ('study_site', models.CharField(max_length=10, null=True)),
                ('clinician_initials', edc_base.model.fields.custom_fields.InitialsField(blank=True, help_text='Type 2-3 letters, all in uppercase and no spaces', max_length=3, null=True, verbose_name='Initials')),
                ('specimen_type', models.CharField(max_length=25, verbose_name='Specimen type')),
                ('item_type', models.CharField(choices=[('tube', 'Tube'), ('swab', 'Swab'), ('dbs', 'DBS Card'), ('other', 'Other')], default='tube', max_length=25, verbose_name='Item collection type')),
                ('item_count', models.IntegerField(default=1, help_text='Number of tubes, samples, cards, etc being sent for this test/order only. Determines number of labels to print', verbose_name='Number of items')),
                ('estimated_volume', models.DecimalField(decimal_places=2, default=5.0, help_text='If applicable, estimated volume of sample for this test/order. This is the total volume if number of "tubes" above is greater than 1', max_digits=7, verbose_name='Estimated volume in mL')),
                ('comments', models.TextField(blank=True, max_length=25, null=True)),
                ('report_datetime', models.DateTimeField(default=django.utils.timezone.now, help_text="If reporting today, use today's date/time, otherwise use the date/time this information was reported.", validators=[edc_protocol.validators.datetime_not_before_study_start, edc_base.model.validators.date.datetime_not_future], verbose_name='Report Date')),
                ('subject_visit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bcpp_subject.SubjectVisit')),
            ],
            bases=(edc_sync.model_mixins.SyncMixin, edc_base.model.models.url_mixin.UrlMixin, models.Model),
        ),
    ]