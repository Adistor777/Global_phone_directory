from django.urls import path
from app.api.viewsets.user import UserSignupView, UserLoginView

urlpatterns = [
    path('user/signup', UserSignupView.as_view(), name='user-signup'),
    path('user/login', UserLoginView.as_view(), name='user-login'),
]