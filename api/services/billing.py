from flask import render_template

def generate_bill(order, order_lines):
    return render_template("bill.html", order=order, order_lines=order_lines)