# orders.py

from flask import Blueprint, jsonify, request, session
from sqlalchemy import or_, select
from api.services.billing import generate_bill
from api.auth import role_required, token_required
from utils.db import SessionLocal
from utils.models import Author, Book, Order, OrderLine, User

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


@orders_bp.route("/", methods=["GET"])
@token_required
@role_required("Manager")
def get_orders(context):
    status = request.args.get("status")
    if status not in [None, "pending", "completed", "cancelled"]:
        return jsonify({"error": "Invalid status filter"}), 400
    
    page_number = request.args.get("page_number", 1, type=int)
    page_size = request.args.get("page_size", 100, type=int)
    session = SessionLocal()

    filters = []
    try:
        if status:
            filters.append(Order.payment_status == status)
        
        orders = session.query(Order).order_by(Order.id).filter(*filters).offset((page_number - 1) * page_size).limit(page_size).all()
    
        orders_list = []
        for o in orders:
            order_lines = [{"id": ol.id, "book_id": ol.book_id, "type": ol.type, "price": ol.price} for ol in o.order_lines]
            orders_list.append({"id": o.id, "user_id": o.user_id, "total_price": o.total_price, "payment_status": o.payment_status, "order_lines": order_lines, "order_date": o.order_date, "email_sent": o.email_sent})

        return jsonify({"orders": orders_list, "page": {
            "current_page": page_number,
            "total_pages": (session.query(Order).filter(*filters).count() + page_size - 1) // page_size,
        }})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        session.close()


@orders_bp.route("/<int:id>", methods=["GET"])
@token_required
@role_required("Manager")
def get_order_details(context, id):
    session = SessionLocal()
    try:
        order = session.get(Order, id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        order_lines = [{"id": ol.id, "book_id": ol.book_id, "type": ol.type, "price": ol.price} for ol in order.order_lines]
        order_data = {"id": order.id, "user_id": order.user_id, "total_price": order.total_price, "payment_status": order.payment_status, "order_lines": order_lines, "order_date": order.order_date, "email_sent": order.email_sent}

        return jsonify(order_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@orders_bp.route("/create_order", methods=["POST"])
@token_required
@role_required("Customer")
def create_order(context):
    data = request.json
    user_id = context['id']
    order_lines_data = data.get("order_lines", [])

    session = SessionLocal()
    try:
        # Calculate each order line price from book prices and type
        for ol in order_lines_data:
            book = session.get(Book, ol['book_id'])
            if not book:
                return jsonify({"error": f"Book with id {ol['book_id']} not found"}), 404
            # Update book status to 'sold' or 'rented' based on order line type
            if ol['type'] == 'buy':
                ol['price'] = float(book.price_buy)
                book.status = 'sold'
            elif ol['type'] == 'rent':
                ol['price'] = float(book.price_rent)
                book.status = 'rented'
            else:
                return jsonify({"error": f"Invalid order line type '{ol['type']}' and book id {ol['book_id']}"}), 400
            
        total_price = sum(ol['price'] for ol in order_lines_data)
        new_order = Order(user_id=user_id, total_price=total_price)
        session.add(new_order)
        session.flush()  # Ensure new_order.id is available

        for ol_data in order_lines_data:
            new_order_line = OrderLine(order_id=new_order.id, book_id=ol_data['book_id'], type=ol_data['type'], price=ol_data['price'])
            session.add(new_order_line)

        session.commit()
        # Generate bill after order creation
        bill_html = generate_bill(new_order, new_order.order_lines)
        return jsonify({"message": "Order created successfully", "order_id": new_order.id, "bill": bill_html}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@orders_bp.route("/<int:id>/status", methods=["PATCH"])
@token_required
@role_required("Manager")
def update_order_status(context, id):
    data = request.json
    new_status = data.get("status")

    session = SessionLocal()
    try:
        order = session.get(Order, id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        order.payment_status = new_status
        session.commit()
        return jsonify({"message": "Order status updated successfully"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()