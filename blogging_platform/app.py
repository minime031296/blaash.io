from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Token expiration time

db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(10), default='reader')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='posts')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post = db.relationship('Post', backref='comments')
    user = db.relationship('User', backref='comments')


with app.app_context():
    db.create_all()


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Please fill out the form!"}), 400

    hashed_password = generate_password_hash(password)
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return jsonify({"msg": "Invalid email address"}), 400

    if not re.match(r'[A-Za-z0-9]+', username):
        return jsonify({"msg": "Username must contain only characters and numbers!"}), 400

    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "You have successfully registered!"}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Please fill out the form!"}), 400

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity={'id': user.id, 'username': user.username, 'role': user.role})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Incorrect username or password"}), 401


@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    data = request.json
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"msg": "Missing fields"}), 400

    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    if user.role not in ['author', 'admin']:
        return jsonify({"msg": "Unauthorized"}), 403

    new_post = Post(title=title, content=content, author_id=user.id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"msg": "Post created successfully"}), 201


@app.route('/api/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = 2
    author = request.args.get('author')

    query = Post.query
    if author:
        query = query.join(User).filter(User.username == author)
    
    posts = query.paginate(page, per_page, False)

    result = [{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': User.query.get(post.author_id).username,
        'created_at': post.created_at
    } for post in posts.items]

    return jsonify(result), 200


@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    data = request.json
    content = data.get('content')

    if not content:
        return jsonify({"msg": "Missing content"}), 400

    current_user = get_jwt_identity()
    new_comment = Comment(content=content, post_id=post_id, user_id=current_user['id'])

    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"msg": "Comment added successfully"}), 201


if __name__ == "__main__":
    app.run(debug=True)
