from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView

from .views import *
from question import views


app_name = "question"

urlpatterns = [
#	path('',LoginView.as_view(template_name='base.html'), name='base'),
	path('', base, name='base'),
	path('poll', views.poll, name='poll_create'),
	#path('question', QuestionEdit.as_view(), name='question'),
	#path('answer', AnswerEdit.as_view(), name='answer'),
	path('question/create', question_create, name='question_create'),
	path('question_anwer/create/<int:count>/', answer_create, name='answer_create'),
	path('login/', LoginView.as_view(template_name='login.html'), name='login'),
	path('logout/', LogoutView.as_view(), name='logout'),
	path('register/', RegisterView.as_view(  
        template_name='register.html',
        success_url=reverse_lazy('question:base') 
    ), name='register'),  
	path('profile-create/', CreateUserProfile.as_view(), name='profile-create'),
	path('answer_poll', answer_poll, name='answer_poll'),
	path('answer_question/<int:pk>/save', save, name='save'),
	path('results/<int:poll_id>/', results, name='results'),
	path('result_admin', result_admin, name='result_admin'),
	path('points/<int:question_id>/', points, name="points"),
	path('answer_question/<int:pk>/', answer_question, name='answer_question'),
]