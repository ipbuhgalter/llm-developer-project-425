from yandex.cloud.lockbox.v1.payload_service import GetPayloadRequest
from yandex.cloud.lockbox.v1.payload_service import PayloadServiceClient
from yandex.cloud.lockbox.v1.secret_service import SecretServiceClient
from yandex.cloud.lockbox.v1.secret_service import ListSecretsRequest
import grpc


def get_lockbox_secret(secret_id: str, key: str) -> str:
    """
    Получает значение секрета из Yandex Lockbox по ключу.
    
    :param secret_id: ID секрета в Lockbox (например, 'e6q2c8v...')
    :param key: Ключ внутри секрета (например, 'DB_PASSWORD')
    :return: Значение секрета
    """
    # Создаём клиента для работы с Lockbox
    channel = grpc.secure_channel('lockbox.api.cloud.yandex.net:443', grpc.ssl_channel_credentials())
    payload_service = PayloadServiceClient(channel)

    # Запрашиваем полезную нагрузку (сами секреты)
    request = GetPayloadRequest(secret_id=secret_id)
    payload = payload_service.Get(request)

    # Ищем нужный ключ
    for entry in payload.entries:
        if entry.key == key:
            return entry.text_value

    raise KeyError(f"Ключ '{key}' не найден в секрете '{secret_id}'")
