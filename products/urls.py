from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # 상품 목록 조회 및 생성
    path('', views.ProductListCreateView.as_view(), name='product-list'),
    
    # 상품 상세 조회, 수정, 삭제
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # 사용자별 상품 목록 조회
    path('my/', views.UserProductListView.as_view(), name='user-products'),
]
