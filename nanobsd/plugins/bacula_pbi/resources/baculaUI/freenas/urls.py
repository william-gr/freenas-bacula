import os

from django.conf.urls.defaults import patterns, url
from django.views.static import serve

HERE = os.path.abspath(os.path.dirname(__file__))

def servewrapper(request, plugin_id, **kwargs):
     return serve(request, **kwargs)

urlpatterns = patterns('baculaUI.freenas.views',
     url(r'^edit$', 'edit', name="bacula_edit"),
     url(r'^devices/$', 'devices_view', name="bacula_devices_view"),
     url(r'^devices/new/$', 'devices_new', name="bacula_devices_new"),
     url(r'^devices/edit/(?P<oid>\d+)/$', 'devices_edit', name="bacula_devices_edit"),
     url(r'^devices/delete/(?P<oid>\d+)/$', 'devices_delete', name="bacula_devices_delete"),
     url(r'^deviceassigns/$', 'deviceassigns_view', name="bacula_deviceassigns_view"),
     url(r'^deviceassigns/new/$', 'deviceassigns_new', name="bacula_deviceassigns_new"),
     url(r'^deviceassigns/edit/(?P<oid>\d+)/$', 'deviceassigns_edit', name="bacula_deviceassigns_edit"),
     url(r'^deviceassigns/delete/(?P<oid>\d+)/$', 'deviceassigns_delete', name="bacula_deviceassigns_delete"),
     url(r'^directors/$', 'directors_view', name="bacula_directors_view"),
     url(r'^directors/new/$', 'directors_new', name="bacula_directors_new"),
     url(r'^directors/edit/(?P<oid>\d+)/$', 'directors_edit', name="bacula_directors_edit"),
     url(r'^directors/delete/(?P<oid>\d+)/$', 'directors_delete', name="bacula_directors_delete"),
     url(r'^directorassigns/$', 'directorassigns_view', name="bacula_directorassigns_view"),
     url(r'^directorassigns/new/$', 'directorassigns_new', name="bacula_directorassigns_new"),
     url(r'^directorassigns/edit/(?P<oid>\d+)/$', 'directorassigns_edit', name="bacula_directorassigns_edit"),
     url(r'^directorassigns/delete/(?P<oid>\d+)/$', 'directorassigns_delete', name="bacula_directorassigns_delete"),
     url(r'^daemons/$', 'daemons_view', name="bacula_daemons_view"),
     url(r'^daemons/new/$', 'daemons_new', name="bacula_daemons_new"),
     url(r'^daemons/edit/(?P<oid>\d+)/$', 'daemons_edit', name="bacula_daemons_edit"),
     url(r'^daemons/delete/(?P<oid>\d+)/$', 'daemons_delete', name="bacula_daemons_delete"),
     url(r'^messages/$', 'messages_view', name="bacula_messages_view"),
     url(r'^messages/new/$', 'messages_new', name="bacula_messages_new"),
     url(r'^messages/edit/(?P<oid>\d+)/$', 'messages_edit', name="bacula_messages_edit"),
     url(r'^messages/delete/(?P<oid>\d+)/$', 'messages_delete', name="bacula_messages_delete"),
     url(r'^messagesassigns/$', 'messagesassigns_view', name="bacula_messagesassigns_view"),
     url(r'^messagesassigns/new/$', 'messagesassigns_new', name="bacula_messagesassigns_new"),
     url(r'^messagesassigns/edit/(?P<oid>\d+)/$', 'messagesassigns_edit', name="bacula_messagesassigns_edit"),
     url(r'^messagesassigns/delete/(?P<oid>\d+)/$', 'messagesassigns_delete', name="bacula_messagesassigns_delete"),
     url(r'^treemenu-icon$', 'treemenu_icon', name="treemenu_icon"),
     url(r'^media/(?P<path>.*)$', servewrapper, {
            'document_root': os.path.join(HERE, "static"),
        }, name="bacula_media"),
     url(r'^_s/treemenu$', 'treemenu', name="treemenu"),
     url(r'^_s/start$', 'start', name="start"),
     url(r'^_s/stop$', 'stop', name="stop"),
     url(r'^_s/status$', 'status', name="status"),
)
