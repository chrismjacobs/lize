"""Helpers for uploading files to S3 and generating signed URLs."""
import uuid
import boto3
from botocore.exceptions import ClientError
from flask import current_app


def get_s3_client():
    return boto3.client(
        's3',
        region_name=current_app.config['AWS_S3_REGION'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
    )


def upload_file_to_s3(file_obj, folder='uploads', content_type=None):
    """Upload a file-like object to S3 and return its public URL."""
    s3 = get_s3_client()
    bucket = current_app.config['AWS_S3_BUCKET']
    region = current_app.config['AWS_S3_REGION']

    ext = ''
    filename = getattr(file_obj, 'filename', '')
    if '.' in filename:
        ext = '.' + filename.rsplit('.', 1)[1].lower()

    key = f"{folder}/{uuid.uuid4().hex}{ext}"

    extra_args = {}
    if content_type:
        extra_args['ContentType'] = content_type
    elif ext in ('.jpg', '.jpeg'):
        extra_args['ContentType'] = 'image/jpeg'
    elif ext == '.png':
        extra_args['ContentType'] = 'image/png'
    elif ext == '.webm':
        extra_args['ContentType'] = 'audio/webm'
    elif ext == '.mp4':
        extra_args['ContentType'] = 'audio/mp4'

    s3.upload_fileobj(file_obj, bucket, key, ExtraArgs=extra_args)
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"


def delete_s3_file(url):
    """Delete a file from S3 given its public URL."""
    try:
        s3 = get_s3_client()
        bucket = current_app.config['AWS_S3_BUCKET']
        region = current_app.config['AWS_S3_REGION']
        prefix = f"https://{bucket}.s3.{region}.amazonaws.com/"
        if url.startswith(prefix):
            key = url[len(prefix):]
            s3.delete_object(Bucket=bucket, Key=key)
    except ClientError:
        pass  # best-effort delete
