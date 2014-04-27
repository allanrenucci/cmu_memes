from django.db import models

from django.contrib.auth.models import User

class Meme(models.Model):
	author = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)
	title = models.CharField(max_length=60)
	picture = models.ImageField(upload_to='memes/')

	def __unicode__(self):
		return title

	@staticmethod
	def get_memes(author=None):
		if author is None:
			return Meme.objects.all().order_by('-date')

		return Meme.objects.filter(author=author).order_by('-date')
	
