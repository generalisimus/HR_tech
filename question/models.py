from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import reverse

#Создаем модель опроса
class Poll(models.Model):
	title = models.CharField(max_length=200, verbose_name='Опрос', blank=True, unique=True)
	data_publish = models.DateTimeField(verbose_name='дата публикации', default=timezone.now)
	is_active = models.BooleanField(verbose_name='опубликован')

	def get_absolute_url(self):
		return reverse('question:answer_question', kwargs={"pk": self.id})

	def __str__(self):
		return self.title


	class Meta:
		verbose_name = 'Опрос'
		verbose_name_plural = 'Опрос'

#Создаем модель вопроса
class Question(models.Model):
	name = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True, blank=True)
	title = models.CharField(max_length=500, verbose_name='Вопрос')
	images = models.ImageField(upload_to='media/%Y/%m/%d', default=None, blank=True)

	#is_active = models.BooleanField(verbose_name='опубликован')

	def get_absolute_url(self):
		return reverse('answer_question', kwargs={"pk": self.id})

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = 'Вопрос'
		verbose_name_plural = 'Вопросы'

#Создаем класс ответа
class Answer(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	answer = models.CharField(max_length=200, verbose_name='Ответ')
	point = models.IntegerField(verbose_name='балл', default=0)

	def __str__(self):
		return self.answer

	class Meta:
		verbose_name='Ответ'
		verbose_name_plural='Ответы'

class ResultsAll(models.Model):
	name = models.CharField(max_length=50,)
	id_user = models.IntegerField()
	poll_total = models.CharField(max_length=200)
	total = models.IntegerField(default=0)

	def __str__(self):
		return self.poll_total



class Results(models.Model):
	name_user = models.CharField(max_length=50,)
	question_total = models.CharField(max_length=200,)
	poll_total = models.CharField(max_length=200)
	total = models.IntegerField(default=0)



class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	poll = models.ManyToManyField(Poll, blank=True)



	class Meta:
		verbose_name='Пользователь'
		verbose_name_plural='Пользователи'

	def __str__(self):
		return self.user.username


