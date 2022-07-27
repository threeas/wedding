import random,os, requests,json
#3rd Party import

from flask import render_template, redirect, request,flash,session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

#local import
from weddingapp import app, db
from weddingapp.forms import ContactForm, SignupForm
from weddingapp.models import Contact, Gifts, Guest_gift, Guests, Comment, Lga,State,Uniform,Orders, Order_details, Payment

# Here are utility functions that we can call from any part of the route
def get_price(itemid):
    """Given an id, it fetches the price of uniform"""
    deets = Uniform.query.get(itemid)
    if deets != None:
        return deets.uni_price
    else:
        return 0

def generate_ref():
    """It generates a random string of number"""
    ref = random.random() *10000000
    return int(ref)



# The starting point, this route displays the available uniform for sale
@app.route('/asoebi', methods=['POST','GET'])
def asoebi():
    loggedin = session.get("guest")
    if loggedin != None:
        if request.method=='GET':
            uni = db.session.query(Uniform).all()
            return render_template('user/aso_ebi.html', uni=uni)
        else:
            uniform_selected = request.form.getlist('uniform') #checkboxes
            if uniform_selected:
                #STEP1: insert into order table
                ref= generate_ref()
                session['reference'] = ref
                ord = Orders(order_by=loggedin,order_status='Pending',order_ref=ref)  
                
                db.session.add(ord)   
                db.session.commit() 

                #STEP2: insert each of the item into order_details
                orderid = ord.order_id
                total = 0 #get total amount & use it to update orders table
                for i in uniform_selected:
                    price = get_price(i)

                    ord_det = Order_details(det_orderid=orderid,det_itemid=i,det_itemprice=price)

                    total = total + price
                    db.session.add(ord_det)
                
                ord.order_totalamt = total #update orders

                #insert into payment table too and set status to pending
                p = Payment(pay_orderid=ord.order_id,pay_guestid=loggedin,pay_amt=total,pay_ref=ref,pay_status='Pending')
                db.session.add(p)

                #commit all changes on all tables (orders,order_details,payment) to the db
                db.session.commit()

                return redirect('/confirmation') #display all the things we captured back to the user on this page for confirmation b4 we tell him to pay
            else:
                flash('Please make a selection')
                return redirect('/asoebi')
    else:
        return redirect('/login')

@app.route('/confirmation')
def confirmation():
    loggedin = session.get("guest")
    ref = session.get('reference')
    if loggedin != None:
        # we are joining several tables below in order to get details available on all these tables because we did not set relationship(s)

        deets = Orders.query.join(Order_details,Orders.order_id==Order_details.det_orderid).join(Uniform,Order_details.det_itemid==Uniform.uni_id).filter(Orders.order_by == loggedin,Orders.order_ref==ref).add_columns(Order_details,Uniform).all() 

        # we want to get the amount as stored on orders table so that we can display total amount
        t = Orders.query.filter(Orders.order_ref==ref).first()

        return render_template('user/confirmation_page.html',deets=deets,total=t.order_totalamt)
    else:
        return redirect('/login')


""" This route will be visited from confirmation_page.html"""

@app.route('/initialize_paystack')
def initialize_paystack():
    #connect to paystack and send amount,email, reference, pk_key(as authorization), paystack will respond back with the the url where you will direct user to in order to supply their card details

    loggedin = session.get('guest')
    if loggedin != None:
        ref = session.get('reference')
        a = db.session.query(Orders).filter(Orders.order_ref==ref).first()
        g = db.session.query(Guests).get(loggedin)
        
        data = {"email":g.guest_email,"amount":a.order_totalamt*100, "reference":ref}
        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_3c5244cfb8965dd000f07a4cfa97185aab2e88d5"}
        response = requests.post("https://api.paystack.co/transaction/initialize",headers=headers, data=json.dumps(data))
        rsp_json = response.json()
        if rsp_json['status'] == True:
            url = rsp_json['data']['authorization_url']
            return redirect(url)
        else:
            return 'Please try again'
    else:
        return redirect('/login')


@app.route('/paystack_landing')
def paystack_landing():
    """This route would have been configured in the paystack developer dashboard, this is where user would be redirected to after inputing their card details, here you will confirm the transaction status and update your db accordingly"""

    loggedin = session.get('guest')
    ref = request.args.get('reference')
    headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_3c5244cfb8965dd000f07a4cfa97185aab2e88d5"}
    response = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers)
    rsp_json = response.json() 
    #uncomment this out to see the structure of what paystack returns, then you would be able to pick what you need
    #return rsp_json 
    
    if rsp_json['status'] == True: 
        data = rsp_json['data']
        actual_amt = data['amount']/100
        feedback = data['gateway_response']
        #update payment table
        pay = Payment.query.filter(Payment.pay_ref==ref).first()
        pay.pay_status = 'Paid'
        pay.pay_feedback =feedback
        db.session.commit()
        return "Successfully Paid"  
        # or direct the user to their dashboard where they would see their transaction history as Paid
    else:
        pay = Payment(pay_orderid=1,pay_guestid=loggedin,pay_amt=actual_amt,pay_status='Failed')
        db.session.add(pay)
        db.session.commit()
        return "Failed, try again"

"""Miscellanoues"""
@app.route('/login', methods=["POST","GET"])
def login():
    if request.method =="GET":
        return render_template('user/login.html')
    else:
        email = request.form["email"]
        password = request.form["password"]
        #retrieve the hashed password belonging to this user
        userdeets = Guests.query.filter(Guests.guest_email==email).first()
        if userdeets and check_password_hash(userdeets.guest_pwd, password):
            session["guest"] = userdeets.guest_id
            return redirect("/profile")
        else:
            flash("Invalid Credentials")
            return redirect("/login")




@app.route('/profile')
def user_profile():
    """See the implementation method of paystack with js pop up on this html template"""
    loggedin = session.get("guest")
    if loggedin != None:
        guest_deets = db.session.query(Guests).filter(Guests.guest_id==loggedin).first()
        return render_template('user/profile.html', guest_deets=guest_deets)
    else:
        flash("You must be logged in to view this page")
        return redirect("/login")