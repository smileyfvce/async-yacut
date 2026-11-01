import re
from flask import jsonify, request, url_for
from yacut import app, db
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap
from yacut.utils import get_unique_short_id

MAX_CUSTOM_ID_LENGTH = 16
RESERVED_ID = 'files'


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
        if custom_id == RESERVED_ID or URLMap.query.filter_by(
            short=custom_id
        ).first():
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )
        short_id = custom_id
    else:
        short_id = get_unique_short_id()

    url_map = URLMap(original=original, short=short_id)
    db.session.add(url_map)
    db.session.commit()

    return jsonify({
        'url': url_map.original,
        'short_link': url_for(
            'redirect_to_original', short_id=short_id, _external=True
        ),
    }), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), 200