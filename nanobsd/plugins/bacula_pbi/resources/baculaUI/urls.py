from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
     url(r'^plugins/bacula-sd/(?P<plugin_id>\d+)/', include('baculaUI.freenas.urls')),
)
