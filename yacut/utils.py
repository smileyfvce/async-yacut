import random

from yacut.models import URLMap

SHORT_ID_LENGTH = 6
SHORT_ID_ALPHABET = (
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
)


def get_unique_short_id(length=SHORT_ID_LENGTH):
    while True:
        short_id = ''.join(random.choices(SHORT_ID_ALPHABET, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id