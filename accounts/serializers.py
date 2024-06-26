from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import User, EmailActivation
    
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'tin']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'tin', 'first_name', 'last_name', 'photo')


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    default_error_messages = {
        'bad_token': ('Token is not exist')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    
    def save(self, **kwargs):
        try:
            RefreshToken(token=self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class UserLegalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('is_physic',)


class UserInfoUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, allow_null=True, allow_blank=True)
    last_name = serializers.CharField(max_length=30, allow_null=True, allow_blank=True)
    # photo = Base64ImageField(max_length=None, use_url=True, allow_null=True, default=None)


class UserPasswordUpdateSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=125, required=True)


class ResetUserPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=125, required=True)