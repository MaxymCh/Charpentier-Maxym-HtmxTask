from django.urls import path
from firsttuto import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('tasks/', views.TasksList.as_view(), name='tasks'),
    path('all-tasks/', views.AllTasksList.as_view(), name='all-tasks'),

]


htmx_views = [
    path('check_username', views.check_username, name="check_username"),
    path('add-task/', views.add_task, name="add-task"),
    path('delete-user-task/<int:task_id>/', views.delete_user_task, name="delete-user-task"),
    path('search-task/', views.search_task, name="search-task"),
    path('clear/', views.clear, name="clear"),
    path('sort/', views.sort, name="sort"),
    path('load-more-tasks/', views.load_more_tasks, name='load-more-tasks'),
    path('edit-task/<int:task_id>/', views.edit_task, name="edit-task"),
    path('get-task/<int:task_id>/', views.get_task, name="get-task"),
    path('delete-task/<int:task_id>/', views.delete_task, name="delete-task"),
    path('inscription-task/<int:task_id>/', views.inscription_task, name="inscription-task"),

]

urlpatterns += htmx_views