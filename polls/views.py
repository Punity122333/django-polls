from typing import Any
from django.db.models import F, QuerySet
from django.db.models.manager import BaseManager
from django.shortcuts import get_object_or_404, render
from django.template import loader
from .models import Question, Choice, Vote
from django.urls import reverse
from django.views import generic 
from django.utils import timezone
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.http import HttpRequest
import logging
from logging import Logger
from django.core.paginator import Page, Paginator
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

logger: Logger = logging.getLogger(name=__name__)

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Question]:
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")

@method_decorator(login_required, name="dispatch")
class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    
    def get_queryset(self) -> QuerySet[Question]:
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def index(request: HttpRequest) -> HttpResponse:
    latest_question_list: QuerySet[Question] = Question.objects.order_by("-pub_date")
    paginator = Paginator(latest_question_list, 10)
    page_number: str | None = request.GET.get("page")
    page_obj: Page = paginator.get_page(page_number)
    return render(request, "polls/index.html", {"page_obj": page_obj})

def detail(request: HttpRequest, question_id: int) -> HttpResponse:
    question: Question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})

def results(request: HttpRequest, question_id: int) -> HttpResponse:
    question: Question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})

def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for: str = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip: str = x_forwarded_for.split(',')[0]
    else:
        ip: str = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def vote(request: HttpRequest, question_id: int) -> HttpResponse:
    question: Question = get_object_or_404(Question, pk=question_id)
    client_ip: str = get_client_ip(request)

    if Vote.objects.filter(question=question, ip_address=client_ip).exists():
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You have already voted.",
            },
        )

    try:
        selected_choice: Choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()

        Vote.objects.create(question=question, ip_address=client_ip)

        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

def graph(request: HttpRequest, question_id: int) -> HttpResponse:
    question: Question = get_object_or_404(Question, pk=question_id)
    choices: QuerySet[Choice] = question.choice_set.all()
    labels: list[str] = [choice.choice_text for choice in choices]
    data: list[int] = [choice.votes for choice in choices]

    context: dict[str, Any] = {
        "question": question,
        "labels": labels,
        "data": data,
    }
    return render(request, "polls/graph.html", context)