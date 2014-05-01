from django.conf.urls import patterns, url

urlpatterns = patterns('website.views',
	url(r'^$', 'home', name='home'),
	url(r'^new/$', 'new', name='new'),
	url(r'^best/$', 'best', name='best'),
	
	url(r'^about/$', 'about', name='about'),

	url(r'^register/$', 'register', name='register'),
	url(r'^profile/$', 'profile', name='profile'),
	url(r'^profile/update/$', 'update_profile', name='update profile'),
	url(r'^profile/set-password/$', 'set_password', name='set password'),
	url(r'^profile/delete/$', 'delete_profile', name='delete profile'),

	url(r'^post/$', 'post_meme', name='post meme'),
	url(r'^delete/(?P<id>\d+)/$', 'delete_meme', name ='delete meme'),
	url(r'^upvote/(?P<id>\d+)/$', 'meme_upvote', name='meme upvote'),
	url(r'^downvote/(?P<id>\d+)/$', 'meme_downvote', name='meme downvote'),

	url(r'^picture/(?P<id>\d+)/$', 'get_picture', name='picture'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'extra_context':{'active':'login'}}, name='login'),
    url(r'^logout/$', 'logout_then_login', name='logout'),
)