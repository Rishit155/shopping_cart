from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import requests

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'carts.sqlite')
db = SQLAlchemy(app)

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carts.db'  # SQLite database file
# db = SQLAlchemy(app)

# Define a model for the Cart
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# URL of the Product Service
product_service_url = 'http://product-service-url/products'  # Update with your actual Product Service URL

@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    cart_data = []
    for cart_item in cart_items:
        product_response = requests.get(f'{product_service_url}/{cart_item.product_id}')
        if product_response.status_code == 200:
            product = product_response.json()
            cart_data.append({
                'product_id': cart_item.product_id,
                'name': product['name'],
                'quantity': cart_item.quantity,
                'price': product['price'] * cart_item.quantity
            })
    return jsonify(cart_data)

@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):
    quantity = request.json.get('quantity', 1)
    
    # Check if the product exists in the Product Service
    product_response = requests.get(f'{product_service_url}/{product_id}')
    if product_response.status_code != 200:
        return jsonify({'message': 'Product not found'}), 404
    
    product = product_response.json()
    
    existing_cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if existing_cart_item:
        existing_cart_item.quantity += quantity
    else:
        new_cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)
    
    db.session.commit()
    
    return jsonify({'message': 'Product added to cart'}), 201

@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    quantity = request.json.get('quantity', 1)
    
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if not cart_item:
        return jsonify({'message': 'Product not found in cart'}), 404
    
    if cart_item.quantity <= quantity:
        db.session.delete(cart_item)
    else:
        cart_item.quantity -= quantity
    
    db.session.commit()
    
    return jsonify({'message': 'Product removed from cart'}), 200

if __name__ == '__main__':
    with app.app_context():  # Create an application context
        db.create_all()  # Create the database tables
    app.run(debug=True)
