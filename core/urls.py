from django.conf import settings
from django.urls import path, include, re_path
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as drf_views

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from core.users.views import UserViewSet, GoogleAuthTokenView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/api-token-auth/', drf_views.obtain_auth_token, name='api_token_auth'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/conduit/', include('core.conduit.urls')),

    # django-allauth
    path('accounts/', include('allauth.urls')),

    # drf-spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Organizations / Teams
    path('api/v1/organizations/', include('core.organizations.urls')),

    # PROFILES (NEW)
    path('api/v1/profiles/', include('profiles.urls')),

    # default redirect
    re_path(r'^$', RedirectView.as_view(url='/api/v1/', permanent=False)),

    path('api/v1/subscriptions/', include('subscriptions.urls')),


    path('api/v1/google-auth-token/', GoogleAuthTokenView.as_view(), name='google_auth_token'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
