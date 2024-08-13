from django.urls import path
from .views import *

urlpatterns = [
    path("", UserFullInformationView.as_view(), name="user_introspection"),
    path("/password", PasswordUpdateView.as_view(), name="user_password"),
    path("/picture", ProfilePictureView.as_view(), name="profile_picture_update"),
    path("/<int:userid>", UserInformationView.as_view(), name="user_info"),
]