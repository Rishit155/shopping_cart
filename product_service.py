from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'products.sqlite')
db = SQLAlchemy(app)

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'  # SQLite database file
# db = SQLAlchemy(app)

# Define a model for the Product
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': product.quantity
        }
        product_list.append(product_data)
    return jsonify(product_list)

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': product.quantity
        }
        return jsonify(product_data)
    else:
        return jsonify({'message': 'Product not found'}), 404

@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    if 'name' not in data or 'price' not in data or 'quantity' not in data:
        return jsonify({'message': 'Invalid data'}), 400
    
    new_product = Product(
        name=data['name'],
        price=data['price'],
        quantity=data['quantity']
    )
    print(new_product)
    print('hello')
    db.session.add(new_product)
    print('hello')
    db.session.commit()
    
    return jsonify({'message': 'Product added successfully'}), 201

if __name__ == '__main__':
    with app.app_context():  # Create an application context
        db.create_all()  # Create the database tables
    app.run(debug=True)
