from django.conf import settings

FRONTEND_SETTINGS = settings.LOCAL_SETTINGS['FRONTEND_URLS']
BASE_URL = FRONTEND_SETTINGS['BASE_URL']


def reset_password_url(uuid: str, token: str):

    url = BASE_URL + FRONTEND_SETTINGS['RESET_PASSWORD']

    return url.replace(
        "{uid}",
        uuid
    ).replace(
        "{token}",
        token
    )
