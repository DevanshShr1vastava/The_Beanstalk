from django.shortcuts import redirect, render
from .models import questionBank,QuestionPapers,userAttempts
import pandas as pd
import numpy as np
from django.utils import timezone
from datetime import timedelta
from eva01.generateQP import generateQIDS

# Create your views here.
time_global = 30*60
def hyoka(request, qpID, qID):
    
    if request.session.get('test_state') != 'in_progress':
        return redirect('home')  # Redirect if no active test
    
    QB = pd.DataFrame(questionBank.objects.all().values())
    question = QB.loc[QB['qID']== qID]
    
    # print(question)
    if(request.method == "POST"):
        attemptInfo = request.POST
        print(attemptInfo)
        if(qID == QuestionPapers.objects.filter(qpID=qpID).last().qID):
            attemptData = userAttempts(
                qpID = qpID,
                qID = qID,
                answer = attemptInfo.get('usrAnswer'),
                marked_for_review = attemptInfo.get('mFr'),
                time_taken = attemptInfo.get('TT')
            )
            attemptData.save()
                      
            
            if qID == QuestionPapers.objects.filter(qpID=qpID).last().qID:
                request.session['test_state'] = 'completed'
                return redirect('test_complete_page/')
        else:
            attemptData = userAttempts(
                qpID = qpID,
                qID = qID,
                answer = attemptInfo.get('usrAnswer'),
                marked_for_review = attemptInfo.get('mFr'),
                time_taken = attemptInfo.get('TT')
            )
            attemptData.save()
            curQ = QuestionPapers.objects.filter(qpID = qpID).filter(qID=qID).first()

            subseqQid = QuestionPapers.objects.filter(pk__gt = curQ.pk).order_by('pk').first().qID

            return redirect('hyoka',qpID=qpID,qID=subseqQid)
    
    return render(request,'hyoka.html',{'question':question.to_dict,"timer":time_global})
    


def arena(request):
    QB = pd.DataFrame(questionBank.objects.all().values())
    print(QB)

    questionPaper = generateQIDS(QB)
    
    if QuestionPapers.objects.exists():
        newQPid = QuestionPapers.objects.order_by('id').last().qpID + 1
    else:
        newQPid = 1
    
    for i in questionPaper:
        paperQuestion = QuestionPapers(
            qpID=newQPid,
            qID=i
        )
        paperQuestion.save()

    firstQID = QuestionPapers.objects.filter(qpID=newQPid).first().qID
    
    if request.method == "POST":
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

def test_complete_page(request):
    
    return render(request,"test_complete_page.html")
