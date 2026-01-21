import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from django.http import StreamingHttpResponse
from .tasks import process_and_store_pinecone
from .rag.pipeline import rag_pipeline

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES["file"]

        upload_dir = "data/uploads/"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file_obj.name)
        with open(file_path, "wb") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        
        job = process_and_store_pinecone.delay(file_path)
        return Response(
            {"job_id" : job.id, "status" : "processing"},
            status=status.HTTP_202_ACCEPTED)


class QueryPipelineView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        system_prompt = request.data["system_prompt"]
        question = request.data["question"]
        top_k = request.data["top_k"]
        response = StreamingHttpResponse(rag_pipeline(question=question, 
                                                  top_k=top_k, 
                                                  system_prompt=system_prompt), content_type="text/plain")
        return response
