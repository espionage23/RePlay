from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # 회원가입
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # 로그인
    path('login/', views.LoginView.as_view(), name='login'),
    
    # 토큰 갱신
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 회원정보 조회 및 수정
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # 비밀번호 변경
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
]
