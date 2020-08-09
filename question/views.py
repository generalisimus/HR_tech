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

# class QuestionEdit(CreateView):
# 	model = Question
# 	form_class = QuestionForm
# 	success_url = reverse_lazy('question:answer')
# 	template_name = 'question.html'


# class AnswerEdit(CreateView):
# 	model = Answer
# 	form_class = AnswerForm 
# 	success_url = reverse_lazy('question:base')
# 	template_name = 'answer.html'


def question_create(request):
	QuestionFormSet = formset_factory(QuestionForm, extra=1)
	if request.method == 'POST':
		question_formset = QuestionFormSet(request.POST, request.FILES, prefix='question')
		if question_formset.is_valid():
			for question_form in question_formset:
				question_form.save()
			return HttpResponseRedirect(reverse_lazy('question:answer_create'))			
		
	else:
		question_formset = QuestionFormSet(prefix='question')
	return render(request, 'create_poll/question_create.html', {'question_formset': question_formset})



def answer_create(request):

	AnswerFormSet = formset_factory(AnswerForm, extra = 4)
	question = Question.objects.last()
	if request.method == 'POST':
		answer_formset = AnswerFormSet(request.POST, request.FILES, prefix='answer')
		if answer_formset.is_valid():
			for answer_form in answer_formset:
				answer_form.save()
			return HttpResponseRedirect(reverse_lazy('question:base'))

	else:
		answer_formset = AnswerFormSet(prefix='answer')
	return render(request, 'create_poll/answer_create.html', {'answer_formset': answer_formset})


# @login_required
def base(request):
    poll = Poll.objects.all().order_by('id')
    return render(request, 'base.html', context = {'poll': poll})

@user_passes_test(lambda user: user.is_staff)
def poll(request):
	PollFormSet = modelformset_factory(Poll, fields=('title', 'data_publish', 'is_active'))
	if request.method == 'POST':
		form = PollFormSet(request.POST)
		if form.is_valid():
			for instanse in form:
				instanse.save()
			return HttpResponseRedirect(reverse_lazy('question:question_create'))
	else:
		form = PollFormSet(queryset=Poll.objects.none())
	return render(request, 'create_poll/index.html', {'form' : form })

def answer_poll(request):
	template = loader.get_template('answer/answer_poll.html')
	questions = Question.objects.all()
	answers = Answer.objects.all()
	result = ResultsAll.objects.filter(id_user=request.user.id)
	res = [x for x in result]
	polls = Poll.objects.all().exclude(title__in=res).exclude(is_active=False)
	p = polls.first()
	question = Question.objects.filter(name__in=polls).first()
	r = ResultsAll.objects.last()
	data = {
		'p': p,
		'question': question,
		'r': r,
		'results': results,
		'res': res,
		'result': result,
		'polls': polls,
		'questions': questions,
		'answers': answers,
	}
	return HttpResponse(template.render(data, request))

# def answer_question(request, pk):
# 	res = []
# 	polls = Poll.objects.filter(pk=pk)
# 	template = loader.get_template('answer/answer_question.html')
# 	templates = loader.get_template('error.html')
# 	questions = Question.objects.filter(name__in=polls)
# 	question_count = questions.count()
# 	user = request.user

# 	poll = Poll.objects.get(id=pk)
# 	result = ResultsAll.objects.filter(id_user=request.user.id).only('poll_total')
# 	for r in result:
# 		res.append(r)

# 	data = {
# 		'poll': poll,
# 		'res': res,
# 		'result': result,
# 		'user': user,
# 		'question_count': question_count,
# 		'polls': polls,
# 		'questions': questions,
# 	}
# 	a = HttpResponse(template.render(data, request))
# 	for r in res:
# 		if r.poll_total in poll.title:
# 			a = HttpResponse(templates.render(context={'error': 'Вы уже проходили этот опрос'}))

# 	return a

def answer_question(request, pk):
	template = loader.get_template('answer/answer_question.html')
	question = Question.objects.get(pk=pk)
	polls = Poll.objects.get(title=question.name)
	questions = Question.objects.filter(name=polls)
	d = 11
	q = []
	for i in questions:
		q.append(i.id)
	data = {
		'd': d,
		'q': q,
		'polls': polls,
		'question': question,
		'questions': questions

	}

	return HttpResponse(template.render(data, request))

def points(request, question_id):
	question = Question.objects.get(id=question_id)
	poll = Poll.objects.get(title=question.name)
	questions = Question.objects.filter(name=poll)
	q = []
	for i in questions:
		q.append(i.id)
	
	
	if request.method == 'POST':
		question_id += 1

		if request.POST.get('answer') and question_id in q: 
			Results.objects.all().create(total = request.POST['answer'],
							name_user = request.user,
							id_user = request.user.id,
							question_total = question.title, 
							poll_total = poll.title
			)
			return HttpResponseRedirect(reverse('question:answer_question', args=(question_id,)))

		elif question_id not in q:
			return HttpResponseRedirect(reverse('question:save', args=(poll.id,)))


		else:
			return HttpResponseRedirect(reverse('question:answer_question', args=(question.id,)))
	
	return HttpResponseRedirect(reverse('question:answer_question', args=(question_id,)))




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
	# elif request.POST.get('total'):
	# 	ResultsAll.objects.all().create(name = request.user,
	# 							id_user = request.user.id,
	# 							poll_total = polls_in.title,
	# 							total = total_sum
	# 	)
	#	a = HttpResponseRedirect(reverse('question:results', args=(polls_in.id,)))
	return a


def results(request, poll_id):
	template = loader.get_template('result/results.html')
	polls = Poll.objects.filter(id=poll_id)
	poll = Poll.objects.get(id=poll_id)
	results = ResultsAll.objects.filter(poll_total=poll.title)
	user = UserProfile.objects.all()
	res_user = ResultsAll.objects.filter(poll_total=poll.title).count()
	
	questions = Question.objects.filter(name__in=polls).count()
	users = request.user
	
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

# Присвоить связной модели name в answer значение по умоланию далее с помощь Jquery организовать функцию clone
	#для всей формы  т.е клонирование осущ за счет создания формы полностью 

# при добавлениии опроса по умолчанию вопрос добавлять в только что созданный опрос (доделать)

# реализуем переход от radio к checkbox 


# добавляем детальное отображение результатов опроса

# При помощи JS:
#	1. При нажатии на кнопку конструктор опросов скрывать проверку на наличие непройденых опросов
#   2. Добавляе алерты при создании опроса и при ответах на вопросы а так же при регистрации 