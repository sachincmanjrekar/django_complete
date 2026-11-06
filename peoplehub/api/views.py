from django.shortcuts import render
from .models import Person
from .serializers import PersonSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse, JsonResponse
import io
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.shortcuts import get_object_or_404

# Create your views here.
@csrf_exempt
def single_object_view(request, id):
    data = get_object_or_404(Person, id=id)  # Fetch a single object (for example, with id=1)

    if request.method == "PUT":

        stream = io.BytesIO(request.body)  # Create a BytesIO stream from the request body
        parsed_data = JSONParser().parse(stream)  # Parse the JSON data
        serializer = PersonSerializer(data, data=parsed_data)  # Deserialize the data
        if serializer.is_valid():
            serializer.save()  # Save the updated object to the database
            return JsonResponse({"updated": "success"}, content_type='application/json', status=status.HTTP_200_OK)  # Return the updated object as JSON response
        else:
            return JsonResponse(serializer.errors, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)  # Return validation errors as JSON response

    if request.method == "PATCH":
        stream = io.BytesIO(request.body)  # Create a BytesIO stream from the request body
        parsed_data = JSONParser().parse(stream)  # Parse the JSON data
        serializer = PersonSerializer(data, data=parsed_data, partial=True)  # Deserialize the data with partial update
        if serializer.is_valid():
            serializer.save()  # Save the updated object to the database
            return JsonResponse({"updated": "success"}, content_type='application/json', status=status.HTTP_200_OK)  # Return the updated object as JSON response
        else:
            return JsonResponse(serializer.errors, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)  # Return validation errors as JSON response


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