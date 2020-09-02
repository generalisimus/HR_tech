from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, loader
from django.forms import modelformset_factory
from django.urls import reverse_lazy, reverse
from .models import *
from django.views.generic import CreateView, ListView
from . forms import QuestionForm, AnswerForm
from question.models import UserProfile
from django.views.generic import FormView, DetailView
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth import login, authenticate  
from question.forms import ProfileCreationForm, PollForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.forms import formset_factory  
from django.db.models import Sum, Max, Min
from django.db.models import Q
from django.shortcuts import redirect
import datetime
import time

#Регистация
	
class RegisterView(FormView):
	form_class = UserCreationForm  

	def form_valid(self, form):  
		form.save()  
		username = form.cleaned_data.get('username')  
		raw_password = form.cleaned_data.get('password1')  
		login(self.request, authenticate(username=username, password=raw_password))  
		return super(RegisterView, self).form_valid(form)

class CreateUserProfile(FormView):  
  
	form_class = ProfileCreationForm  
	template_name = 'profile-create.html'  
	success_url = reverse_lazy('question:base')  

	def dispatch(self, request, *args, **kwargs):  
		if self.request.user.is_anonymous:  
			return HttpResponseRedirect(reverse_lazy('question:login'))  
		return super(CreateUserProfile, self).dispatch(request, *args, **kwargs)  

	def form_valid(self, form):  
		instance = form.save(commit=False)  
		instance.user = self.request.user  
		instance.save()  
		return super(CreateUserProfile, self).form_valid(form)


#Создаем опрос 
@user_passes_test(lambda user: user.is_staff)
def poll(request):
	PollFormSet = modelformset_factory(Poll, fields=('title', 'data_publish', 'is_active', 'timer'))
	date = datetime.date.today()
	if request.method == 'POST':
		form = PollFormSet(request.POST)
		if form.is_valid():
			for instanse in form:
				instanse.save()
			return HttpResponseRedirect(reverse_lazy('question:question_create'))
	else:
		form = PollFormSet(queryset=Poll.objects.none())
	return render(request, 'create_poll/index.html', {'form' : form, 'date': date })

#Создаем вопрос 
def question_create(request):
	QuestionFormSet = formset_factory(QuestionForm, extra=1)
	date = datetime.date.today()
	count = 0
	if request.method == 'POST':
		count = request.POST['question'] #Вводим кол-во ответов на вопрос.
		question_formset = QuestionFormSet(request.POST, request.FILES, prefix='question')
		if question_formset.is_valid():
			if 'images' in request.FILES:
				question_formset.images = request.FILEX['images']
				question_formset.save(commit=True)
			for question_form in question_formset:
				question_form.save()
			return HttpResponseRedirect(reverse_lazy('question:answer_create', args=(count,)))			
		
	else:
		question_formset = QuestionFormSet(prefix='question')
	return render(request, 'create_poll/question_create.html', { 'date': date, 'question_formset': question_formset })

#Создаем ответы на вопрос
def answer_create(request, count):
	count = count
	date = datetime.date.today()
	question = Question.objects.last()
	AnswerFormSet = formset_factory(AnswerForm, extra = count)
	if request.method == 'POST' and request.POST.get('question'):
		answer_formset = AnswerFormSet(request.POST, request.FILES, prefix='answer')
		if answer_formset.is_valid():
			for answer_form in answer_formset:
				if answer_form =='':
					return HttpResponse('ok')
				answer_form.save()
			return HttpResponseRedirect(reverse_lazy('question:base'))
	else:
		answer_formset = AnswerFormSet(prefix='answer')
	return render(request, 'create_poll/answer_create.html', { 'date': date, 'answer_formset': answer_formset})


#Начальная страница
def base(request):
	poll = Poll.objects.all().order_by('id')
	date = datetime.date.today()
	

	return render(request, 'base.html', context={'poll':poll, 'date': date,})


