from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    """
    사용자 정의 User 모델
    """
    # related_name 충돌 해결을 위한 설정
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )
    
    # 사용자 유형 선택
    USER_TYPE_CHOICES = (
        ('buyer', '구매자'),
        ('seller', '판매자'),
    )
    
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES,
        default='buyer',
        verbose_name='사용자 유형'
    )
    
    # 프로필 이미지
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        verbose_name='프로필 이미지'
    )
    
    # 연락처
    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name='연락처'
    )
    
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'