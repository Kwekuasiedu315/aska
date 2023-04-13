from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.urls import reverse

from api.models.user_models import GENDER_CHOICES, CustomUser


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "nickname",
            "email",
            "birthdate",
            "gender",
            "bio",
            "profile_picture",
            "cover_picture",
            "subjects",
            "level",
        ]
        widgets = {
            "subjects": forms.CheckboxSelectMultiple,
            "level": forms.RadioSelect,
        }


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="New password",
        min_length=5,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="New password confirmation",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = CustomUser
        fields = [
            "phone_number",
            "first_name",
            "middle_name",
            "last_name",
            "birthdate",
            "gender",
            "password1",
            "password2",
        ]
        labels = {
            "birthdate": "Date of birth",
        }
        widgets = {
            "birthdate": forms.DateInput(
                format=("%Y-%m-%d"), attrs={"placeholder": "YYYY-MM-DD"}
            ),
            "gender": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("This phone number is already in use.")
        return phone_number

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ForgotPasswordForm(forms.Form):
    phone_or_email = forms.CharField(
        label="Phone number or email",
        widget=forms.TextInput(attrs={"class": "form-control", "required": True}),
    )

    def clean_phone_or_email(self):
        user = self.get_user()
        if not user:
            raise forms.ValidationError(
                "Phone number or email doesn't exist in our database"
            )
        return self.cleaned_data["phone_or_email"]

    def get_user(self):
        phone_or_email = self.cleaned_data["phone_or_email"]
        try:
            user = CustomUser.objects.get(
                models.Q(phone_number=phone_or_email) | models.Q(email=phone_or_email)
            )
        except CustomUser.DoesNotExist:
            return None
        return user

    def send_reset_password_email(self, request):
        user = self.get_user()
        reset_code = user.reset_password()
        if user and user.email:
            reset_link = request.build_absolute_uri(
                reverse("web:reset-password", kwargs={"user": user.id})
            )
            # send the reset password code and link to reset the password to email
            subject = "Reset your Askademy password"
            message = f"Dear {user.full_name},\n\nWe have received a request to reset the password for your Askademy account. To proceed with the password reset, please use the code provided below, and click on the following link:\n\nReset code: {reset_code}\n\nReset link: {reset_link}\n\nPlease note that the reset code will expire in 24 hours. If you did not initiate this password reset request, please contact our support team immediately.\n\nBest regards,\nThe Askademy Team."
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
        else:
            raise ValueError("The user doesn't have email account")


class ResetPasswordForm(forms.Form):
    reset_code = forms.CharField(
        label="Reset code",
        widget=forms.TextInput(attrs={"class": "form-control", "required": True}),
    )
    new_password = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "required": True}),
    )
    confirm_password = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "required": True}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        return super().__init__(*args, **kwargs)

    def clean_reset_code(self):
        reset_code = self.cleaned_data.get("reset_code")
        if self.user.password_reset_code != reset_code:
            raise forms.ValidationError("Invalid reset code.")
        return reset_code

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get("new_password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if new_password != confirm_password:
            raise forms.ValidationError("Passwords don't match.")
        return confirm_password

    def save(self):
        password = self.cleaned_data["new_password"]
        self.user.set_password(password)
        self.user.save()
