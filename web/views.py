from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.contrib import messages

from .forms import (
    RegistrationForm,
    UpdateUserForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from api.models import CustomUser

from . import dummy


def about_view(request):
    return render(request, template_name="web/about_askademy.html")


def search_results(request):
    query = request.GET.get("q", "")
    name_filter = request.GET.get("name", "")
    location_filter = request.GET.get("location", "")
    job_title_filter = request.GET.get("job_title", "")

    # Filter the dummy data based on the search criteria
    results = []
    for item in dummy.dummy_data:
        if query and query.lower() not in item.name.lower():
            continue
        if name_filter and name_filter.lower() not in item.name.lower():
            continue
        if location_filter and location_filter.lower() not in item.location.lower():
            continue
        if job_title_filter and job_title_filter.lower() not in item.job_title.lower():
            continue
        results.append(item)

    # Paginate the search results
    paginator = Paginator(results, 10)  # Show 10 results per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "query": query,
        "name_filter": name_filter,
        "location_filter": location_filter,
        "job_title_filter": job_title_filter,
        "results": page_obj,
    }
    return render(request, "web/search_results.html", context)


class UserProfileView(TemplateView):
    template_name = "auth/user_profile.html"

    def get_context_data(self, pk, **kwargs):
        user = get_object_or_404(CustomUser, pk=pk)
        context = super().get_context_data(**kwargs)
        context["user"] = get_object_or_404(CustomUser, pk=pk)
        context["user_has_school_info"] = any(
            x for x in [user.school, user.subjects.count(), user.level]
        )
        context["posts"] = dummy.posts
        context["friends"] = dummy.friends
        context["user_photos"] = dummy.album["user_photos"]
        context["user_videos"] = dummy.album["user_videos"]
        return context


class UpdateUserProfileView(generic.UpdateView):
    model = CustomUser
    form_class = UpdateUserForm
    template_name = "auth/user_update.html"
    success_url = reverse_lazy("web:home")

    def get_object(self, *args, **kwargs):
        return self.request.user


class HomePageView(TemplateView):
    template_name = "web/home.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = dummy.posts
        return context


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("web:home")
    else:
        form = RegistrationForm()
    return render(request, "auth/register.html", {"form": form})


def login_view(request):
    form = {"error": None, "message": ""}
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")
        user = authenticate(phone_number=phone_number, password=password)
        if user is not None:
            login(request, user)
            return redirect("web:home")
        else:
            form["error"] = True
            form["message"] = "Invalid phone number or password"
    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("web:login")


def forgot_password_view(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                # generate a one-time use reset link
                form.send_reset_password_email(request)
                messages.success(
                    request,
                    f'A password Reset Code has been sent to "{user.email or user.phone_number}".',
                )
                return redirect("web:reset-password", user=user.id)
    else:
        form = ForgotPasswordForm()
    return render(request, "auth/reset-password/forgot_password.html", {"form": form})


def reset_password_view(request, user):
    user = get_object_or_404(CustomUser, id=user)
    if request.method == "POST":
        form = ResetPasswordForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Password reset successful. Enter your login credentials"
            )
            return redirect("web:login")
    else:
        form = ResetPasswordForm()
    return render(request, "auth/reset-password/reset_password.html", {"form": form})
