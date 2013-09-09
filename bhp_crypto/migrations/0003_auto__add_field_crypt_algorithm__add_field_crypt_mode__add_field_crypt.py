# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Crypt.algorithm'
        db.add_column('bhp_crypto_crypt', 'algorithm', self.gf('django.db.models.fields.CharField')(max_length=25, null=True), keep_default=False)

        # Adding field 'Crypt.mode'
        db.add_column('bhp_crypto_crypt', 'mode', self.gf('django.db.models.fields.CharField')(max_length=25, null=True), keep_default=False)

        # Adding field 'Crypt.salt'
        db.add_column('bhp_crypto_crypt', 'salt', self.gf('django.db.models.fields.CharField')(max_length=50, null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Crypt.algorithm'
        db.delete_column('bhp_crypto_crypt', 'algorithm')

        # Deleting field 'Crypt.mode'
        db.delete_column('bhp_crypto_crypt', 'mode')

        # Deleting field 'Crypt.salt'
        db.delete_column('bhp_crypto_crypt', 'salt')


    models = {
        'bhp_crypto.crypt': {
            'Meta': {'object_name': 'Crypt'},
            'algorithm': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True'}),
            'cipher_text': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'hash_text': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'})
        },
        'bhp_crypto.testmodel': {
            'Meta': {'object_name': 'TestModel'},
            'char1': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'char2': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'text1': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'text2': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'text3': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'})
        },
        'bhp_crypto.testmodelaudit': {
            'Meta': {'ordering': "['-_audit_timestamp']", 'object_name': 'TestModelAudit', 'db_table': "'bhp_crypto_testmodel_audit'"},
            '_audit_change_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            '_audit_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            '_audit_subject_identifier': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            '_audit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'char1': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'char2': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'text1': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'text2': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'text3': ('django.db.models.fields.CharField', [], {'max_length': '78L'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'})
        }
    }

    complete_apps = ['bhp_crypto']