#Страница выбора опроса пользователем
def answer_poll(request):	

	poll_timer_start = Poll.objects.all()
	date_now = time.time()

	list_following_poll = []
	q = str()
	

	for i in poll_timer_start:
		if i.is_active == False and date_now > i.data_publish.timestamp():
			q = Poll.objects.get(title__iexact=i.title)
	if q:
		q.is_active = True
		q.save()

	for i in poll_timer_start:
		if date_now < i.data_publish.timestamp():
			list_following_poll.append(i.title)
	
	if list_following_poll:		
		sorted_following_poll = sorted(list_following_poll)
		first_following_poll = sorted_following_poll[0]

		following_poll = Poll.objects.get(title__iexact=first_following_poll)
		following_poll_time = Poll.objects.get(title__iexact=first_following_poll).data_publish.timestamp() 
			
	
	template = loader.get_template('answer/answer_poll.html')
	questions = Question.objects.all()
	answers = Answer.objects.all()
	result = ResultsAll.objects.filter(id_user=request.user.id)
	res = [x for x in result]
	polls = Poll.objects.all().exclude(title__in=res).exclude(is_active=False)
	poll_first = polls.first()
	question = Question.objects.filter(name__in=polls).first()
	results_all = ResultsAll.objects.last()
	date = datetime.date.today()

	data = {
		'polls': polls,
		'q': q,
		'date': date,
		'poll_first': poll_first,
		'question': question,
		'results_all': results_all,
		'results': results,
		'res': res,
		'result': result,
		'polls': polls,
		'questions': questions,
		'answers': answers,
	}
	return HttpResponse(template.render(data, request))


#Страница ответов и расчета времени
def answer_question(request, pk):
	
	template = loader.get_template('answer/answer_question.html')
	question = Question.objects.get(pk=pk)
	polls = Poll.objects.get(title=question.name)
	questions = Question.objects.filter(name=polls)
	date = datetime.date.today()		
	if polls.timer:		
		i = []
		for q in questions:
			i.append(q.timer_start)
		sum_time = sum(i)
		a = sum_time * 0.75
		minutes = round(a) // 60
		second = round(a) % 60

		data = {
			'minutes': round(minutes),
			'second': round(second),
#			'sum_time': sum_time,
			'date': date,
			'polls': polls,
			'question': question,
			'questions': questions

		}
		return HttpResponse(template.render(data, request))
	else:		
		data = {
			'date': date,
			'polls': polls,
			'question': question,
			'questions': questions

		}
		return HttpResponse(template.render(data, request))
	return HttpResponse(template.render(data, request))



#Сохранение результатов на каждый вопрос

def points(request, question_id):
	result = Results.objects.filter(id_user=request.user.id)
	question = Question.objects.get(id=question_id)
	poll = Poll.objects.get(title=question.name)
	questions = Question.objects.filter(name=poll)
	count = 0
	list_result = []
	for i in result:
		list_result.append(i.question_total)
	if question.id in list_result:
		context={
			'error': ' Вы пытались ответить дважды' '\n'
					'обратитесь к администратору'

		}
		return render(request, 'error.html', context)

	question_list_id = []
	for i in questions:
		question_list_id.append(i.id)
	
	if request.method == 'POST' and question.question_type == 'radio':
		if request.POST.get('answer') and question_id in question_list_id: 
			Results.objects.all().create(total = request.POST['answer'],
							name_user = request.user,
							id_user = request.user.id,
							question_total = question.title, 
							poll_total = poll.title
			)			
			question_id = question_id
			while question_id <= question_list_id[-1]:
				question_id += 1
				if question_id in question_list_id:
					return HttpResponseRedirect(reverse('question:answer_question', args=(question_id,)))
				elif question_id > question_list_id[-1]:
					return HttpResponseRedirect(reverse('question:save', args=(poll.id,)))					
				else:
					continue
	elif request.method == 'POST' and question.question_type == 'checkbox':
		if request.POST.get('answer') and question_id in question_list_id:		
			answer_server = request.POST.getlist('answer')
			question_check = []
			for i in answer_server:
				question_check.append(int(i))
			sum_question = sum(question_check)

			Results.objects.all().create(total = sum_question,
							name_user = request.user,
							id_user = request.user.id,
							question_total = question.title, 
							poll_total = poll.title
			)

			question_id = question_id
			while question_id <= question_list_id[-1]:
				question_id += 1
				if question_id in question_list_id:
					return HttpResponseRedirect(reverse('question:answer_question', args=(question_id,)))
				elif question_id > question_list_id[-1]:
					return HttpResponseRedirect(reverse('question:save', args=(poll.id,)))		
				else:
					continue

	else:
		return HttpResponseRedirect(reverse('question:answer_question', args=(question.id,)))
	
	return HttpResponseRedirect(reverse('question:answer_question', args=(question_id,)))


