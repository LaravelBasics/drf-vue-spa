from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    """ログインシリアライザー"""
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)