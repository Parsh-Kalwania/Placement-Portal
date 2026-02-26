from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Application
from .serializers import ApplicationSerializer
from users.permissions import IsNotBlacklisted


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsNotBlacklisted]

    def get_queryset(self):
        user = self.request.user

        if user.role == "student":
            return Application.objects.filter(student=user)

        if user.role == "company":
            return Application.objects.filter(drive__company=user)

        return Application.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "student":
            raise PermissionDenied("Only students can apply")

        drive = serializer.validated_data["drive"]

        # Prevent duplicate applications
        if Application.objects.filter(student=user, drive=drive).exists():
            raise PermissionDenied("You already applied to this drive")

        serializer.save(student=user)