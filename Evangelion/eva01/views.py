from collections import defaultdict
from django.forms import FloatField
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import questionBank,QuestionPapers,userAttempts, UserProfile
from django.db.models import Avg, Case, When, F, FloatField, ExpressionWrapper


# from django.contrib.auth.models import User
import pandas as pd
import numpy as np
from django.utils import timezone
from datetime import timedelta
from eva01.generateQP import generateQIDS,analyse_usr
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, UserForm, UserProfileForm, userSubjectSelectionForm
from django.db import models
from django.db.models import Avg, Max, Min, Count, Sum, Q
from django.shortcuts import render, get_object_or_404
from .models import Questions
import matplotlib.pyplot as plt
from django.db.models import Count
from io import BytesIO
import base64
from django.urls import reverse

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
        return redirect('newHome') #if question is not found, redirect to home
    
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
            return redirect(reverse('test_complete_page', kwargs={'test_id': qpID}))  # Ensure kwargs is passed correctly

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

    # to get the user and obtain corresponding data
    if request.user.is_authenticated:
        user_id = request.user.id
        username = request.user.username
    

    if QuestionPapers.objects.filter(userID = user_id).exists():
        # fetch all the user attempts and format it so that the model can work with it 

        usratmpts = pd.DataFrame(userAttempts.objects.filter(userID = user_id).values()).groupby('qID_id').agg(
            attempts=('answer',list),
            marked_for_review = ('marked_for_review','first'),
            time_taken=('time_taken','first'),
            answer = ('answer','first')
        ).reset_index()

        # pass the usrAttempt as the input for the topic classification model

        analysis_result = analyse_usr(usratmpts)

        # based on the classification, we obtain the weightage to be increased or deccreased and thus this new dictionary maps it accordingly 

        weight_dict = dict(zip(analysis_result['subdomain'].to_list(),analysis_result['category_encoded'].to_list()))

        # we generate a new questionpaper with the modified weights
        user_profile = UserProfile.objects.get(user=request.user)
        questionPaper = generateQIDS(QB,user_profile,weight_dict)

    else:

        #when there are no user attempts avaiable then that means a fresh new question paper must be generated without modified weights
        user_profile = UserProfile.objects.get(user=request.user)
        questionPaper = generateQIDS(QB,user_profile)
    
    
    #when confirmed that the test is being taken then only save it in the database
    if request.method == "POST":

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

        # Set session variables consistently before redirecting
        request.session['test_state'] = 'in_progress'
        request.session['test_qpID'] = newQPid
        request.session['test_start_time'] = timezone.now().timestamp()
        request.session['test_duration'] = time_global  # 30 minutes in seconds
        return redirect('hyoka', qpID=newQPid, qID=firstQID)
    
    return render(request, "arenaMain.html")

def home(request):
    if request.session.get('test_state') == 'in_progress':
        qpID = request.session.get('test_qpID')
        qID = QuestionPapers.objects.filter(qpID=qpID).first().qID
        return redirect('hyoka', qpID=qpID, qID=qID)
     
    return render(request, "home.html")


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('user_subjects')
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

    most_worked = (
        userAttempts.objects.filter(userID=request.user)
        .values('qID__subdomain')
        .annotate(subdomain_count=Count('qID__subdomain'))
        .order_by('-subdomain_count')
    )
    chart_subdomains = [item['qID__subdomain'] for item in most_worked]
    chart_counts = [item['subdomain_count'] for item in most_worked]

    focus_areas = (
        userAttempts.objects.filter(userID=request.user)
        .exclude(answer=F('qID__option_number'))  # Incorrect answers
        .values('qID__subdomain')
        .annotate(wrong_count=Count('qID__subdomain'))
        .order_by('-wrong_count')[:4]  # Top 4 areas
    )

    selected_subjects = request.user.userprofile.selected_subjects.all()


    return render(request,"newHome.html",{"DisplayData":{"most_worked":most_worked,"focus_areas": focus_areas, "selected_subjects":selected_subjects,"chart_subdomains":chart_subdomains,"chart_counts":chart_counts}})


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


