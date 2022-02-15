import boto3
import json
from django.conf import settings
from django.core.management.base import BaseCommand
from wagtail.images.models import Image


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("images.json", "r", encoding="utf-8") as f:
            s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            images = json.load(f)
            for image in images.keys():
                try:
                    Image.objects.get(filename=image["filename"])
                except Image.DoesNotExist:
                    img_file = s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, image["title"], image["filename"])
                    Image.objects.create(title=image["title"], file=img_file)
