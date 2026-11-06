from django.shortcuts import render
from .models import Person
from .serializers import PersonSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse

# Create your views here.
def single_object_view(request):
    data = Person.objects.get(id=1)  # Fetch a single object (for example, with id=1)
    serializer = PersonSerializer(data)
    json_data = JSONRenderer().render(serializer.data)  # Convert to JSON
    return HttpResponse(json_data, content_type='application/json')  # Return as JSON response

def multiple_objects_view(request):
    data = Person.objects.all()  # Fetch all objects
    serializer = PersonSerializer(data, many=True)
    json_data = JSONRenderer().render(serializer.data)  # Convert to JSON
    return HttpResponse(json_data, content_type='application/json')  # Return as JSON response