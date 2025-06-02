from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # 🔁 Replace this email with your actual admin email
    user = User.query.filter_by(email='siam@gmail.com').first()
    if user:
        user.role = 'owner'
        user.is_admin_approved = True
        db.session.commit()
        print("✅ Admin approved!")
    else:
        print("❌ No user found with that email.")
