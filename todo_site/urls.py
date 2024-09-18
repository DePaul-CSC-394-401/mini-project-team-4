from django.contrib import admin
from django.urls import path
from todo import views
from todo.views import CustomLoginView, RegisterPage
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),

    path('', views.index, name="todo"),
     path('del/<str:item_id>/', views.remove, name='del'),
    path('edit/<str:item_id>', views.edit, name="edit"),
    path('admin/', admin.site.urls), 
    path('complete/<int:item_id>/', views.mark_complete, name='mark_complete'),
    path('change-password/', views.change_password, name='change_password'),
    path('update-email/', views.update_email, name='update_email'),
]