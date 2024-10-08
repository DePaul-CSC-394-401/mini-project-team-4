from django.contrib import admin
from django.urls import path
from todo import views
from todo.views import CustomLoginView, RegisterPage
from django.contrib.auth.views import LogoutView
from django.urls import path


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),
    path('', views.index, name='todo'),
    path('start_timer/<int:item_id>/', views.start_timer, name='start_timer'),
    path('stop_timer/<int:item_id>/', views.stop_timer, name='stop_timer'),
    path('timer_log/<int:item_id>/', views.timer_log, name='timer_log'),
    path('', views.index, name="todo"),
    path('del/<str:item_id>/', views.remove, name='del'),
    path('edit/<str:item_id>', views.edit, name="edit"),
    path('admin/', admin.site.urls), 
    path('complete/<int:item_id>/', views.mark_complete, name='mark_complete'),
    path('change-password/', views.change_password, name='change_password'),
    path('update-email/', views.update_email, name='update_email'),
    path('create-team/', views.create_team, name='create_team'),
    path('teams/', views.user_teams, name='user_teams'),
    path('teams/update/<int:team_id>/', views.update_team, name='update_team'),
    path('teams/delete/<int:team_id>/', views.delete_team, name='delete_team'),
]