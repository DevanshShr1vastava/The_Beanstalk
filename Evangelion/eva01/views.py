from django.shortcuts import redirect, render
from .models import questionBank,QuestionPapers,userAttempts
import pandas as pd
import numpy as np
from eva01.generateQP import generateQIDS

# Create your views here.
def hyoka(request, qpID, qID):
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

            return redirect('/')
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
    
    return render(request,'hyoka.html',{'question':question.to_dict})
    


def arena(request):
    QB = pd.DataFrame(questionBank.objects.all().values())
    print(QB)

    questionPaper = generateQIDS(QB)

    # CurrentQuestionPaper = QB[QB['qID'].isin(questionPaper)]
    # currentQuestionPaperList = CurrentQuestionPaper.to_dict(orient="records")
    
    if(QuestionPapers.objects.exists()):
        newQPid = QuestionPapers.objects.order_by('id').last().qpID + 1
        for i in questionPaper:
            paperQuestion = QuestionPapers(
                qpID = newQPid,
                qID = i
            )
            paperQuestion.save()
        firstQID = QuestionPapers.objects.filter(qpID=newQPid).first().qID 
        if(request.method == "POST"):
            return redirect('hyoka',qpID=newQPid,qID=firstQID)    
    else:
        for i in questionPaper:
            paperQuestion = QuestionPapers(
                qpID = 1,
                qID = i
            )
            paperQuestion.save()
        firstQID = QuestionPapers.objects.filter(qpID=1).first().qID 
        if(request.method == "POST"):
            return redirect('hyoka',qpID=1,qID=firstQID)    

    return render(request,"arenaMain.html")


def home(request):
    
    return render(request,"home.html")