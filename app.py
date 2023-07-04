from flask import Flask, render_template, request,redirect

app = Flask(__name__)

menu = [
    {'id': 1, 'name': 'Dish 1', 'price': 10.99, 'availability': True},
    {'id': 2, 'name': 'Dish 2', 'price': 12.99, 'availability': True},
    {'id': 3, 'name': 'Dish 3', 'price': 8.99, 'availability': False}
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
        menu.append({'id': dish_id, 'name': dish_name, 'price': dish_price, 'availability': dish_availability})
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

# ...
if __name__ == '__main__':
    app.run(debug=True)