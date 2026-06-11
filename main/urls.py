from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'main'

urlpatterns =[
    path('', views.home_page, name='home'),
    path('events/', views.events_page, name='events'),
    
    # Авторизация и профиль
    path('accounts/login/', views.login_page, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/profile/', views.profile_view, name="profile"),

    # Маршруты для смены пароля
    path(
        'accounts/password/change/',
        auth_views.PasswordChangeView.as_view(
            template_name='accounts/info_manager.html',
            success_url=reverse_lazy('main:password_change_done')
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

    # Articles
    path('search/', views.search_view, name='search'),
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='article_edit'),
    path('articles/<slug:slug>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('articles/<slug:slug>/publish/', views.article_publish_toggle, name='article_publish_toggle'),
    path('articles/<slug:slug>/comment/', views.add_comment, name='add_comment'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),

    # Tags
    path('tags/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),

    # Management (for content managers)
    path('management/', views.article_management_dashboard, name='management_dashboard'),
    path('management/articles/', views.ArticleManagementListView.as_view(), name='article_management'),

    # Password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(success_url=reverse_lazy('main:password_reset_done')), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('main:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # mailing
    path(
    "profile/newsletter/",
    views.toggle_newsletter,
    name="toggle_newsletter",
    ),

    # Bug report
    path('report-bug/', views.report_bug, name='report_bug'),

    # Динамические страницы (ДОЛЖНЫ БЫТЬ В САМОМ КОНЦЕ!)
    path('<slug:slug>/', views.page_detail, name='page_detail'),

    
]