from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.home_page, name='home'),
    path('educ.html', views.educ_page, name='educ'),
    path('events.html', views.events_page, name='events'),
    path('materials.html', views.materials_page, name='materials'),
    path('about_us.html', views.about_us_page, name='about_us'),
    path('login.html', views.login_page, name='login'),
    path('register.html', views.register_page, name='register'),
    path('profile', views.profile_view, name="profile"),
    
]
