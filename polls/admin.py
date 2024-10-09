from typing import Literal
from django.contrib import admin

from .models import Choice, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines: list[type[ChoiceInline]] = [ChoiceInline]
    list_display: tuple[Literal['question_text'], Literal['pub_date'], Literal['was_published_recently']] = (
        "question_text", 
        "pub_date", 
        "was_published_recently"
    )
    list_filter = ["pub_date"]
    search_fields = ['question_text']


admin.site.register(Question, QuestionAdmin)