from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UpdateUserSerializer, ChangePasswordSerializer
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.

class RegisterView(generics.CreateAPIView):
    """
    회원가입 View
    """
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    """
    로그인 View
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user is None:
            return Response(
                {"error": "아이디 또는 비밀번호가 올바르지 않습니다."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    회원정보 조회 및 수정 View
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            "message": "회원정보가 성공적으로 수정되었습니다.",
            "user": serializer.data
        })


class ChangePasswordView(generics.UpdateAPIView):
    """
    비밀번호 변경 View
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # 비밀번호가 변경되면 기존 토큰 무효화를 위해 새로운 토큰 발급
        refresh = RefreshToken.for_user(request.user)
        
        return Response({
            "message": "비밀번호가 성공적으로 변경되었습니다.",
            "token": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        })
