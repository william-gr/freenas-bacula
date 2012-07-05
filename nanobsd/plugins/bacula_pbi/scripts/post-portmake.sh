#!/bin/sh
# PBI building script
# This will run after your port build is complete
##############################################################################

bacula_pbi_path=/usr/pbi/bacula-$(uname -m)/

find ${bacula_pbi_path}/lib -iname "*.py[co]" -delete
find ${bacula_pbi_path}/lib -iname "*.a" -delete
rm -rf ${bacula_pbi_path}/share/doc
rm -rf ${bacula_pbi_path}/share/emacs
rm -rf ${bacula_pbi_path}/share/examples
rm -rf ${bacula_pbi_path}/share/gettext
