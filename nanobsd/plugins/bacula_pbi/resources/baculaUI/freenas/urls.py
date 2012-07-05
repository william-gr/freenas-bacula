from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('baculaUI.freenas.views',
     url(r'^edit$', 'edit', name="bacula_edit"),
     url(r'^devices/new/$', 'devices_new', name="bacula_devices_new"),
     url(r'^devices/edit/(?P<oid>\d+)/$', 'devices_edit', name="bacula_devices_edit"),
     url(r'^treemenu-icon$', 'treemenu_icon', name="treemenu_icon"),
     url(r'^_s/treemenu$', 'treemenu', name="treemenu"),
     url(r'^_s/start$', 'start', name="start"),
     url(r'^_s/stop$', 'stop', name="stop"),
     url(r'^_s/status$', 'status', name="status"),
)
