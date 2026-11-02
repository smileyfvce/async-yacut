from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField
from wtforms.validators import URL, DataRequired, Length, Optional

from yacut.constants import MAX_CUSTOM_ID_LENGTH


class URLMapForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Некорректный URL')
        ],
    )
    custom_id = StringField(
        'Короткая ссылка',
        validators=[
            Optional(),
            Length(
                max=MAX_CUSTOM_ID_LENGTH,
                message=f'Не более {MAX_CUSTOM_ID_LENGTH} символов',
            )
        ],
    )
    submit = SubmitField('Создать')


class FileUploadForm(FlaskForm):
    files = MultipleFileField(
        'Файлы',
        validators=[FileRequired(message='Обязательное поле')],
    )
    submit = SubmitField('Загрузить')