from django import forms 
from question.models import UserProfile, Poll, Question, Answer

class ProfileCreationForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ['user']

class PollForm(forms.ModelForm):
	class Meta:
		model = Poll
		fields = ['title', 'data_publish', 'is_active' ]


class QuestionForm(forms.ModelForm):
	class Meta:
		model = Question
		fields =  ['name', 'title', 'question_type', 'images', 'timer_start']


class AnswerForm(forms.ModelForm):
	class Meta:
		model = Answer
		fields = ['answer', 'point',]

