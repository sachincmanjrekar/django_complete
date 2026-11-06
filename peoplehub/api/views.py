from django.shortcuts import render
from .models import Person
from .serializers import PersonSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse, JsonResponse
import io
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status


# Create your views here.
def single_object_view(request):
    data = Person.objects.get(id=1)  # Fetch a single object (for example, with id=1)
    serializer = PersonSerializer(data)
    json_data = JSONRenderer().render(serializer.data)  # Convert to JSON
    return JsonResponse(serializer.data, content_type='application/json')  # Return as JSON response

@csrf_exempt
def multiple_objects_view(request):
    if request.method == 'POST':
        # Handle POST request to create a new Person object
        json_data = request.body  # Get the raw JSON data from the request body
        stream = io.BytesIO(json_data)  # Create a BytesIO stream from the JSON
        parsed_data = JSONParser().parse(stream)  # Parse the JSON data
        serializer = PersonSerializer(data=parsed_data)  # Deserialize the data
        if serializer.is_valid():
            # If the data is valid, create a new Person object
            serializer.save()  # Save the new object to the database
            return JsonResponse({"created": "success"}, content_type='application/json', status=status.HTTP_201_CREATED)  # Return the created object as JSON response
        else:
            return JsonResponse(serializer.errors, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)  # Return validation errors as JSON response
        
    data = Person.objects.all()  # Fetch all objects
    serializer = PersonSerializer(data, many=True)
    return JsonResponse(serializer.data, content_type='application/json', safe=False)  # Return as JSON response