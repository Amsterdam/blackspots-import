"""
API urls
"""
from django.conf.urls import include, url
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from api import views


class RootView(routers.APIRootView):
    pass


class BlackspotsRouter(routers.DefaultRouter):
    APIRootView = RootView


router = BlackspotsRouter()

# register spots/export before spots to prevent collision with spots/{id}
router.register(r'spots/export', views.SpotExportViewSet)
router.register(r'spots', views.SpotViewSet)
router.register(r'documents', views.DocumentViewSet)


# OpenAPI and Redoc schema specification
schema_view = get_schema_view(
    openapi.Info(
        title="Blackspots API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='swagger-schema'),  # noqa: line to long
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
