from rest_framework import permissions

class IsSellerOrReadOnly(permissions.BasePermission):
    """
    판매자만 수정/삭제할 수 있도록 하는 권한 클래스
    """
    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 누구에게나 허용
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # 쓰기 권한은 해당 상품의 판매자에게만 허용
        return obj.seller == request.user
