from typing import Literal
from django.db import models
import datetime
from django.utils import timezone

from django.contrib import admin # timezone.now() returns the current date and time in a timezone-aware format
# Create your models here.

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    
    def __str__(self) -> str:
        return self.question_text
    
    @admin.display(
        boolean = True,
        ordering = "pub_date",
        description="Published recently?"
    )
    def was_published_recently(self) -> bool:
        now: datetime.datetime = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text= models.CharField(max_length=200)
    votes = models.IntegerField(default =0)
    
    def __str__(self) -> str:
        return self.choice_text
    
class Vote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    
    class Meta:
        unique_together: tuple[Literal['question'], Literal['ip_address']] = ("question", "ip_address")