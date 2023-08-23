from re import T
from django.db.models import fields
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    # media_segment_id = serializers.CharField(max_length= 50,default = "all")

    class Meta:
        model = User
        fields = ('email',
                  'name',
                  'phone',
                  'emp_code',
                  'user_role',
                  )

    def create(self, validated_data):
        user = User(email=validated_data['email'],
                    name=validated_data['name'],
                    phone=validated_data['phone'],
                    emp_code=validated_data['emp_code'],
                    user_role=validated_data['user_role'],
                    current_status=1,
                    is_active=1

                    )
        user.set_password(validated_data['password'])
        user.save()
        return user


class EditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()


class ResetPasswordLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetPassword
        fields = ('user_id', 'key', 'time')


class ResetPasswordsSerializer(serializers.Serializer):
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    key = serializers.CharField(max_length=25)