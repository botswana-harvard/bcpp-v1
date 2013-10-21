# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'SubjectRequisitionInspector.aliquot_type'
        db.delete_column('bcpp_inspector_subjectrequisitioninspector', 'aliquot_type')


    def backwards(self, orm):
        # Adding field 'SubjectRequisitionInspector.aliquot_type'
        db.add_column('bcpp_inspector_subjectrequisitioninspector', 'aliquot_type',
                      self.gf('django.db.models.fields.CharField')(default='xx', max_length=50),
                      keep_default=False)


    models = {
        'bcpp_inspector.subjectrequisitioninspector': {
            'Meta': {'object_name': 'SubjectRequisitionInspector'},
            'app_name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'device_id': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'One.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'One.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'is_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'item_identifier': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'requisition_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'requisition_identifier': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'specimen_identifier': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'subject_identifier': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'})
        }
    }

    complete_apps = ['bcpp_inspector']