from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Main Pages
    path('', views.dashboard, name='dashboard'),
    path('app/<int:app_id>/', views.app_detail, name='app_detail'),
    path('app/<int:app_id>/review/', views.post_review, name='post_review'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),

    # User Actions
    path('my-reviews/', views.my_reviews, name='my_reviews'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
