from django.urls import path, include

urlpatterns = [
    path('/user', include('api.v1.user.urls')),
    path('/verifier', include('api.v1.verifier.urls')),
    path('/chat', include('api.v1.chat.urls')),
    path('/conference', include('api.v1.conference.urls')),
]
