from flask import Blueprint, send_from_directory, abort, current_app
from flask_login import login_required
from app.models import Document

images_bp = Blueprint('images', __name__, url_prefix='/api')

@images_bp.route('/documents/<int:doc_id>/image', methods=['GET'])
@login_required
def get_document_image(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if not doc.image_path:
        abort(404)
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        doc.image_path
    )