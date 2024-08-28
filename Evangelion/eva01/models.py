from django.db import models

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


class userAttempts(models.Model):
    qpID = models.IntegerField()
    qID = models.IntegerField()
    answer = models.IntegerField()
    marked_for_review = models.IntegerField()
    time_taken = models.IntegerField()

class QuestionPapers(models.Model):
    qpID = models.IntegerField()
    qID = models.IntegerField()
