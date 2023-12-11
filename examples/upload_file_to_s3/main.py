import os
import boto3


def upload_file_to_bucket(file_path: str, bucket_name: str, object_name: str):
    # Create a new S3 bucket
    s3_client = boto3.client('s3')
    
    # Upload a file to the created bucket
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print('File uploaded successfully!')
    except Exception as e:
        print(e)

if __name__ == "__main__":
    bucket_name = '<your bucket name>'
    file_path = os.path.dirname(__file__)
    object_name = 'test.txt'
    file_path = os.path.join(file_path, object_name)
    upload_file_to_bucket(file_path, bucket_name, object_name)
