from django.shortcuts import render
from .models import Person
from .serializers import PersonSerializer, PersonModelSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse, JsonResponse
import io
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin

# Create your views here.
@api_view(['GET', 'PUT', 'PATCH'])
def single_object_view(request, id):
    data = get_object_or_404(Person, id=id)  # Fetch a single object (for example, with id=1)

    if request.method == "PUT":

        parsed_data = request.data  # Get the parsed data from the request
        serializer = PersonModelSerializer(data, data=parsed_data)  # Deserialize the data
        serializer.is_valid(raise_exception=True)  # Validate the data and raise an exception if invalid
        serializer.save()  # Save the updated object to the database
        return Response({"updated": "success"}, status=status.HTTP_200_OK)  # Return the updated object as JSON response

    if request.method == "PATCH":
        parsed_data = request.data  # Get the parsed data from the request
        serializer = PersonModelSerializer(data, data=parsed_data, partial=True)  # Deserialize the data with partial update
        serializer.is_valid(raise_exception=True)  # Validate the data and raise an exception if invalid
        serializer.save()  # Save the updated object to the database
        return Response({"updated": "success"}, status=status.HTTP_200_OK)  # Return the updated object as JSON response

    if request.method == "GET":

        # GET: return the single object as JSON
        serializer = PersonModelSerializer(data)
        return Response(serializer.data)


class SingleObjectView(APIView):
    def get(self, request, id):
        data = get_object_or_404(Person, id=id)  # Fetch a single object (for example, with id=1)
        serializer = PersonModelSerializer(data)
        return Response(serializer.data)

    def put(self, request, id):
        data = get_object_or_404(Person, id=id)  # Fetch a single object (for example, with id=1)
        parsed_data = request.data  # Get the parsed data from the request
        serializer = PersonModelSerializer(data, data=parsed_data)  # Deserialize the data
        serializer.is_valid(raise_exception=True)  # Validate the data and raise an exception if invalid
        serializer.save()  # Save the updated object to the database
        return Response({"updated": "success"}, status=status.HTTP_200_OK)  # Return the updated object as JSON response

    def patch(self, request, id):
        data = get_object_or_404(Person, id=id)  # Fetch a single object (for example, with id=1)
        parsed_data = request.data  # Get the parsed data from the request
        serializer = PersonModelSerializer(data, data=parsed_data, partial=True)  # Deserialize the data with partial update
        serializer.is_valid(raise_exception=True)  # Validate the data and raise an exception if invalid
        serializer.save()  # Save the updated object to the database
        return Response({"updated": "success"}, status=status.HTTP_200_OK)  # Return the updated object as JSON response


@api_view(['GET', 'POST'])
def multiple_objects_view(request):
    if request.method == 'POST':
        parsed_data = request.data  # Get the parsed data from the request
        serializer = PersonModelSerializer(data=parsed_data)  # Deserialize the data
        serializer.is_valid(raise_exception=True)  # Validate the data and raise an exception if invalid
        # If the data is valid, create a new Person object
        serializer.save()  # Save the new object to the database
        return Response({"created": "success"}, status=status.HTTP_201_CREATED)  # Return the created object as JSON response

    if request.method == 'GET':
        print(request.accepted_renderer)
        data = Person.objects.all()  # Fetch all objects
        serializer = PersonModelSerializer(data, many=True)
        return Response(serializer.data)  # Return as JSON response


class MultipleObjectsView(APIView):
    def get(self, request):
        data = Person.objects.all()  # Fetch all objects
        serializer = PersonModelSerializer(data, many=True)
        return Response(serializer.data)  # Return as JSON response

    def post(self, request):
        parsed_data = request.data  # Get the parsed data from the request
        serializer = PersonModelSerializer(data=parsed_data)  # Deserialize the data
        serializer.is_valid(raise_exception=True)  # Validate the data and raise an exception if invalid
        serializer.save()  # Save the new object to the database
        return Response({"created": "success"}, status=status.HTTP_201_CREATED)  # Return the created object as JSON response

class SingleObjectGenericView(GenericAPIView):
    queryset = Person.objects.all()  # The objects this view works with
    serializer_class = PersonModelSerializer  # The serializer this view uses
    lookup_field = 'id'  # get_object() finds the object by the <int:id> from the URL

    def get(self, request, id):
        data = self.get_object()  # Fetch the object (404 if it doesn't exist)
        serializer = self.get_serializer(data)
        return Response(serializer.data)

    def put(self, request, id):
        data = self.get_object()
        serializer = self.get_serializer(data, data=request.data)  # Deserialize the data
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Save the updated object to the database
        return Response({"updated": "success"}, status=status.HTTP_200_OK)

    def patch(self, request, id):
        data = self.get_object()
        serializer = self.get_serializer(data, data=request.data, partial=True)  # Partial update
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"updated": "success"}, status=status.HTTP_200_OK)


class MultipleObjectsGenericView(GenericAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonModelSerializer

    def get(self, request):
        data = self.get_queryset()  # Fetch all objects from queryset
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)  # Deserialize the data
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Save the new object to the database
        return Response({"created": "success"}, status=status.HTTP_201_CREATED)
