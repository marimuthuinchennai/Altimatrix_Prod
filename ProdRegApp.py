import sys
sys.path.append('/home/ec2-user/environment')
import pytest
from flask import Flask, jsonify, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime
# app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product_registration.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
app.config['SQLALCHEMY_ECHO'] = True
# db = SQLAlchemy(app)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Dummy user model (replace with your actual user model)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_description = db.Column(db.Text, nullable=False)
    manufacturer_info = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    manufacture_date = db.Column(db.Date, nullable=False)
    warranty_info = db.Column(db.String(100))
    product_category = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User authentication endpoints
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

# Product registration endpoint
@app.route('/products', methods=['POST'])
@login_required
def register_product():
    data = request.json
    serial_number = data.get('serial_number')
    existing_product = Product.query.filter_by(serial_number=serial_number).first()
    if existing_product:
        # Handle duplicate serial number error
        return jsonify({'message': 'Serial number already exists'}), 409
    else:
        product = Product(
            product_name=data['product_name'],
            product_description=data['product_description'],
            manufacturer_info=data['manufacturer_info'],
            serial_number=data['serial_number'],
            manufacture_date= datetime.strptime(data['manufacture_date'], "%Y-%m-%d").date(),
            warranty_info=data.get('warranty_info'),
            product_category=data['product_category']
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product registered successfully', 'product_id': product.id}), 201

# Product search and retrieval endpoint
@app.route('/products', methods=['GET'])
@login_required
def get_products():
    query_params = request.args
    page = int(query_params.get('page', 1))
    per_page = int(query_params.get('per_page', 10))
    product_name = query_params.get('product_name')
    manufacturer_info = query_params.get('manufacturer_info')
    product_category = query_params.get('product_category')

    filters = []
    if product_name:
        filters.append(Product.product_name.ilike(f'%{product_name}%'))
    if manufacturer_info:
        filters.append(Product.manufacturer_info.ilike(f'%{manufacturer_info}%'))
    if product_category:
        filters.append(Product.product_category.ilike(f'%{product_category}%'))

    products = Product.query.filter(or_(*filters)).paginate(page=page, per_page=per_page, error_out=False)
    result = [{
        'product_name': product.product_name,
        'manufacturer_info': product.manufacturer_info,
        'product_category': product.product_category,
        'id':product.id
    } for product in products.items]

    return jsonify({'products': result, 'total_products': products.total, 'page': page, 'per_page': per_page}), 200

# Product update endpoint
@app.route('/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    data = request.json
    product.product_name = data.get('product_name', product.product_name)
    product.product_description = data.get('product_description', product.product_description)
    product.manufacturer_info = data.get('manufacturer_info', product.manufacturer_info)
    product.serial_number = data.get('serial_number', product.serial_number)
    product.manufacture_date = data.get('manufacture_date', product.manufacture_date)
    product.warranty_info = data.get('warranty_info', product.warranty_info)
    product.product_category = data.get('product_category', product.product_category)

    db.session.commit()
    return jsonify({'message': 'Product updated successfully', 'product_id': product.id}), 200

# Product deletion endpoint
@app.route('/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200
    
def insert_user_if_not_exists(username, password_hash):
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:
            new_user = User(username=username, password_hash=password_hash)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        else:
            return existing_user
def create_test_user():
    username = 'test_user1'
    password_hash = 'hashed_password'
    return insert_user_if_not_exists(username, password_hash)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
        user = create_test_user()
    
    # db.create_all()
    app.run(debug=True)

