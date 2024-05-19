from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(512), nullable=False)
    books = db.relationship('Book', secondary='mybooks', backref='users')
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def set_password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)

class Book(db.Model):
    __tablename__ = "book"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    author = db.Column(db.String(64), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    description = db.Column(db.String(512), nullable=True)
    copies = db.Column(db.Integer, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)
    blink = db.Column(db.String(64), nullable=False)
    book_feedback = db.relationship('Feedback', backref='books', lazy=True)
    sect = db.relationship('Section', backref=db.backref('books', lazy=True))

class Section(db.Model):
    __tablename__ = "section"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    ebooks = db.relationship("Book", backref="section", lazy=True)

class Mybooks(db.Model):
    __tablename__ = "mybooks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=True)
    is_granted = db.Column(db.Boolean, nullable=False, default=False)
    issued_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    return_date = db.Column(db.DateTime, nullable=False, default=datetime.now() + timedelta(days=5))
    book = db.relationship('Book', backref='mybooks')
    user = db.relationship('User', backref='mybooks')
    access_requests = db.relationship('AccessRequests', backref='mybooks')
    feedback = db.relationship('Feedback', backref='mybooks')

class AccessRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    ebook = db.Column(db.String(64), nullable=False)
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    mybooks_id = db.Column(db.Integer, db.ForeignKey('mybooks.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=True)

class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    mybooks_id = db.Column(db.Integer, db.ForeignKey('mybooks.id'), nullable=True)
    user = db.relationship('User', backref='feedback')
    book = db.relationship('Book', backref='feedback')

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(name='admin', username='admin', passhash=generate_password_hash('admin'), is_admin=True)
            db.session.add(admin)
            db.session.commit()
