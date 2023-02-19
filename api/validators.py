from rest_framework.serializers import ValidationError
from .models import CustomUser


def phone_number_exists(phone_number):
    user = CustomUser.objects.filter(phone_number=phone_number)
    if not user:
        raise ValidationError("A user with the input Phone number doesn't exists")
    return phone_number
