from django.utils import timezone
from django.shortcuts import redirect,get_object_or_404
from django.utils.deprecation import MiddlewareMixin
from .models import questionBank,QuestionPapers,userAttempts, UserProfile

def voidTest(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        username = request.user.username
    
    # now fetch the last given questionPaper id
    # we need to remove the last attempts first 
    # and then remove the question paper from the questionPapers database

    qpID_to_remove = QuestionPapers.objects.filter(userId = user_id).order_by('qpID').last().qpID

    question_paper_to_remove = get_object_or_404(QuestionPapers, userID = user_id, qpID = qpID_to_remove)

    user_attempt_to_remove = userAttempts.objects.filter(userID = user_id, qpID = question_paper_to_remove)
    # deleting the attempts first to avoid foreign key constraint error
    user_attempt_to_remove.delete()

    # now delete the question paper itself second since no foreign key constraint error will come now

    question_paper_to_remove.delete()



def auto_submit_test(request):
    # Logic to automatically submit the test
    request.session['test_state'] = 'completed'
    # Save test results to the database
    # Redirect to a results or thank you page
    return redirect('test_complete_page')

class TestTimerMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        test_state = request.session.get('test_state')
        if test_state == 'in_progress':
            start_time = request.session.get('test_start_time')
            duration = request.session.get('test_duration')
            elapsed_time = timezone.now().timestamp() - start_time
            
            if elapsed_time >= duration:
                return auto_submit_test(request)
            