#Сохранение общих результатов на опрос

def save(request, pk):
	template = loader.get_template('result/results.html')
	polls = Poll.objects.filter(pk=pk)
	polls_in = Poll.objects.get(pk=pk)
	questions = Question.objects.filter(name__in=polls)
	questions_count = questions.count()
	results = Results.objects.only('request.user.id').order_by('-id')[:questions_count]
	total_sum = results.aggregate(Sum('total'))['total__sum']
	if request.method == "GET":
		ResultsAll.objects.all().create(name = request.user,
								id_user = request.user.id,
								poll_total = polls_in.title,
								total = total_sum
		)
		a = HttpResponseRedirect(reverse('question:results', args=(polls_in.id,)))
	return a



#Вывод рузультата прохождения опроса пользователем

def results(request, poll_id):
	template = loader.get_template('result/results.html')
	polls = Poll.objects.filter(id=poll_id)
	poll = Poll.objects.get(id=poll_id)
	results = ResultsAll.objects.filter(poll_total=poll.title)
	user = UserProfile.objects.all()
	res_user = ResultsAll.objects.filter(poll_total=poll.title).count()
	
	questions = Question.objects.filter(name__in=polls).count()
	users = request.user
	date = datetime.date.today()
	
	result_user = ResultsAll.objects.filter(poll_total=poll.title).get(id_user=users.id)

	result_procent = []
	for r in results:
		result_procent.append(r.total)
	repeat = 0
	while True:
		if result_user.total in result_procent:
			result_procent.remove(result_user.total)
			repeat += 1
		elif result_user not in result_procent:
			result_procent.append(result_user.total)
			repeat -= 1
			break
	result_procent = sorted(result_procent)
	res = result_procent.index(result_user.total) + 1
	result_procent_user = 100 - (res * 100 // len(result_procent))

	poll_question = Question.objects.filter(name__in=polls)
	poll_answer = Answer.objects.filter(question__in=poll_question)
	data = {
		'date': date,
		'res_user': res_user,
		'user': user,
		'result_user': result_user,
		'repeat': repeat,
		'result_procent': result_procent,
		'result_procent_user': result_procent_user,
		'poll': poll,
		'users': users,
	}
	return HttpResponse(template.render(data, request))

#Вывод результата для администратора.
def result_admin(request):
	template = loader.get_template('result/result_admin.html')
	search_query = request.GET.get('search', '')
	search_user = request.GET.get('search_user', '')
	search_question = request.GET.get('search_accurate', '')
	result_max = ResultsAll.objects.all().order_by('poll_total', '-total')

	if search_query:
		result = ResultsAll.objects.filter(Q(name__icontains=search_query) |
				 Q(poll_total__icontains=search_query)).order_by('poll_total', '-total')
			
	else:
		result = ResultsAll.objects.all().order_by('poll_total', '-total')[:20]
	
	user = request.user
	users = UserProfile.objects.all()


	
	data = {
		'result_max': result_max,
		'users': users,
		'user': user,                                              
		'result': result,
	}
	return HttpResponse(template.render(data))
