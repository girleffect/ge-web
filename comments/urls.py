from django.urls import include, path

urlpatterns = [
    path('', include('django_comments.urls')),
]
