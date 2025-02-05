from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserProfileViewSet, ProfileQuestionViewSet, ProfileAnswerViewSet

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profiles')
router.register(r'questions', ProfileQuestionViewSet, basename='profile-questions')
router.register(r'answers', ProfileAnswerViewSet, basename='profile-answers')

urlpatterns = [
    path('', include(router.urls)),
]
