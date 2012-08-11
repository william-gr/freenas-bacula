# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BaculaSDService'
        db.create_table('freenas_baculasdservice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('enable', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('freenas', ['BaculaSDService'])

        # Adding model 'BaculaSDStorage'
        db.create_table('freenas_baculasdstorage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('baculasd_st_name', self.gf('django.db.models.fields.CharField')(default='freenas-sd', unique=True, max_length=255)),
            ('baculasd_st_sdport', self.gf('django.db.models.fields.IntegerField')(default=9103, unique=True)),
            ('baculasd_st_maximumconcurrentjobs', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('baculasd_st_proceeddespiteioerrors', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('freenas', ['BaculaSDStorage'])

        # Adding model 'BaculaSDDirector'
        db.create_table('freenas_baculasddirector', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('baculasd_dir_name', self.gf('django.db.models.fields.CharField')(default='bacula-dir', unique=True, max_length=255)),
            ('baculasd_dir_password', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('baculasd_dir_monitor', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('freenas', ['BaculaSDDirector'])

        # Adding model 'BaculaSDDevice'
        db.create_table('freenas_baculasddevice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('baculasd_dev_name', self.gf('django.db.models.fields.CharField')(default='FileStorage', unique=True, max_length=127)),
            ('baculasd_dev_mediatype', self.gf('django.db.models.fields.CharField')(default='File', max_length=5)),
            ('baculasd_dev_archivedevice', self.gf('django.db.models.fields.CharField')(default='/mnt/tank/bacula', unique=True, max_length=255)),
            ('baculasd_dev_labelmedia', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('baculasd_dev_randomaccess', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('baculasd_dev_removablemedia', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('baculasd_dev_alwaysopen', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('baculasd_dev_maximumconcurrentjobs', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('freenas', ['BaculaSDDevice'])

        # Adding model 'BaculaSDMessages'
        db.create_table('freenas_baculasdmessages', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('baculasd_msg_name', self.gf('django.db.models.fields.CharField')(default='Standard', unique=True, max_length=255)),
            ('baculasd_msg_destination', self.gf('django.db.models.fields.CharField')(default='director', max_length=15)),
            ('baculasd_msg_address', self.gf('django.db.models.fields.CharField')(default='bacula-dir', max_length=255, blank=True)),
            ('baculasd_msg_msgtype1', self.gf('django.db.models.fields.CharField')(default='all', max_length=9)),
            ('baculasd_msg_msgtype2', self.gf('django.db.models.fields.CharField')(default='', max_length=9, blank=True)),
            ('baculasd_msg_msgtype3', self.gf('django.db.models.fields.CharField')(default='', max_length=9, blank=True)),
            ('baculasd_msg_msgtypeaux', self.gf('django.db.models.fields.TextField')(default='# message-type4, message-type5, message-type6, ... ', blank=True)),
        ))
        db.send_create_signal('freenas', ['BaculaSDMessages'])

        # Adding model 'BaculaSDDeviceAssignment'
        db.create_table('freenas_baculasddeviceassignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('baculasd_map_device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freenas.BaculaSDDevice'])),
            ('baculasd_map_storage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freenas.BaculaSDStorage'])),
        ))
        db.send_create_signal('freenas', ['BaculaSDDeviceAssignment'])

        # Adding model 'BaculaSDDirectorAssignment'
        db.create_table('freenas_baculasddirectorassignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('baculasd_map_director', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freenas.BaculaSDDirector'])),
            ('baculasd_map_storage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freenas.BaculaSDStorage'])),
        ))
        db.send_create_signal('freenas', ['BaculaSDDirectorAssignment'])

        # Adding model 'BaculaSDMessagesAssignment'
        db.create_table('freenas_baculasdmessagesassignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('baculasd_map_messages', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freenas.BaculaSDMessages'])),
            ('baculasd_map_storage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freenas.BaculaSDStorage'])),
        ))
        db.send_create_signal('freenas', ['BaculaSDMessagesAssignment'])


    def backwards(self, orm):
        # Deleting model 'BaculaSDService'
        db.delete_table('freenas_baculasdservice')

        # Deleting model 'BaculaSDStorage'
        db.delete_table('freenas_baculasdstorage')

        # Deleting model 'BaculaSDDirector'
        db.delete_table('freenas_baculasddirector')

        # Deleting model 'BaculaSDDevice'
        db.delete_table('freenas_baculasddevice')

        # Deleting model 'BaculaSDMessages'
        db.delete_table('freenas_baculasdmessages')

        # Deleting model 'BaculaSDDeviceAssignment'
        db.delete_table('freenas_baculasddeviceassignment')

        # Deleting model 'BaculaSDDirectorAssignment'
        db.delete_table('freenas_baculasddirectorassignment')

        # Deleting model 'BaculaSDMessagesAssignment'
        db.delete_table('freenas_baculasdmessagesassignment')


    models = {
        'freenas.baculasddevice': {
            'Meta': {'object_name': 'BaculaSDDevice'},
            'baculasd_dev_alwaysopen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'baculasd_dev_archivedevice': ('django.db.models.fields.CharField', [], {'default': "'/mnt/tank/bacula'", 'unique': 'True', 'max_length': '255'}),
            'baculasd_dev_labelmedia': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'baculasd_dev_maximumconcurrentjobs': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'baculasd_dev_mediatype': ('django.db.models.fields.CharField', [], {'default': "'File'", 'max_length': '5'}),
            'baculasd_dev_name': ('django.db.models.fields.CharField', [], {'default': "'FileStorage'", 'unique': 'True', 'max_length': '127'}),
            'baculasd_dev_randomaccess': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'baculasd_dev_removablemedia': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'freenas.baculasddeviceassignment': {
            'Meta': {'object_name': 'BaculaSDDeviceAssignment'},
            'baculasd_map_device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freenas.BaculaSDDevice']"}),
            'baculasd_map_storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freenas.BaculaSDStorage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'freenas.baculasddirector': {
            'Meta': {'object_name': 'BaculaSDDirector'},
            'baculasd_dir_monitor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'baculasd_dir_name': ('django.db.models.fields.CharField', [], {'default': "'bacula-dir'", 'unique': 'True', 'max_length': '255'}),
            'baculasd_dir_password': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'freenas.baculasddirectorassignment': {
            'Meta': {'object_name': 'BaculaSDDirectorAssignment'},
            'baculasd_map_director': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freenas.BaculaSDDirector']"}),
            'baculasd_map_storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freenas.BaculaSDStorage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'freenas.baculasdmessages': {
            'Meta': {'object_name': 'BaculaSDMessages'},
            'baculasd_msg_address': ('django.db.models.fields.CharField', [], {'default': "'bacula-dir'", 'max_length': '255', 'blank': 'True'}),
            'baculasd_msg_destination': ('django.db.models.fields.CharField', [], {'default': "'director'", 'max_length': '15'}),
            'baculasd_msg_msgtype1': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '9'}),
            'baculasd_msg_msgtype2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '9', 'blank': 'True'}),
            'baculasd_msg_msgtype3': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '9', 'blank': 'True'}),
            'baculasd_msg_msgtypeaux': ('django.db.models.fields.TextField', [], {'default': "'# message-type4, message-type5, message-type6, ... '", 'blank': 'True'}),
            'baculasd_msg_name': ('django.db.models.fields.CharField', [], {'default': "'Standard'", 'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'freenas.baculasdmessagesassignment': {
            'Meta': {'object_name': 'BaculaSDMessagesAssignment'},
            'baculasd_map_messages': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freenas.BaculaSDMessages']"}),
            'baculasd_map_storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freenas.BaculaSDStorage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'freenas.baculasdservice': {
            'Meta': {'object_name': 'BaculaSDService'},
            'enable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'freenas.baculasdstorage': {
            'Meta': {'object_name': 'BaculaSDStorage'},
            'baculasd_st_maximumconcurrentjobs': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'baculasd_st_name': ('django.db.models.fields.CharField', [], {'default': "'freenas-sd'", 'unique': 'True', 'max_length': '255'}),
            'baculasd_st_proceeddespiteioerrors': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'baculasd_st_sdport': ('django.db.models.fields.IntegerField', [], {'default': '9103', 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['freenas']