
from rest_framework import serializers
from .models import Person

class PersonSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    age = serializers.IntegerField()
    city = serializers.CharField(max_length=100)

    def create(self, validated_data):
        # Create and return a new `Person` instance, given the validated data.
        return Person.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Update and return an existing `Person` instance, given the validated data.
        instance.name = validated_data.get('name', instance.name)
        instance.age = validated_data.get('age', instance.age)
        instance.city = validated_data.get('city', instance.city)
        instance.save()
        return instance 