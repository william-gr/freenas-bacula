#!/bin/sh
#########################################

bacula_pbi_path=/usr/pbi/bacula-sd-$(uname -m)/

cp ${bacula_pbi_path}/bacula ${bacula_pbi_path}/ix-bacula-sd /usr/local/etc/rc.d/

pw group add bacula
pw user add bacula -g bacula -d ${bacula_pbi_path}/etc/bacula/home

${bacula_pbi_path}/bin/python ${bacula_pbi_path}/baculaUI/manage.py syncdb --migrate --noinput
