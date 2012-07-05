from django.utils.translation import ugettext_lazy as _


BACULASD_DEV_MEDIATYPE_CHOICES = (
    ('File', _('File')),
#    ('Tape', _('Tape')),
#    ('Fifo',  _('Fifo')),
#    ('DVD',  _('DVD')),
    )

BACULASD_MSG_DESTINATION_CHOICES = (
    ('director', _('Director')),
    ('file', _('File')),
    ('append', _('Append file')),
    ('syslog', _('Syslog')),
    ('mail', _('Email per job')),
    ('mail on error', _('Email on job error')),
    ('mail on success', _('Email on job success')),
    ('operator', _('Email per message')),
    ('console', _('Console')),
    ('stdout', _('Standard output')),
    ('stderr', _('Standard error')),
    ('catalog', _('Catalog database')),
    )

BACULASD_MSG_MSGTYPE_CHOICES = (
    ('info', _('General information messages')),
    ('warning', _('Warning messages')),
    ('error', _('Non-fatal error messages')),
    ('fatal', _('Fatal error messages')),
    ('terminate', _('Message generated when the daemon shuts down')),
    ('notsaved', _('Files not saved because of some error')),
    ('skipped',
        _('Files that were skipped because of a user supplied option')),
    ('mount', _('Volume mount or intervention requests')),
    ('restored', _('Listing for each file restored')),
    ('all', _('All message types')),
    ('security', _('Security info/warning messages')),
    ('alert', _('Alert messages')),
    ('volmgmt', _('Volume management messages')),
    ('!info', _('Not general information messages')),
    ('!warning', _('Not warning messages')),
    ('!error', _('Not non-fatal error messages')),
    ('!fatal', _('Not fatal error messages')),
    ('!terminate', _('Not message generated when the daemon shuts down')),
    ('!notsaved', _('Not files not saved because of some error')),
    ('!skipped',
        _('Not files that were skipped because of a user supplied option')),
    ('!mount',  _('Not volume mount or intervention requests')),
    ('!restored',  _('Not listing for each file restored')),
    ('!security',  _('Not security info/warning messages')),
    ('!alert',  _('Not alert messages')),
    ('!volmgmt',  _('Not volume management messages')),
    )
