from flask import Flask, render_template, request,redirect
from flask_socketio import SocketIO, emit
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)
menu = [
    {'id': 1, 'name': 'Dish 1', 'price': 10.99, 'availability': True,'rating': 0, 'reviews': []},
    {'id': 2, 'name': 'Dish 2', 'price': 12.99, 'availability': True,'rating': 0, 'reviews': []},
    {'id': 3, 'name': 'Dish 3', 'price': 8.99, 'availability': False,'rating': 0, 'reviews': []}
]
orders = []
order_id = 1

# ...

# Menu management routes
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/menu')
def menu1():
    return render_template('menu.html', menu=menu)

@app.route('/menu/add', methods=['GET', 'POST'])
def add_dish():
    if request.method == 'POST':
        dish_id = int(request.form['id'])
        dish_name = request.form['name']
        dish_price = float(request.form['price'])
        dish_availability = True if request.form.get('availability') else False

    
        # Check if dish with the given ID already exists
        if any(dish['id'] == dish_id for dish in menu):
            error = f"Dish with ID {dish_id} already exists."
            return render_template('add_dish.html', error=error)

        # Add the new dish to the menu
        menu.append({'id': dish_id, 'name': dish_name, 'price': dish_price, 'availability': dish_availability,"rating":0,"reviews":[]})
        return redirect('/menu')

    return render_template('add_dish.html')

@app.route('/menu/remove', methods=['GET', 'POST'])
def remove_dish():
    if request.method == 'POST':
        dish_id = int(request.form['id'])

        # Find the dish with the given ID
        for dish in menu:
            if dish['id'] == dish_id:
                menu.remove(dish)
                break

        return redirect('/menu')

    return render_template('remove_dish.html')

@app.route('/menu/update', methods=['GET', 'POST'])
def update_dish():
    if request.method == 'POST':
        dish_id = int(request.form['id'])
        dish_availability = True if request.form.get('availability') else False

        # Find the dish with the given ID and update its availability
        for dish in menu:
            if dish['id'] == dish_id:
                dish['availability'] = dish_availability
                break

        return redirect('/menu')

    return render_template('update_dish.html')
@app.route('/order')
def order():
    return render_template('order.html', orders=orders)

@app.route('/order/new', methods=['GET', 'POST'])
def new_order():
    if request.method == 'POST':
        customer_name = request.form['name']
        dish_ids = request.form.getlist('dish_id')

        ordered_dishes = []
        total_price = 0.0

        for dish_id in dish_ids:
            dish_id = int(dish_id)
            dish = next((d for d in menu if d['id'] == dish_id), None)

            if dish and dish['availability']:
                ordered_dishes.append(dish)
                total_price += dish['price']

        if len(ordered_dishes) == 0:
            error = "No valid dishes found in the order."
            return render_template('new_order.html', error=error)

        global order_id
        order = {'id': order_id, 'customer': customer_name, 'dishes': ordered_dishes, 'status': 'received', 'total_price': total_price}
        orders.append(order)
        order_id += 1

        return redirect('/order')

    return render_template('new_order.html', menu=menu)

@app.route('/order/update', methods=['GET', 'POST'])
def update_order():
    if request.method == 'POST':
        order_id = int(request.form['id'])
        new_status = request.form['status']

        order = next((o for o in orders if o['id'] == order_id), None)
        if order:
            order['status'] = new_status

        return redirect('/order')

    return render_template('update_order.html', orders=orders)

@app.route('/order/review')
def review_orders():
    return render_template('review_orders.html', orders=orders)


# In-memory data store for menu and feedback
@app.route('/feedback')
def menu_page():
    return render_template('feedbak.html', menu=menu)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    dish_id = int(request.form['dish_id'])
    rating = int(request.form['rating'])
    review = request.form['review']

    # Update rating and review for the selected dish
    menu[dish_id - 1]['rating'] = (menu[dish_id - 1]['rating'] + rating) / 2
    menu[dish_id - 1]['reviews'].append(review)

    # Redirect back to the menu page
    return redirect('/feedback')

preprogrammed_responses = {
    "operation_hours": "Our operation hours are from 9 am to 5 pm, Monday to Friday.",
    "order_status": "The status of your order is currently being processed.",
    "order_status1":"It will take 30min to deliverd for Now"
    # Add more pre-programmed responses for common queries
}

@app.route('/chat')
def home1():
    return render_template('chat.html')

@app.route('/chatget', methods=['POST'])
def chat():
    user_message = request.form['user_input']
    response = generate_response(user_message)
    return response

def generate_response(user_message):
    # Add your logic here to generate the chatbot response
    if user_message.lower() == 'what is your operation hours?':
        return preprogrammed_responses['operation_hours']
    elif user_message.lower() == 'what is the status of my order?':
        return preprogrammed_responses['order_status']
    elif user_message.lower() == 'how much time it will take?':
        return preprogrammed_responses['order_status1']
    else:
        return "I'm sorry, I don't have the information you're looking for. plase contact for coustomer servies toll free no"





@app.route('/up')
def index1():
    return render_template('up.html')

@socketio.on('connect')
def handle_connect():
    emit('connection_response', {'message': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('get_order_status')
def handle_get_order_status(order_id):
    status = orders.get(order_id, 'Unknown')
    emit('order_status', {'order_id': order_id, 'status': status})

@socketio.on('update_order_status')
def handle_update_order_status(data):
    order_id = data['order_id']
    status = data['status']
    orders[order_id] = status
    emit('order_status_updated', {'order_id': order_id, 'status': status}, broadcast=True)

# ...
if __name__ == '__main__':
    app.run(debug=True)