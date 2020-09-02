from django.contrib import admin

from question.models import *
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
	list_display = ['title', 'id', 'is_active', 'timer']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	search_fields = ['title']
	inlines = [AnswerInline]
	list_display = ['title', 'id', 'name']
	#date_hierarchy = ('data_publish')

@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
	pass

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
	pass

@admin.register(ResultsAll)
class ResultAllAdmin(admin.ModelAdmin):
	model = ResultsAll
	list_display = ['name', 'id_user', 'poll_total', 'total']
	list_filter = ['poll_total']
	search_fields = ['name']