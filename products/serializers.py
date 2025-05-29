from rest_framework import serializers
from .models import Product, ProductImage
from django.db import transaction

class ProductImageSerializer(serializers.ModelSerializer):
    """
    상품 이미지 시리얼라이저
    """
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'is_main')
        read_only_fields = ('id',)

class ProductSerializer(serializers.ModelSerializer):
    """
    상품 시리얼라이저
    """
    images = ProductImageSerializer(many=True, read_only=True)
    
    # 파일 업로드를 위한 필드
    uploaded_images = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        help_text='상품 이미지 파일 (여러 개 업로드 가능)'
    )
    
    main_image = serializers.IntegerField(
        write_only=True, 
        required=False,
        allow_null=True,
        help_text='대표 이미지로 설정할 이미지의 인덱스 (0부터 시작)'
    )
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'seller', 'title', 'price', 'description',
            'condition', 'status', 'category', 'brand', 'model_name',
            'views', 'created_at', 'updated_at', 'images',
            'uploaded_images', 'main_image'
        )
        read_only_fields = ('id', 'seller', 'views', 'created_at', 'updated_at')
        extra_kwargs = {
            'title': {'help_text': '상품 제목'},
            'price': {'help_text': '상품 가격'},
            'description': {'help_text': '상품 설명'},
            'condition': {'help_text': '상품 상태 (NEW, LIKE_NEW, GOOD, FAIR, POOR)'},
            'status': {'help_text': '판매 상태 (AVAILABLE, RESERVED, SOLD)'},
            'category': {'help_text': '카테고리 (GUITAR, BASS, DRUM, KEYBOARD, WIND, STRING, PERCUSSION, AMPLIFIER, EFFECT, ACCESSORY, ETC)'},
            'brand': {'help_text': '브랜드명'},
            'model_name': {'help_text': '모델명'}
        }

    def to_internal_value(self, data):
        # multipart/form-data 요청 처리
        if hasattr(data, 'getlist'):
            # request.FILES에서 이미지 가져오기
            files = data.getlist('uploaded_images')
            if files:
                data = data.copy()
                data.setlist('uploaded_images', files)
        return super().to_internal_value(data)

    @transaction.atomic
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        main_image_index = validated_data.pop('main_image', None)
        
        product = Product.objects.create(**validated_data)
        
        if uploaded_images:
            for index, image in enumerate(uploaded_images):
                is_main = (index == main_image_index) if main_image_index is not None else (index == 0)
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_main=is_main
                )
        
        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        main_image_index = validated_data.pop('main_image', None)
        
        # 기존 상품 정보 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 새 이미지 추가
        if uploaded_images:
            for index, image in enumerate(uploaded_images):
                is_main = (index == main_image_index) if main_image_index is not None else False
                ProductImage.objects.create(
                    product=instance,
                    image=image,
                    is_main=is_main
                )
        
        # 대표 이미지 변경
        if main_image_index is not None and not uploaded_images:
            instance.images.update(is_main=False)
            if 0 <= main_image_index < instance.images.count():
                instance.images.filter(is_main=False)[main_image_index].is_main = True
                instance.images.filter(is_main=False)[main_image_index].save()
        
        return instance