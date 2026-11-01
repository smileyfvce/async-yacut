import asyncio

from flask import current_app, flash, redirect, render_template, request, url_for

from yacut import app, db
from yacut.forms import FileUploadForm, URLMapForm
from yacut.models import URLMap
from yacut.utils import get_unique_short_id
from yacut.yandex_disk import upload_files

RESERVED_ID = "files"


@app.route("/", methods=["GET", "POST"])
def index_view():
    form = URLMapForm()
    short_link = None

    if form.validate_on_submit():
        original = form.original_link.data.strip()
        custom_id = (form.custom_id.data or "").strip() or None

        if custom_id:
            if (
                custom_id == RESERVED_ID
                or URLMap.query.filter_by(short=custom_id).first()
            ):
                flash("Предложенный вариант короткой ссылки уже существует.")
                return render_template("index.html", form=form)
            short_id = custom_id
        else:
            short_id = get_unique_short_id()

        db.session.add(URLMap(original=original, short=short_id))
        db.session.commit()
        short_link = url_for("redirect_to_original",
                             short_id=short_id, _external=True)

    return render_template("index.html", form=form, short_link=short_link)


@app.route("/files", methods=["GET", "POST"])
def files_page():
    form = FileUploadForm()
    results = None

    if form.validate_on_submit():
        files = [f for f in request.files.getlist("files") if f.filename]

        if not files:
            flash("Выберите хотя бы один файл")
        else:
            token = current_app.config["DISK_TOKEN"]
            download_urls = asyncio.run(upload_files(files, token))

            results = []
            for file_obj, download_url in zip(files, download_urls):
                short_id = get_unique_short_id()
                db.session.add(URLMap(original=download_url, short=short_id))
                db.session.commit()
                short_link = url_for(
                    "redirect_to_original",
                    short_id=short_id,
                    _external=True,
                )
                results.append((file_obj.filename, short_link))

    return render_template("files.html", form=form, results=results)


@app.route("/<string:short_id>")
def redirect_to_original(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
