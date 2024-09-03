from collections import defaultdict
from django.shortcuts import redirect, render
from .models import questionBank,QuestionPapers,userAttempts
import pandas as pd
import numpy as np
from django.utils import timezone
from datetime import timedelta
from eva01.generateQP import generateQIDS,analyse_usr
# Create your views here.
time_global = 30*60
def hyoka(request, qpID, qID):
    
    if request.session.get('test_state') != 'in_progress':
        return redirect('home')  # Redirect if no active test
    
    #fetch the question
    question = questionBank.objects.filter(qID=qID).first()
    current_QP = QuestionPapers.objects.filter(qpID=qpID, qID=qID).first()

      # Get the total number of questions in the paper
    total_questions = QuestionPapers.objects.filter(qpID=qpID).count()

    # Get the number of questions already attempted by the user
    questions_completed = userAttempts.objects.filter(qpID__qpID=qpID).count()
  
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
        
        print(usr_ans)
        user_attempt = userAttempts(
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

            cur_qp = QuestionPapers.objects.filter(qpID = qpID, qID=qID).first()
            next_qp = QuestionPapers.objects.filter(qpID=qpID, pk__gt=cur_qp.pk).order_by('pk').first()
            if(next_qp is None):
                request.session['test_state'] = 'completed'
                return redirect('test_complete_page')
            else:
                next_qID = next_qp.qID.qID
                return redirect('hyoka',qpID=qpID, qID=next_qID)
    
    return render(request,'hyoka.html',{'question':question,"timer":time_global,"progress":progress_percent,"total_questions":total_questions})
    


def arena(request):
    QB = pd.DataFrame(questionBank.objects.all().values())

    questionPaper = generateQIDS(QB)
    
    if QuestionPapers.objects.exists():
        newQPid = QuestionPapers.objects.order_by('qpID').last().qpID + 1
    else:
        newQPid = 1
    
    for question in questionPaper:
        question_obj = questionBank.objects.get(qID=question) #fetching the question object
        paper_question = QuestionPapers(
            qpID=newQPid,
            qID=question_obj #saving question object in the QuestionPapers model
        )
        paper_question.save()

    first_qp = QuestionPapers.objects.filter(qpID=newQPid).first()
    firstQID = first_qp.qID.qID if first_qp else None # Fetch the qID of the first question
    
    if request.method == "POST":
        # Set session variables consistently before redirecting
        request.session['test_state'] = 'in_progress'
        request.session['test_qpID'] = newQPid
        request.session['test_start_time'] = timezone.now().timestamp()
        request.session['test_duration'] = time_global  # 30 minutes in seconds
        return redirect('hyoka', qpID=newQPid, qID=firstQID)
    
    return render(request, "arenaMain.html")

def analyse(request):
    usratmpts = pd.DataFrame(userAttempts.objects.all().values()).groupby('qID_id').agg(
            attempts=('answer',list),
            marked_for_review = ('marked_for_review','first'),
            time_taken=('time_taken','first'),
            answer = ('answer','first')
        ).reset_index()
    print(usratmpts)
    analysis_result = analyse_usr(usratmpts)

    print(analysis_result['subdomain'].to_list())
    print(analysis_result['category_encoded'].to_list())

    weight_dict = dict(zip(analysis_result['subdomain'].to_list(),analysis_result['category_encoded'].to_list()))
    print(type(weight_dict))
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

def test_complete_page(request):
    
    return render(request,"test_complete_page.html")
