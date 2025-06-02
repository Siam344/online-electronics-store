from app import create_app, db
from app.models import *
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Disabling foreign key checks...")
    db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))
    db.session.commit()

    print("Dropping all tables...")
    db.drop_all()

    print("Creating all tables...")
    db.create_all()

    print("Re-enabling foreign key checks...")
    db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))
    db.session.commit()

    print("Database reset complete!")
