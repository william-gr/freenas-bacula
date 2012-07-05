import hashlib
import json
import os
import pwd
import urllib

from django.utils.translation import ugettext_lazy as _

from dojango import forms
from baculaUI.freenas import models, utils


class BaculaForm(forms.ModelForm):

    class Meta:
        model = models.Bacula
        widgets = {
            'rpc_port': forms.widgets.TextInput(),
        }
        exclude = (
            'enable',
            )

    def __init__(self, *args, **kwargs):
        self.jail = kwargs.pop('jail')
        super(BaculaForm, self).__init__(*args, **kwargs)

        self.fields['logfile'].widget = forms.widgets.TextInput(attrs={
            'data-dojo-type': 'freeadmin.form.PathSelector',
            'root': os.path.join(
                self.jail['fields']['jail_path'],
                self.jail['fields']['jail_name'],
                #self.plugin['fields']['plugin_path'][1:],
                ),
            'dirsonly': 'false',
            })

        self.fields['conf_dir'].widget = \
        self.fields['download_dir'].widget = \
        self.fields['watch_dir'].widget = forms.widgets.TextInput(attrs={
            'data-dojo-type': 'freeadmin.form.PathSelector',
            'root': os.path.join(
                self.jail['fields']['jail_path'],
                self.jail['fields']['jail_name'],
                #self.plugin['fields']['plugin_path'][1:],
                ),
            'dirsonly': 'true',
            })

    def clean_rpc_password(self):
        rpc_password = self.cleaned_data.get("rpc_password")
        if not rpc_password:
            return self.instance.rpc_password
        return rpc_password

    def save(self, *args, **kwargs):
        obj = super(BaculaForm, self).save(*args, **kwargs)

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

        if obj.watch_dir:
            try:
                os.chmod(obj.watch_dir, 0o755)
                if user_ids:
                    os.chown(obj.watch_dir, *user_ids)
            except:
                pass

        if not os.path.exists(obj.conf_dir):
            try:
                os.makedirs(obj.conf_dir)
            except OSError:
                pass

        try:
            os.chmod(obj.conf_dir, 0o755)
            if user_ids:
                os.chown(obj.conf_dir, *user_ids)
        except:
            pass

        if obj.download_dir:
            try:
                os.chmod(obj.download_dir, 0o755)
                if user_ids:
                    os.chown(obj.download_dir, *user_ids)
            except:
                pass

        settingsfile = os.path.join(obj.conf_dir, "settings.json")
        if os.path.exists(settingsfile):
            with open(settingsfile, 'r') as f:
                settings = json.loads(f.read())
        else:
            try:
                open(settingsfile, 'w').close()
            except OSError:
                #FIXME
                pass
            settings = {}

        if obj.rpc_password:
            settings['rpc-password'] = '{' + hashlib.sha1(obj.rpc_password).hexdigest()
        with open(settingsfile, 'w') as f:
            f.write(json.dumps(settings, sort_keys=True, indent=4))

        os.system(os.path.join(utils.bacula_pbi_path, "tweak-rcconf"))
