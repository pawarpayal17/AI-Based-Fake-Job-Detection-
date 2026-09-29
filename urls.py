from django.urls import path
from . import views
#app_name = 'jobs'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('submit_job/', views.submit_job, name='submit_job'),
    path('history/', views.history_view, name='history'),
    path('about_us/', views.about_us, name='about_us'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('api/predict/', views.api_predict, name='api_predict'),
]