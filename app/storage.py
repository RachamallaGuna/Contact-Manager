"""
Handles profile image uploads.

If AWS_S3_BUCKET + credentials are configured, images are uploaded to S3
and a public URL is returned. Otherwise, images are saved locally under
app/static/uploads so the app still works out of the box for local dev/demo.
"""
import os
import uuid
from flask import current_app, url_for
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_profile_image(file_storage):
    if not file_storage or file_storage.filename == "":
        return None

    if not allowed_file(file_storage.filename):
        raise ValueError("Unsupported file type.")

    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    bucket = current_app.config.get("AWS_S3_BUCKET")

    if bucket:
        import boto3

        s3 = boto3.client(
            "s3",
            aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
            region_name=current_app.config["AWS_REGION"],
        )
        s3.upload_fileobj(
            file_storage,
            bucket,
            f"profile-images/{unique_name}",
            ExtraArgs={"ContentType": file_storage.mimetype},
        )
        region = current_app.config["AWS_REGION"]
        return f"https://{bucket}.s3.{region}.amazonaws.com/profile-images/{unique_name}"

    # Local fallback
    upload_dir = os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, secure_filename(unique_name))
    file_storage.save(filepath)
    return url_for("static", filename=f"uploads/{unique_name}")
