import os
BASE = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = os.environ.get('SECRET_KEY', 'change_this_secret')
DATABASE = os.path.join(BASE, 'messages.db')
UPLOAD_FOLDER = os.path.join(BASE, '..', 'static', 'files')
ALLOWED_EXT = {'png','jpg','jpeg','gif','webp','pdf','txt','zip','jpg'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max
