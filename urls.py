from django.urls import path
from .views import signup, login_api

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", login_api, name="login_api"),  # ✅ Added login API route
]

