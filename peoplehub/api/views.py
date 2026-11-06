from django.shortcuts import render
from .models import Person
from .serializers import PersonSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import io
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def single_object_view(request):
    data = Person.objects.get(id=1)  # Fetch a single object (for example, with id=1)
    serializer = PersonSerializer(data)
    json_data = JSONRenderer().render(serializer.data)  # Convert to JSON
    return HttpResponse(json_data, content_type='application/json')  # Return as JSON response

@csrf_exempt
def multiple_objects_view(request):
    if request.method == 'POST':
        # Handle POST request to create a new Person object
        json_data = request.body  # Get the raw JSON data from the request body
        stream = io.BytesIO(json_data)  # Create a BytesIO stream from the JSON
        parsed_data = JSONParser().parse(stream)  # Parse the JSON data
        print(parsed_data)  # Print the parsed data for debugging
        print(type(parsed_data)) 
        
    data = Person.objects.all()  # Fetch all objects
    serializer = PersonSerializer(data, many=True)
    json_data = JSONRenderer().render(serializer.data)  # Convert to JSON
    return HttpResponse(json_data, content_type='application/json')  # Return as JSON response