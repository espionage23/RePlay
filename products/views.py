from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import F
from drf_yasg.utils import swagger_auto_schema, swagger_serializer_method
from drf_yasg import openapi
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsSellerOrReadOnly

class ProductSortMixin:
    """
    상품 정렬 믹스인
    
    정렬 옵션 (sort 파라미터):
    - latest: 최신순 (기본값)
    - oldest: 오래된순
    - price_high: 가격 높은순
    - price_low: 가격 낮은순
    - views: 조회수순
    """
    def get_sorted_queryset(self, queryset):
        sort_by = self.request.query_params.get('sort', 'latest')
        
        # 정렬 옵션에 따라 쿼리셋 정렬
        if sort_by == 'oldest':
            return queryset.order_by('created_at')
        elif sort_by == 'price_high':
            return queryset.order_by('-price')
        elif sort_by == 'price_low':
            return queryset.order_by('price')
        elif sort_by == 'views':
            return queryset.order_by('-views')
        else:  # latest (기본값)
            return queryset.order_by('-created_at')


class ProductListCreateView(ProductSortMixin, generics.ListCreateAPIView):
    """
    상품 목록 조회 및 생성 뷰
    
    list:
        모든 상품 목록을 조회합니다.
        정렬 옵션: sort=latest(기본값), oldest, price_high, price_low, views
    
    create:
        새 상품을 등록합니다.
        인증된 사용자만 등록 가능합니다.
        파일 업로드를 위해 반드시 Content-Type: multipart/form-data 로 요청해야 합니다.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'POST':
            if 'multipart/form-data' in self.request.content_type:
                # multipart/form-data 요청인 경우
                return ProductSerializer(data=self.request.data, context={'request': self.request})
            # JSON 요청인 경우
            return ProductSerializer(data=self.request.data)
        return super().get_serializer(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # 파일 업로드 처리
        if 'uploaded_images' in request.FILES:
            request.data._mutable = True
            request.data.setlist('uploaded_images', request.FILES.getlist('uploaded_images'))
            request.data._mutable = False
        return self.create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
    
    def get_queryset(self):
        return self.get_sorted_queryset(super().get_queryset())


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    상품 상세 조회, 수정, 삭제 뷰
    
    retrieve:
        특정 상품의 상세 정보를 조회합니다.
    update:
        특정 상품의 정보를 수정합니다. (판매자만 가능)
    delete:
        특정 상품을 삭제합니다. (판매자만 가능)
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSellerOrReadOnly]  # 권한 클래스 적용
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def check_object_permissions(self, request, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE'] and obj.seller != request.user:
            self.permission_denied(request, message='이 상품의 판매자가 아닙니다.')
        return super().check_object_permissions(request, obj)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 조회수 증가
        instance.views = F('views') + 1
        instance.save()
        instance.refresh_from_db()  # F() 표현식 이후 새로운 값을 가져오기 위해
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserProductListView(ProductSortMixin, generics.ListAPIView):
    """
    사용자별 상품 목록 조회 뷰
    
    list:
        현재 로그인한 사용자의 상품 목록을 조회합니다.
        
        정렬 옵션 (sort 파라미터):
        - latest: 최신순 (기본값)
        - oldest: 오래된순
        - price_high: 가격 높은순
        - price_low: 가격 낮은순
        - views: 조회수순
        
        예시: /api/products/my/?sort=price_high
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Product.objects.filter(seller=self.request.user)
        return self.get_sorted_queryset(queryset)
