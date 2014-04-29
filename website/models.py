from django.db import models

from django.contrib.auth.models import User

class Meme(models.Model):
	author = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)
	title = models.CharField(max_length=60)
	picture = models.ImageField(upload_to='memes/')
	up_vote_count = models.IntegerField(default=0)
	down_vote_count = models.IntegerField(default=0)

	def __unicode__(self):
		string = (
			'Meme(id=%d, title=%s, date=%s, up_vote=%d, down_vote=%d)'
			% (self.id, self.title, self.date, self.up_vote_count, self.down_vote_count)
		)

		return string

	@staticmethod
	def get_memes(author=None):
		if author is None:
			return Meme.objects.all().order_by('-date')

		return Meme.objects.filter(author=author).order_by('-date')
	
class Vote(models.Model):
	UP = 1
	DOWN = -1
	NONE = 0
	meme = models.ForeignKey(Meme)
	owner = models.ForeignKey(User)
	value = models.IntegerField()

	class Meta:
		unique_together = ('meme', 'owner')

	def __unicode__(self):
		string = (
			'Vote(id=%d, meme=%d, owner=%s, value=%d)'
			% (self.id, self.meme.id, self.owner.username, self.value)
		)

		return string

