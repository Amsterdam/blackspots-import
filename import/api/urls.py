"""
API urls
"""
from django.conf.urls import include
from rest_framework import routers
from django.urls import path

from api import views


class RootView(routers.APIRootView):
    pass


class BlackspotsRouter(routers.DefaultRouter):
    APIRootView = RootView


router = BlackspotsRouter()

router.register(r'spots', views.SpotViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
