from django.http import HttpResponse
from django.test import TestCase
import datetime
from django.utils import timezone
from django.urls import reverse
from .models import Question, Choice
from typing import List

def create_question(question_text: str, days: int) -> Question:
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time: datetime.datetime = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self) -> None:
        """
        If no questions exist, an appropriate message is displayed.
        """
        response: HttpResponse = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self) -> None:
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question: Question = create_question(question_text="Past question.", days=-30)
        response: HttpResponse = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self) -> None:
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response: HttpResponse = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self) -> None:
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question: Question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response: HttpResponse = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self) -> None:
        """
        The questions index page may display multiple questions.
        """
        question1: Question = create_question(question_text="Past question 1.", days=-30)
        question2: Question = create_question(question_text="Past question 2.", days=-5)
        response: HttpResponse = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )
        
class QuestionDetailViewTests(TestCase):
    
    def test_future_question(self):
        future_question: Question = create_question(question_text="Future question.", days=5)
        url: str = reverse("polls:detail", args=(future_question.id,))
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_past_question(self):
        past_question: Question = create_question(question_text="Past question.", days=-5)
        url: str = reverse("polls:detail", args=(past_question.id,))
        response: HttpResponse = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        
class GraphViewTests(TestCase):
    
    def test_graph_view_with_no_votes(self) -> None:
        question: Question = create_question(question_text="Question with no votes", days=-1)
        url: str = reverse("polls:graph", args=(question.id,))
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)
        
    def test_graph_view_with_votes(self) -> None:
        question: Question = create_question(question_text="Votes question.", days=-1)
        choice1: Choice = Choice.objects.create(question=question, choice_text="Choice 1", votes=5)
        choice2: Choice = Choice.objects.create(question=question, choice_text="Choice 2", votes=3)
        url: str = reverse("polls:graph", args=(question.id,))
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)
        self.assertContains(response, choice1.choice_text)
        self.assertContains(response, choice2.choice_text)