from django.conf.urls import patterns, url

urlpatterns = patterns('website.views',
	url(r'^register/$', 'register', name='register'),
	url(r'^$', 'home', name='home'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout_then_login', name='logout'),
)