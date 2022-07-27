from datetime import datetime
import enum
from weddingapp import db 

class Payment_status(enum.Enum):
    Paid="Paid"
    Pending="Pending"
    Failed="Failed"
class Payment(db.Model): 
    pay_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    pay_orderid = db.Column(db.Integer(), db.ForeignKey('orders.order_id'))
    pay_guestid = db.Column(db.Integer(), db.ForeignKey('guests.guest_id'))
    pay_amt =db.Column(db.Float(), nullable=False)
    pay_ref=db.Column(db.String(50), nullable=True)
    pay_date=db.Column(db.DateTime(), default=datetime.utcnow())
    pay_status=db.Column(db.Enum(Payment_status))
    pay_mode =db.Column(db.String(255), nullable=True)
    pay_feedback = db.Column(db.String(255), nullable=True)

 
class Orders(db.Model): 
    order_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    order_by = db.Column(db.Integer(), db.ForeignKey('guests.guest_id'))
    order_status =db.Column(db.Enum('Completed','Pending'), nullable=False)
    order_ref = db.Column(db.String(50), nullable=False)
    order_totalamt =db.Column(db.Float(), nullable=True)
    order_date=db.Column(db.DateTime(), default=datetime.utcnow())
    
class Order_details(db.Model): 
    det_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    det_orderid = db.Column(db.Integer(), db.ForeignKey('orders.order_id'))
    det_itemid = db.Column(db.Integer(), db.ForeignKey('uniform.uni_id'))
    det_itemprice =db.Column(db.Float(), nullable=False)



class Guests(db.Model): 
    guest_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    guest_fname =db.Column(db.String(50), nullable=False)
    guest_lname =db.Column(db.String(50), nullable=False)
    guest_email=db.Column(db.String(80), nullable=False)
    guest_image= db.Column(db.String(80), nullable=True)
    guest_address= db.Column(db.Text(), nullable=True)
    guest_pwd =db.Column(db.String(255), nullable=False)
    guest_regdate=db.Column(db.DateTime(), default=datetime.utcnow())
    #dgifts =db.relationship("Guest_gift", back_populates="guest_deets")

    
class Uniform(db.Model):
    #columname=db.Column(db.datatype())
    uni_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    uni_name =db.Column(db.String(50), nullable=False)
    uni_price =db.Column(db.Float(), nullable=False)
