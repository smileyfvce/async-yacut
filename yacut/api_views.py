from http import HTTPStatus
import re
from flask import jsonify, request
from yacut import app, db
from yacut.constants import MAX_CUSTOM_ID_LENGTH, RESERVED_ID
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)

    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')

    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    original = data['url']
    if not isinstance(original, str) or not original.strip():
        raise InvalidAPIUsage('"url" не может быть пустым')

    custom_id = data.get('custom_id')
    if custom_id:
        if not isinstance(custom_id, str):
            raise InvalidAPIUsage('"custom_id" должен быть строкой')
        if len(custom_id) > MAX_CUSTOM_ID_LENGTH:
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
        if not re.fullmatch(r'[A-Za-z0-9]+', custom_id):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
        if custom_id == RESERVED_ID or URLMap.get_by_short(custom_id):
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )
        short_id = custom_id
    else:
        short_id = URLMap.get_unique_short_id()

    url_map = URLMap(original=original, short=short_id)
    db.session.add(url_map)
    db.session.commit()

    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    url_map = URLMap.get_by_short(short_id)
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK