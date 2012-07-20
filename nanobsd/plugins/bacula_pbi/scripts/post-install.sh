#!/bin/sh
#########################################

bacula_rc=/usr/local/bin/bacula-daemon
bacula_pbi_path=/usr/pbi/bacula-$(uname -m)/

mv ${bacula_pbi_path}/bacula /usr/local/etc/rc.d/

pw group add bacula
pw user add bacula -g bacula -d ${bacula_pbi_path}/etc/bacula/home

${bacula_pbi_path}/bin/python ${bacula_pbi_path}/baculaUI/manage.py syncdb --migrate --noinput
