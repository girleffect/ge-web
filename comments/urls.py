from django.urls import include, path
from .views import CommentReplyView
urlpatterns = [
    path("", include("django_comments.urls")),
    path("reply/<int:parent>/", CommentReplyView.as_view(), name="comment-reply")
]
