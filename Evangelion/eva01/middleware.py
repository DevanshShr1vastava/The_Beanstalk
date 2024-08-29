from django.utils import timezone
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class TestTimerMiddleware(MiddlewareMixin):
    def auto_submit_test(request):
        # Logic to automatically submit the test
        request.session['test_state'] = 'completed'
        # Save test results to the database
        # Redirect to a results or thank you page
        return redirect('test_complete_page')
    
    def process_request(self, request):
        test_state = request.session.get('test_state')
        if test_state == 'in_progress':
            start_time = request.session.get('test_start_time')
            duration = request.session.get('test_duration')
            elapsed_time = timezone.now().timestamp() - start_time
            
            if elapsed_time >= duration:
                return auto_submit_test(request)
            
