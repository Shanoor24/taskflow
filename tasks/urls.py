from django.urls import path
from . import views


urlpatterns = [
    path('hello/', views.hello, name='hello'),
    path('tasks/', views.TaskList.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskDetail.as_view(), name='task-detail'),
    path('tasks/generic/', views.TaskListGeneric.as_view(), name='task-list-generic'),
    path('tasks/generic/create/', views.TaskListCreateGeneric.as_view(), name='task-list-create-generic'),
    path('tasks/generic/<int:pk>/', views.TaskDetailGeneric.as_view(), name='task-detail-generic'),
]