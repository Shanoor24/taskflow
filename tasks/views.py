from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import IsOwnerOrReadonly, IsOwnerOnly
from django.core.cache import cache
from .tasks import task_created_notification


class TaskListGeneric(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOnly]
    
    # def get_queryset(self):
    #     queryset = Task.objects.filter(owner=self.request.user)
    #     return queryset

class TaskListCreateGeneric(ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Task.objects.filter(owner=self.request.user)
        else:
            queryset = Task.objects.none()
        
        completed = self.request.query_params.get('completed', None)
        if completed == 'true':
            queryset = queryset.filter(completed=True)
        elif completed == 'false':
            queryset = queryset.filter(completed=False)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    

class TaskDetailGeneric(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOnly]
    
    # def get_queryset(self):
    #     queryset = Task.objects.filter(owner=self.request.user)
    #     return queryset

class TaskList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Create a separate cache key for each user
        cache_key = f"tasks:user:{request.user.id}:list"
        print("Cache key:", cache_key)
        
        # Check whether the user's tasks are already cached
        cached_tasks = cache.get(cache_key)
        
        if cached_tasks is not None:
            print("Fetching tasks from Redis")
            return Response(cached_tasks, status=status.HTTP_200_OK)

        print("Fetching tasks from PostgreSQL")
        
        # Cache miss: fetch tasks from PostgreSQL
        tasks = Task.objects.filter(owner=request.user)
        serializer = TaskSerializer(tasks, many=True)
        
        cache.set(cache_key, serializer.data, timeout=300)
        
        print("Tasks saved in Redis")
        
        return Response(serializer.data)
    
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task =serializer.save(owner=request.user)
            
            cache_key = f"tasks:user:{request.user.id}:list"
            cache.delete(cache_key)
            
            # Trigger Celery after the database transaction commits
            from django.db import transaction
            
            transaction.on_commit(
                lambda: task_created_notification.delay(task.id)
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetail(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, request, pk):
        return get_object_or_404(Task, pk=pk, owner=request.user)   
    
    def invalidate_task_cache(self, user_id):
        cache_key = f"tasks:user:{user_id}:list"
        cache.delete(cache_key)
        print(f"Cache invalidated for user: {user_id}")
    
    def get(self, request, pk):
        task = self.get_object(request, pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        task = self.get_object(request, pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            self.invalidate_task_cache(request.user.id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        task = self.get_object(request, pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            self.invalidate_task_cache(request.user.id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        task = self.get_object(request, pk)
        task.delete()
        self.invalidate_task_cache(request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    


# Create your views here.
def hello(request):
    response_data = JsonResponse({
        "message": "Hello from TaskFlow!",
        "project_name": "TaskFlow",
        "status": "success"
    })
    return response_data

