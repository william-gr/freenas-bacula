import json
import os
import pwd
import urllib

from django.utils.translation import ugettext_lazy as _

from dojango import forms
from baculaUI.freenas import models, utils


class BaculaSDServiceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BaculaSDStorageForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        obj = super(BaculaSDStorageForm, self).save(*args, **kwargs)
        #started = notifier().reload("baculasd")
        #if started is False and models.services.objects.get(srv_service = 'baculasd').srv_enable:
        #    raise ServiceFailed("baculasd", _("The Bacula Storage Daemon failed to reload."))

        return obj

    class Meta:
        model = models.BaculaSDStorage
        widgets = {
            'baculasd_st_sdport': forms.widgets.TextInput(),
        }


class BaculaSDStorageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BaculaSDStorageForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        obj = super(BaculaSDStorageForm, self).save(*args, **kwargs)
        #started = notifier().reload("baculasd")
        #if started is False and models.services.objects.get(srv_service = 'baculasd').srv_enable:
        #    raise ServiceFailed("baculasd", _("The Bacula Storage Daemon failed to reload."))

        """
        advanced_settings = {}
        for field in obj._meta.local_fields:
            if field.attname not in utils.bacula_advanced_vars:
                continue
            info = utils.bacula_advanced_vars.get(field.attname)
            value = getattr(obj, field.attname)
            if info["type"] == "checkbox":
                if value:
                    if info.get("on"):
                        advanced_settings[field.attname] = info["on"]
                else:
                    if info.get("off"):
                        advanced_settings[field.attname] = info["off"]

            elif info["type"] == "textbox" and value:
                advanced_settings[field.attname] = "%s %s" % (info["opt"], value)

        rcconf = os.path.join(utils.bacula_etc_path, "rc.conf")
        with open(rcconf, "w") as f:
            if obj.enable:
                f.write('bacula_enable="YES"\n')

            if obj.watch_dir:
                f.write('bacula_watch_dir="%s"\n' % (obj.watch_dir, ))

            if obj.conf_dir:
                f.write('bacula_conf_dir="%s"\n' % (obj.conf_dir, ))

            if obj.download_dir:
                f.write('bacula_download_dir="%s"\n' % (obj.download_dir, ))

            bacula_flags = ""
            for value in advanced_settings.values():
                bacula_flags += value + " "
            f.write('bacula_flags="%s"\n' % (bacula_flags, ))

        try:
            user_ids = pwd.getpwnam("bacula")[2:4]
        except:
            user_ids = None

        os.system(os.path.join(utils.bacula_pbi_path, "tweak-rcconf"))
        """
        return obj

    class Meta:
        model = models.BaculaSDStorage
        widgets = {
            'baculasd_st_sdport': forms.widgets.TextInput(),
        }
        exclude = (
            'enable',
            )


class BaculaSDDirectorForm(forms.ModelForm):

    def save(self):
        obj = super(BaculaSDDirectorForm, self).save()
        #started = notifier().reload("baculasd")
        #if started is False and models.services.objects.get(srv_service = 'baculasd').srv_enable:
        #    raise ServiceFailed("baculasd", _("The Bacula Storage Daemon failed to reload."))
        return obj

    class Meta:
        model = models.BaculaSDDirector


class BaculaSDDeviceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.jail = kwargs.pop('jail')
        super(BaculaSDDeviceForm, self).__init__(*args, **kwargs)

        self.fields['baculasd_dev_archivedevice'].widget = forms.widgets.TextInput(attrs={
            'data-dojo-type': 'freeadmin.form.PathSelector',
            'root': os.path.join(
                self.jail['fields']['jail_path'],
                self.jail['fields']['jail_name'],
                #self.plugin['fields']['plugin_path'][1:],
                ),
            'dirsonly': 'false',
            })

    def save(self):
        super(BaculaSDDeviceForm, self).save()
        #started = notifier().reload("baculasd")
        #if started is False and models.services.objects.get(srv_service = 'baculasd').srv_enable:
        #    raise ServiceFailed("baculasd", _("The Bacula Storage Daemon failed to reload."))

    class Meta:
        model = models.BaculaSDDevice
        widgets = {
            'baculasd_dev_mediatype': forms.widgets.FilteringSelect(),
        }


class BaculaSDMessagesForm(forms.ModelForm):

    def clean_baculasd_msg_address(self):
        address = self.cleaned_data.get("baculasd_msg_address")
        destination = self.cleaned_data.get("baculasd_msg_destination")
        if destination == 'stdout':
            address = ""
        elif destination == 'stderr':
            return ""
        elif destination == 'console':
            return ""
        elif destination == 'syslog':
            return ""
        elif destination == 'director':
            return 'bacula-dir'
        else:
            return address

    def clean_baculasd_msg_msgtypeaux(self):
        msgtypeaux = self.cleaned_data.get("baculasd_msg_msgtypeaux")
        if msgtypeaux.startswith('#'):
            return ""
        else:
            return msgtypeaux

    def save(self):
        super(BaculaSDMessagesForm, self).save()
        #started = notifier().reload("baculasd")
        #if started is False and models.services.objects.get(srv_service = 'baculasd').srv_enable:
        #    raise ServiceFailed("baculasd", _("The Bacula Storage Daemon failed to reload."))

    class Meta:
        model = models.BaculaSDMessages


class BaculaSDDeviceAssignmentForm(forms.ModelForm):

    def save(self):
        super(BaculaSDDeviceAssignmentForm, self).save()
        #started = notifier().reload("baculasd")
        #if started is False and models.services.objects.get(srv_service = 'baculasd').srv_enable:
        #    raise ServiceFailed("baculasd", _("The Bacula Storage Daemon failed to reload."))

    class Meta:
        model = models.BaculaSDDeviceAssignment


class BaculaSDDirectorAssignmentForm(forms.ModelForm):

    def save(self):
        super(BaculaSDDirectorAssignmentForm, self).save()
        #started = notifier().reload("baculasd")
        #if started is False and models.services.objects.get(srv_service = 'baculasd').srv_enable:
        #    raise ServiceFailed("baculasd", _("The Bacula Storage Daemon failed to reload."))

    class Meta:
        model = models.BaculaSDDirectorAssignment


class BaculaSDMessagesAssignmentForm(forms.ModelForm):

    def save(self):
        super(BaculaSDMessagesAssignmentForm, self).save()
        #started = notifier().reload("baculasd")
        #if started is False and models.services.objects.get(srv_service = 'baculasd').srv_enable:
        #    raise ServiceFailed("baculasd", _("The Bacula Storage Daemon failed to reload."))

    class Meta:
        model = models.BaculaSDMessagesAssignment
