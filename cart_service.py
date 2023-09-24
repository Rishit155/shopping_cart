from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Define a dictionary to store cart data (for demonstration purposes).
carts = {}

# URL of the Product Service
product_service_url = 'http://product-service-url/products'

@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    if user_id not in carts:
        return jsonify({'message': 'Cart not found'}), 404
    
    return jsonify(carts[user_id])

@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):
    quantity = request.json.get('quantity', 1)
    
    # Check if the product exists in the Product Service
    product_response = requests.get(f'{product_service_url}/{product_id}')
    if product_response.status_code != 200:
        return jsonify({'message': 'Product not found'}), 404
    
    product = product_response.json()
    
    if user_id not in carts:
        carts[user_id] = {}
    
    if product_id in carts[user_id]:
        carts[user_id][product_id]['quantity'] += quantity
    else:
        carts[user_id][product_id] = {
            'name': product['name'],
            'quantity': quantity,
            'price': product['price'] * quantity
        }
    
    return jsonify({'message': 'Product added to cart'}), 201

@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    quantity = request.json.get('quantity', 1)
    
    if user_id not in carts or product_id not in carts[user_id]:
        return jsonify({'message': 'Product not found in cart'}), 404
    
    current_quantity = carts[user_id][product_id]['quantity']
    
    if quantity >= current_quantity:
        del carts[user_id][product_id]
    else:
        carts[user_id][product_id]['quantity'] -= quantity
        carts[user_id][product_id]['price'] -= quantity * carts[user_id][product_id]['price']
    
    return jsonify({'message': 'Product removed from cart'}), 200

if __name__ == '__main__':
    app.run(debug=True)
