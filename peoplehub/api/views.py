from django.shortcuts import render
from .models import Person
from .serializers import PersonSerializer

# Create your views here.
def single_object_view(request):
    data = Person.objects.get(id=1)  # Fetch a single object (for example, with id=1)
    serializer = PersonSerializer(data)
    print(serializer.data)  # Print the serialized data to the console

def multiple_objects_view(request):
    data = Person.objects.all()  # Fetch all objects
    serializer = PersonSerializer(data, many=True)
    print(serializer.data)  # Print the serialized data to the console