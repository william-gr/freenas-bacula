from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
     url(r'^plugins/bacula-server/', include('baculaUI.freenas.urls')),
)
