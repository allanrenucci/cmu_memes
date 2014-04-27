from django.conf.urls import patterns, url

urlpatterns = patterns('website.views',
	url(r'^register/$', 'register', name='register'),
	url(r'^$', 'home', name='home'),
	url(r'^profile/$', 'profile', name='profile'),
	url(r'^profile/update/$', 'update_profile', name='update profile'),
	url(r'^profile/set-password/$', 'set_password', name='set password'),
	url(r'^profile/delete/$', 'delete_profile', name='delete profile'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout_then_login', name='logout'),
)