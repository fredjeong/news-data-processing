from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from articles.models import ArticleLike, ArticleView, ArticleScrap, NewsArticle
from articles.serializers import NewsArticleSerializer, SimpleNewsArticleSerializer
from .models import User

class CustomRegisterSerializer(RegisterSerializer):
    username = None

    date_of_birth = serializers.DateField()
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'date_of_birth', 'first_name', 'last_name']

    def save(self, request):
        user = super().save(request)
        user.date_of_birth = self.data.get('date_of_birth')
        user.first_name = self.data.get('first_name')
        user.last_name = self.data.get('last_name')
        user.save()
        return user

class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        attrs['email'] = attrs['email'].lower()
        return super().validate(attrs)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_of_birth', 'is_active', 'created_at', 'updated_at']

class UserLikedArticleSerializer(serializers.ModelSerializer):
    article = SimpleNewsArticleSerializer(read_only=True)
    class Meta:
        model = ArticleLike
        fields = ['article', 'liked_at']

class UserViewedArticleSerializer(serializers.ModelSerializer):
    article = SimpleNewsArticleSerializer(read_only=True)
    class Meta:
        model = ArticleView
        fields = ['article', 'viewed_at']

class UserScrappedArticleSerializer(serializers.ModelSerializer):
    article = SimpleNewsArticleSerializer(read_only=True)
    class Meta:
        model = ArticleScrap
        fields = ['article', 'scrapped_at']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'date_of_birth']

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('현재 비밀번호가 올바르지 않습니다.')
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError('새 비밀번호가 일치하지 않습니다.')
        if len(data['new_password1']) < 8:
            raise serializers.ValidationError('비밀번호는 8자 이상이어야 합니다.')
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user
