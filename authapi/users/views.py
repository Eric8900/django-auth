from rest_framework import generics
from rest_framework.response import Response
from django.core.signing import Signer, BadSignature
from django.core.mail import send_mail
from .models import CustomUser
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

signer = Signer()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()
        token = signer.sign(user.email)
        verfication_url = f"http://localhost:8000/auth/verify-email/?token={token}"
        send_mail(
            "Verify your Email",
            f"Click here to verify your email: {verfication_url}",
            None,
            [user.email]
        )
        
class VerifyEmailView(generics.GenericAPIView):
    def get(self, request):
        token = request.GET.get("token")
        try:
            email = signer.unsign(token)
            user = CustomUser.objects.get(email=email)
            user.is_active = True
            user.is_verified = True
            user.save()
            return Response({"detail": "Email verified successfully"})
        except (BadSignature, CustomUser.DoesNotExist):
            return Response({"detail": "Email verified Invalid or expired token"}, status=400)
        
class TestAccessView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": f"Authenticated as {request.user.username}"})