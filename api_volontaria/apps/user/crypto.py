# inspired from https://github.com/florimondmanca/djangorestframework-api-key/tree/master/src/rest_framework_api_key
import typing


from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import get_random_string


# def concatenate(left: str, right: str) -> str:
#     return "{}.{}".format(left, right)


# def split(concatenated: str) -> typing.Tuple[str, str]:
#     left, _, right = concatenated.partition(".")
#     return left, right


class KeyGenerator:
    def __init__(self, secret_key_length: int = 40):
        # self.prefix_length = prefix_length
        self.secret_key_length = secret_key_length

    # def get_prefix(self) -> str:
    #     return get_random_string(self.prefix_length)

    def get_secret_key(self) -> str:
        return get_random_string(self.secret_key_length)

    def hash(self, value: str) -> str:
        return make_password(value)

    def generate(self) -> typing.Tuple[str, str]:
        # prefix = self.get_prefix()
        secret_key = self.get_secret_key()
        # key = concatenate(prefix, secret_key)
        hashed_key = self.hash(key)
        return key, hashed_key

    def verify(self, key: str, hashed_key: str) -> bool:
        return check_password(key, hashed_key)
