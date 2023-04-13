from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("search/", views.search_results, name="search"),
    path("about/", views.about_view, name="about-askademy"),
    path("profile/<int:pk>/", views.UserProfileView.as_view(), name="user-profile"),
    path(
        "profile/update/",
        views.UpdateUserProfileView.as_view(),
        name="update-user-profile",
    ),
    path("auth/register/", views.register_view, name="register"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("auth/forgot-password/", views.forgot_password_view, name="forgot-password"),
    path(
        "auth/<str:user>/reset-password/",
        views.reset_password_view,
        name="reset-password",
    ),
]
