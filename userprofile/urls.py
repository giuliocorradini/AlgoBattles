from django.urls import path
from .views import *

urlpatterns = [
    path("", UserFullInformationView.as_view(), name="user_introspection"),
    path("/<int:userid>", UserInformationView.as_view(), name="user_info"),
]