@login_required
def user_subjects(request):

    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if(request.method == "POST"):
        form = userSubjectSelectionForm(request.POST, instance = profile)
        if form.is_valid():
            form.save()
            return redirect('newHome')
    else:
        form = userSubjectSelectionForm(instance = profile)

    return render(request,"subjects_select.html",{'form':form})


@login_required
def lifetime_accuracy(request):
    user_id = request.user
    subdomain_accuracy = (
        userAttempts.objects.filter(userID=request.user)
        .values('qID__subdomain')
        .annotate(
            accuracy=ExpressionWrapper(100*Avg(
                Case(
                    When(answer=F('qID__option_number'), then=1),
                    default=0,
                    output_field=FloatField()
                )
            ),output_field=FloatField()
),
            total_attempts=Count('id')
        )
    )
    
    # Fetch all user attempts
    total_attempts = userAttempts.objects.filter(userID=user_id).count()
    correct_attempts = userAttempts.objects.filter(userID=user_id, answer=1).count()

    # Calculate overall lifetime accuracy
    if total_attempts > 0:
        accuracy = (correct_attempts / total_attempts) * 100
    else:
        accuracy = 0

    # Prepare data for the accuracy graph
    # Group attempts by test papers to show accuracy for each test
    accuracy_data = (
        userAttempts.objects.filter(userID=user_id)
        .values('qpID__qpID')  # Group by test ID
        .annotate(
            total=Count('answer'),
            correct=Count('answer', filter=models.Q(answer=1))
        )
        .order_by('qpID__qpID')
    )
    
    # Prepare data for the graph
    labels = [f"Test {item['qpID__qpID']}" for item in accuracy_data]
    accuracy_scores = [
        round((item['correct'] / item['total']) * 100, 2) if item['total'] > 0 else 0 
        for item in accuracy_data
    ]

    # Prepare domain-wise accuracy data
    domain_data = (
        userAttempts.objects.filter(userID=user_id)
        .values('qID__domain')  # Group by domain name
        .annotate(
            total=Count('answer'),
            correct=Count('answer', filter=models.Q(answer=1))
        )
    )
    
    # Prepare domain list for the table
    domains_data = [
        {
            'domain_name': item['qID__domain'],
            'total_attempts': item['total'],
            'accuracy_percentage': round((item['correct'] / item['total']) * 100, 2) if item['total'] > 0 else 0
        }
        for item in domain_data
    ]

    context = {
        'total_attempts': total_attempts,
        'correct_attempts': correct_attempts,
        'accuracy': round(accuracy, 2),
        'labels': labels,
        'accuracy_scores': accuracy_scores,
        'domains_data': domains_data,  # Pass the domain-wise data
        'subdomains_data':subdomain_accuracy,
    }

    return render(request, 'stats.html', context)



@login_required
def test_complete_page(request):
    user = request.user

    # Retrieve the specific QuestionPaper instance by test_id
    test_qp = get_object_or_404(QuestionPapers)

    # Calculate the total and correct attempts for this specific test
    total_attempts = userAttempts.objects.filter(userID=user, qpID_id=test_qp).count()
    correct_attempts = userAttempts.objects.filter(userID=user, qpID=test_qp, answer=1).count()
    incorrect_attempts = total_attempts - correct_attempts
    review_count = userAttempts.objects.filter(userID=user, marked_for_review=1).count()

    # Prepare data for the pie chart
    labels = ['Correct', 'Incorrect']
    sizes = [correct_attempts, incorrect_attempts]
    colors = ['#4CAF50', '#FF5722']
    explode = (0.1, 0)  # explode the 'Correct' slice

    # Create pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title(f'Accuracy for {test_qp.name}')  # Title with the test name

    # Save the pie chart to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    # Context to pass to the template
    context = {
        'image_base64': image_base64,
        'total_attempts': total_attempts,
        'correct_attempts': correct_attempts,
        'incorrect_attempts': incorrect_attempts,
        'test_qp': test_qp,  # Pass test details to the template
    }

    return render(request, "test_complete_page.html", context)