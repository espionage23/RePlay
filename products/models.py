from django.db import models
from django.conf import settings

# Create your models here.

class Product(models.Model):
    """
    상품 모델
    """
    CONDITION_CHOICES = [
        ('NEW', '새 제품'),
        ('LIKE_NEW', '거의 새 제품'),
        ('GOOD', '좋음'),
        ('FAIR', '보통'),
        ('POOR', '나쁨'),
    ]
    
    STATUS_CHOICES = [
        ('AVAILABLE', '판매중'),
        ('RESERVED', '예약중'),
        ('SOLD', '판매완료'),
    ]
    
    CATEGORY_CHOICES = [
        ('GUITAR', '기타'),
        ('BASS', '베이스'),
        ('DRUM', '드럼'),
        ('KEYBOARD', '키보드'),
        ('WIND', '관악기'),
        ('STRING', '현악기'),
        ('PERCUSSION', '타악기'),
        ('AMPLIFIER', '앰프'),
        ('EFFECT', '이펙터'),
        ('ACCESSORY', '악세서리'),
        ('ETC', '기타'),
    ]
    
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='판매자'
    )
    title = models.CharField('제목', max_length=200)
    price = models.PositiveIntegerField('가격')
    description = models.TextField('설명')
    condition = models.CharField('상태', max_length=10, choices=CONDITION_CHOICES)
    status = models.CharField('판매상태', max_length=10, choices=STATUS_CHOICES, default='AVAILABLE')
    category = models.CharField('카테고리', max_length=10, choices=CATEGORY_CHOICES)
    brand = models.CharField('브랜드', max_length=100)
    model_name = models.CharField('모델명', max_length=100)
    views = models.PositiveIntegerField('조회수', default=0)
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '상품'
        verbose_name_plural = '상품 목록'
    
    def __str__(self):
        return self.title


class ProductImage(models.Model):
    """
    상품 이미지 모델
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='상품'
    )
    image = models.ImageField('이미지', upload_to='products/%Y/%m/%d/')
    is_main = models.BooleanField('대표 이미지', default=False)
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    
    class Meta:
        ordering = ['-is_main', '-created_at']
        verbose_name = '상품 이미지'
        verbose_name_plural = '상품 이미지 목록'
    
    def __str__(self):
        return f'{self.product.title}의 이미지'
