from django.urls import path
from . import views

urlpatterns = [
    path('bugs/', views.bug_list, name='bug-list'),
    path('bugs/<str:bug_id>/', views.bug_detail, name='bug-detail'),
    path('bug-stats/', views.bug_stats, name='bug-stats'),
]