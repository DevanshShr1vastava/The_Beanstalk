from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class questionBank(models.Model):
    qID = models.IntegerField(primary_key=True)
    questions = models.CharField(max_length=255)
    op1 = models.CharField(max_length=255)
    op2 = models.CharField(max_length=255)
    op3 = models.CharField(max_length=255)
    op4 = models.CharField(max_length=255)
    CorrectAnswer = models.CharField(max_length=255)
    option_number = models.IntegerField()
    difficulty = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=255)

class QuestionPapers(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UID")
    qpID = models.IntegerField()
    qID = models.ForeignKey(questionBank,on_delete=models.CASCADE,related_name='queID')

class userAttempts(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UserID")
    qpID = models.ForeignKey(QuestionPapers, on_delete = models.CASCADE, related_name='questionPaperID')
    qID = models.ForeignKey(questionBank, on_delete=models.CASCADE, related_name='questionID')
    answer = models.IntegerField()
    marked_for_review = models.IntegerField()
    time_taken = models.IntegerField()

class Subject(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    selected_subjects = models.ManyToManyField(Subject, blank=True)
    def __str__(self):
        return self.user.username

