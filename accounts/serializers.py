from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    일반적인 사용자 정보 Serializer
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'profile_image', 'phone_number')
        read_only_fields = ('id',)

class RegisterSerializer(serializers.ModelSerializer):
    """
    회원가입을 위한 Serializer
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'user_type', 'phone_number')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')  # password2 필드 제거
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    """
    로그인을 위한 Serializer
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UpdateUserSerializer(serializers.ModelSerializer):
    """
    회원정보 수정을 위한 Serializer
    """
    class Meta:
        model = User
        fields = ('email', 'user_type', 'phone_number', 'profile_image')
        
    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("이미 사용중인 이메일입니다.")
        return value

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance
