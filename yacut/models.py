from datetime import datetime
import random

from flask import url_for

from yacut import db
from yacut.constants import (
    MAX_CUSTOM_ID_LENGTH,
    SHORT_ID_ALPHABET,
    SHORT_ID_GENERATION_ATTEMPTS,
    SHORT_ID_LENGTH
)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(db.String(MAX_CUSTOM_ID_LENGTH),
                      unique=True,
                      nullable=False,
                      index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self):
        return {
            'url': self.original,
            'short_link': url_for(
                'redirect_to_original',
                short_id=self.short,
                _external=True,
            ),
        }

    @classmethod
    def get_by_short(cls, short_id):
        return cls.query.filter_by(short=short_id).first()

    @classmethod
    def get_unique_short_id(cls, length=SHORT_ID_LENGTH):
        for _ in range(SHORT_ID_GENERATION_ATTEMPTS):
            short_id = ''.join(
                random.choices(SHORT_ID_ALPHABET, k=length)
            )
            if cls.get_by_short(short_id) is None:
                return short_id
        raise RuntimeError(
            'Не удалось сгенерировать уникальный короткий идентификатор'
        )
