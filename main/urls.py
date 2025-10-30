from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('educ/', views.educ_page, name='educ'),
    path('events/', views.events_page, name='events'),
    path('materials/', views.materials_page, name='materials'),
    path('about_us/', views.about_us_page, name='about_us'),
    path('accounts/login/', views.login_page, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('accounts/info_manager/', views.info_manager, name='info_manager'),


    # Маршруты для смены пароля
    path(
        'accounts/password/change/',
        auth_views.PasswordChangeView.as_view(
            template_name='accounts/info_manager.html', 
            success_url='/accounts/password/change/done/'
        ),
        name='password_change'
    ),
    path(
        'accounts/password/change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='accounts/succesful_change.html'
        ),
        name='password_change_done'
    ),

]
