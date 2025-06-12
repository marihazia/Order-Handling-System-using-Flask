from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import render_template, request, redirect, url_for

Ordersapp = Flask(__name__)
Ordersapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
db= SQLAlchemy(Ordersapp)
class order(db.Model):
    __tablename__ = 'orders'
    id= db.Column(db.Integer, primary_key= True)
    item_no= db.Column(db.Integer, nullable=False)
    del_date= db.Column(db.String(50), nullable=False)
    sender_name= db.Column(db.String(50), nullable=False)
    rec_name =db.Column(db.String(50), nullable=False)
    rec_address =db.Column(db.String(300), nullable=False)
    status= db.Column(db.String(40), default='ongoing')

class action_log(db.Model):
    __tablename__ = 'action_logs'
    id= db.Column(db.Integer, primary_key= True)
    order_id= db.Column(db.Integer,db.ForeignKey('orders.id'), nullable=False)
    action_type= db.Column(db.String(50), nullable=False)
    perf_by= db.Column(db.String(50), nullable=False)
    time_stamp= db.Column(db.DateTime, default= datetime.utcnow)

@Ordersapp.route('/')
def root_redirect():
    return redirect(url_for('view_orders'))  
  
@Ordersapp.route('/orders')
def view_orders():
    orders = order.query.all()
    html = """
    <h1>Order Handling System</h1>
    <a href='/orders/add'>| Add New Order</a>|
    <h2>All Orders</h2>
    <table border='1' cellpadding='5'>
        <tr>
            <th>ID</th><th>Item No</th><th>Delivery Date</th>
            <th>Sender</th><th>Recipient</th><th>Address</th>
            <th>Status</th><th>Actions</th>
        </tr>
    """
    for o in orders:
        html += f"""
        <tr>
            <td>{o.id}</td><td>{o.item_no}</td><td>{o.del_date}</td>
            <td>{o.sender_name}</td><td>{o.rec_name}</td><td>{o.rec_address}</td>
            <td>{o.status}</td>
            <td>
                <a href='/orders/deliver/{o.id}'>Deliver</a> |
                <a href='/orders/edit/{o.id}'>Edit</a> |
                <a href='/orders/delete/{o.id}'>Delete</a>
            </td>
        </tr>
        """
    html += "</table>"
    return html
    
@Ordersapp.route('/orders/deliver/<int:order_id>')
def mark_del(order_id):
    ord=order.query.get_or_404(order_id)
    ord.status="delivered"
    log= action_log(
        order_id=ord.id, action_type= "marked as delivered", perf_by= "admin"
    )
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('view_orders'))

@Ordersapp.route('/orders/delete/<int:order_id>')
def delete(order_id):
    ord=order.query.get_or_404(order_id)
    ord.status="delivered"
    log= action_log(
        order_id=ord.id, action_type= "deleted", perf_by= "admin"
    )
    db.session.add(log)
    db.session.delete(ord)
    db.session.commit()
    return redirect(url_for('view_orders'))

@Ordersapp.route('/orders/edit/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    ord = order.query.get_or_404(order_id)
    if request.method == 'POST':
        ord.item_no = request.form['item_no']
        ord.del_date = request.form['del_date']
        ord.sender_name = request.form['sender_name']
        ord.rec_name = request.form['rec_name']
        ord.rec_address = request.form['rec_address']
        log = action_log(
            order_id=ord.id, action_type="edited", perf_by="admin"
        )
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('view_orders'))

    return f"""
    <h2>Edit Order {ord.id}</h2>
    <form method='POST'>
        Item No: <input name='item_no' value='{ord.item_no}'><br>
        Delivery Date: <input name='del_date' value='{ord.del_date}'><br>
        Sender Name: <input name='sender_name' value='{ord.sender_name}'><br>
        Recipient Name: <input name='rec_name' value='{ord.rec_name}'><br>
        Recipient Address: <input name='rec_address' value='{ord.rec_address}'><br>
        <input type='submit' value='Update'>
    </form>
    """

@Ordersapp.route('/orders/add', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        new_order = order(
            item_no=request.form['item_no'],
            del_date=request.form['del_date'],
            sender_name=request.form['sender_name'],
            rec_name=request.form['rec_name'],
            rec_address=request.form['rec_address'] 
        )
        db.session.add(new_order)
        db.session.commit()

        log = action_log(
            order_id=new_order.id,
            action_type="added",
            perf_by="admin"
        )
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('view_orders'))

    return """
    <h2>Add New Order</h2>
    <form method='POST'>
        Item No: <input name='item_no'><br>
        Delivery Date: <input name='del_date'><br>
        Sender Name: <input name='sender_name'><br>
        Recipient Name: <input name='rec_name'><br>
        Recipient Address: <input name='rec_address'><br>
        <input type='submit' value='Add'>
    </form>
    """
if __name__ == '__main__':
    with Ordersapp.app_context():
        db.create_all()
    Ordersapp.run(debug=True)
