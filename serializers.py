from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api_user.models import *


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        get_user = {
            'email': user.email,
            'name': user.name,
        }
        # role
        token['user'] = get_user
        return token

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']
        extra_kwargs = {
            'id': {'read_only': True}
        }

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'no', 'street', 'district', 'city']
        extra_kwargs = {
            'id': {'read_only': True}
        }

class UserListSerializer(serializers.ModelSerializer):
    role = RoleSerializer(required=False)
    place = PlaceSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'gender', 'phone', 'birthday', "role", 'place', 'role_id', 'place_id']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
        }

class UserCreateSerializer(serializers.ModelSerializer):
    # role = RoleSerializer()
    place = PlaceSerializer(required=False)
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'gender', 'phone', 'birthday', "role", "password", 'place']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        place_data = validated_data.pop('place', None)
        if place_data:
            place = Place.objects.create(**place_data)
            # validated_data['place'] = place (solution_1)
            validated_data.update({'place': place}) # (solution_2)
        user = User.objects.create_user(email=email, password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        intance_place = instance.place
        data_place = validated_data.pop('place', None)

        instance.email = validated_data.get('email', instance.email)
        instance.name = validated_data.get('name', instance.name)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.role = validated_data.get('role', instance.role)

        if (intance_place is None) and (data_place is not None):
            # if place is not exist, we will create place
            place = Place.objects.create(**data_place)
            instance.place_id = place.id
        elif (intance_place is not None) and (data_place is not None):
            # if place is not exist, we will update place
            instance.place.no = data_place.get('no', instance.place.no)
            instance.place.street = data_place.get('street', instance.place.street)
            instance.place.district = data_place.get('district', instance.place.district)
            instance.place.city = data_place.get('city', instance.place.city)

        instance.save()
        return instance




