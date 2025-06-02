from django.urls import path, include

urlpatterns = [
    # Include all URLs from the grc app with an 'api' prefix
    path('api/', include('grc.urls')),
]
