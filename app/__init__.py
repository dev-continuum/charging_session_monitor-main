from config import Settings
import boto3


settings = Settings()


def get_socket_client():
    return boto3.client('apigatewaymanagementapi', endpoint_url=settings.WEB_SOCKET_API)
