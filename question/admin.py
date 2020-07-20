from django.contrib import admin

from question.models import Question, Poll, UserProfile, Answer
from django.contrib.auth.models import User




class QuestionInline(admin.TabularInline):
	model = Question
	fields = ['title', 'id']
	extra = 2
	
class AnswerInline(admin.TabularInline):
	model = Answer
	field = ['answer', 'point']
	exetra = 2

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
	model = Poll
	list_display = ['title', 'id', 'is_active']
	inlines = [QuestionInline]
	pass
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	search_fields = ['title']
	inlines = [AnswerInline]
	list_display = ['title', 'id']
	#date_hierarchy = ('data_publish')

@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
	pass

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
	pass