from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('check-in-out/', views.check_in_out, name='check_in_out'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('reports/', views.reports, name='reports'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(
        template_name='attendance/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]