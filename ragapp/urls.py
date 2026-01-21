from .views import FileUploadView, QueryPipelineView
from django.urls import path


urlpatterns = [
    path("file_upload/", FileUploadView.as_view(), name="file_upload"),
    path("chat/stream/", QueryPipelineView.as_view(), name="query_pipeline"),
]