from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User
from apps.user.serializers import UserCreateSerializer, UserLoginSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        """
        Create a new user.
        `request`: The HTTP request containing user details (username, role(candidate, employer), email, password).
        **Return**:
        - 201 Created: Returns a success message if the user is successfully registered.
        - 400 Bad Request: Returns validation errors if any field is invalid.
        """
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            password = make_password(serializer.validated_data["password"])
            serializer.save(password=password)
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response({**serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        """
        Authenticates a user with valid login credentials (username and password).
        `request`: The HTTP request containing user details (username, password).
        **Return**:
        - 200 OK: Returns JWT access and refresh tokens upon successful login.
        - 401 Unauthorized: If the login credentials are invalid.
        - 400 Bad Request: If the input data does not pass validation.
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(
                request=self.request, username=username, password=password
            )
            if not user:
                return Response(
                    {"message": "Invalid Login Credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            refresh = RefreshToken.for_user(user)
            response_data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response(
                {"message": "Success", "data": response_data}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["get"],
        url_path="role",
        permission_classes=[IsAuthenticated],
    )
    def get_user_role(self, request):
        """
         Retrieves the role and username of the currently authenticated user.
        **Responses**:
        - 200 OK: Returns the user's role and username.
        - 401 Unauthorized: If the user is not authenticated.
        """
        user = request.user
        return Response(
            {"role": user.roles, "name": user.username}, status=status.HTTP_200_OK
        )
