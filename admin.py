from blog_4 import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User.query.filter_by(username='南殳').first()
    user.is_admin = True
    db.session.commit()
    print("✅ 管理员权限已授予")