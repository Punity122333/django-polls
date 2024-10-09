from django.urls import path
from django.conf import settings
from django.conf.urls import include
from django.urls.resolvers import URLPattern, URLResolver
from . import views

app_name = "polls"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("<int:question_id>/results/graph/", views.graph, name="graph"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns: list[URLPattern | URLResolver] = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns