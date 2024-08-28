from django.contrib import admin
from .models import questionBank,QuestionPapers, userAttempts
# Register your models here.

admin.site.register(questionBank)
admin.site.register(QuestionPapers)
admin.site.register(userAttempts)

