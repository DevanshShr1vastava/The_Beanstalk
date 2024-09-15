from collections import defaultdict
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import questionBank,QuestionPapers,userAttempts, UserProfile
# from django.contrib.auth.models import User
import pandas as pd
import numpy as np
from django.utils import timezone
from datetime import timedelta
from eva01.generateQP import generateQIDS,analyse_usr
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, UserForm, UserProfileForm

# Create your views here.
time_global = 30*60
@login_required
def hyoka(request, qpID, qID):
    
    if request.session.get('test_state') != 'in_progress':
        return redirect('home')  # Redirect if no active test
    
    if request.user.is_authenticated:
        user_id = request.user.id
        username = request.user.username
    #fetch the question
    question = questionBank.objects.filter(qID=qID).first()
    current_QP = QuestionPapers.objects.filter(qpID=qpID, qID=qID,userID = user_id).first()

    # Get the total number of questions in the paper
    total_questions = QuestionPapers.objects.filter(qpID=qpID, userID = user_id).count()

    # Get the number of questions already attempted by the user
    questions_completed = userAttempts.objects.filter(userID = user_id, qpID__qpID=qpID).count()
    
    progress = total_questions-questions_completed
  

    progress_percent = 100 - round(((progress - 1) / total_questions) * 100)
    
    if not question:
        return redirect('home') #if question is not found, redirect to home
    
    if(request.method == "POST"):
        attemptInfo = request.POST
        
        if(int(attemptInfo.get('usrAnswer'))==int(question.option_number)):
            usr_ans = 1
            
        else:
            usr_ans = 0
        
        # print(usr_ans)

        user_attempt = userAttempts(
            userID = request.user,
            qpID = current_QP,
            qID = question,
            answer = usr_ans,
            marked_for_review = attemptInfo.get('mFr'),
            time_taken = attemptInfo.get('TT')
        )
        user_attempt.save()

        #now checking whether current question is the last question in the question paper
        last_question_id = QuestionPapers.objects.filter(qpID = qpID).order_by('qpID').last().qID

        if(qID == last_question_id):
            request.session['test_state'] = 'completed'
            return redirect('test_complete_page/')
        else:
            #Get the next question in the paper

            cur_qp = QuestionPapers.objects.filter(userID = user_id, qpID = qpID, qID=qID).first()
            next_qp = QuestionPapers.objects.filter(userID = user_id,qpID=qpID, pk__gt=cur_qp.pk).order_by('pk').first()
            if(next_qp is None):
                request.session['test_state'] = 'completed'
                return redirect('test_complete_page')
            else:
                next_qID = next_qp.qID.qID
                return redirect('hyoka',qpID=qpID, qID=next_qID)
    
    return render(request,'hyoka.html',{'question':question,"timer":time_global,"progress":progress_percent,"total_questions":total_questions})

@login_required
def arena(request):
    QB = pd.DataFrame(questionBank.objects.all().values())

    if request.user.is_authenticated:
        user_id = request.user.id
        username = request.user.username
    
    questionPaper = generateQIDS(QB)
    
    if QuestionPapers.objects.filter(userID = user_id).exists():
        newQPid = QuestionPapers.objects.filter(userID=user_id).order_by('qpID').last().qpID + 1
    else:
        newQPid = 1
    
    for question in questionPaper:
        question_obj = questionBank.objects.get(qID=question) #fetching the question object
        paper_question = QuestionPapers(
            userID = request.user,
            qpID=newQPid,
            qID=question_obj #saving question object in the QuestionPapers model
        )
        paper_question.save()

    first_qp = QuestionPapers.objects.filter(qpID=newQPid, userID = user_id).first()
    firstQID = first_qp.qID.qID if first_qp else None # Fetch the qID of the first question
    
    if request.method == "POST":
        # Set session variables consistently before redirecting
        request.session['test_state'] = 'in_progress'
        request.session['test_qpID'] = newQPid
        request.session['test_start_time'] = timezone.now().timestamp()
        request.session['test_duration'] = time_global  # 30 minutes in seconds
        return redirect('hyoka', qpID=newQPid, qID=firstQID)
    
    return render(request, "arenaMain.html")

@login_required
def analyse(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        username = request.user.username
    
    usratmpts = pd.DataFrame(userAttempts.objects.filter(userID = user_id).values()).groupby('qID_id').agg(
            attempts=('answer',list),
            marked_for_review = ('marked_for_review','first'),
            time_taken=('time_taken','first'),
            answer = ('answer','first')
        ).reset_index()
    

    # print(usratmpts)


    analysis_result = analyse_usr(usratmpts)

    # print(analysis_result['subdomain'].to_list())
    # print(analysis_result['category_encoded'].to_list())

    weight_dict = dict(zip(analysis_result['subdomain'].to_list(),analysis_result['category_encoded'].to_list()))
    
    # print(type(weight_dict))

    QB = pd.DataFrame(questionBank.objects.all().values())
    new_QIDS_non_weighted = generateQIDS(QB)
    new_QIDS = generateQIDS(QB,weight_dict)
   
    print("New QIDS unweighted")
    print(new_QIDS_non_weighted)
    print("New QIDS weighted")
    print(new_QIDS)

    return render(request, "analysis.html")

def home(request):
    if request.session.get('test_state') == 'in_progress':
        qpID = request.session.get('test_qpID')
        qID = QuestionPapers.objects.filter(qpID=qpID).first().qID
        return redirect('hyoka', qpID=qpID, qID=qID)
     
    return render(request, "home.html")

@login_required
def test_complete_page(request):
    
    return render(request,"test_complete_page.html")

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/register.html', {'form': form})
        
def user_login(request):
    if request.method =='POST':
        form = AuthenticationForm(request, data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('newHome')
    else:
        form = AuthenticationForm()
    return render(request,'accounts/login.html',{'form':form})

def user_logout(request):
    logout(request)
    return redirect('/login')

def new_home(request):

    return render(request,"newHome.html")


@login_required
def profile_settings(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)  # Fetch or create UserProfile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile_settings')  # Stay on the same page after successful save
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=user_profile)

    return render(request, 'profile_settings.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })