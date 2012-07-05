from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('baculaUI.freenas.views',
     url(r'^edit$', 'edit', name="bacula_edit"),
     url(r'^devices/$', 'devices_view', name="bacula_devices_view"),
     url(r'^devices/new/$', 'devices_new', name="bacula_devices_new"),
     url(r'^devices/edit/(?P<oid>\d+)/$', 'devices_edit', name="bacula_devices_edit"),
     url(r'^directors/$', 'directors_view', name="bacula_directors_view"),
     url(r'^directors/new/$', 'directors_new', name="bacula_directors_new"),
     url(r'^directors/edit/(?P<oid>\d+)/$', 'directors_edit', name="bacula_directors_edit"),
     url(r'^treemenu-icon$', 'treemenu_icon', name="treemenu_icon"),
     url(r'^_s/treemenu$', 'treemenu', name="treemenu"),
     url(r'^_s/start$', 'start', name="start"),
     url(r'^_s/stop$', 'stop', name="stop"),
     url(r'^_s/status$', 'status', name="status"),
)
