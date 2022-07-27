import random,os, requests,json
#3rd Party import

from flask import render_template, redirect, request,flash,session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

#local import
from weddingapp import app, db
from weddingapp.forms import ContactForm, SignupForm
from weddingapp.models import Contact, Gifts, Guest_gift, Guests, Comment, Lga,State,Uniform,Orders, Order_details, Payment

@app.route('/accommodation')
def accommodation():  
    
    username="weddingapp"
    password = "1111"
    try:
        rsp = requests.get("http://127.0.0.1:8080/api/v1.0/getall",verify=False, auth=(username,password))
        rsp_json= rsp.json()#converts rsp from HTTP response to json
        return render_template('user/accommodation.html', rsp_json=rsp_json)
    except:
        return "Plesae Try again , the server on the other end is down..."


@app.route('/')
def home():  
    return render_template('user/index.html')

def get_price(itemid):
    deets = Uniform.query.get(itemid)
    if deets != None:
        return deets.uni_price
    else:
        return 0

def generate_ref():
    ref = random.random() *10000000
    return int(ref)


@app.route('/paystack_landing')
def paystack_landing():
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
    else:
        pay = Payment(pay_orderid=1,pay_guestid=loggedin,pay_amt=actual_amt,pay_status='Failed')
        db.session.add(pay)
        db.session.commit()
        return "Failed, try again"


@app.route('/initialize_paystack')
def initialize_paystack():
    #connect to paystack and send amount,email, reference, key
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


@app.route('/confirmation')
def confirmation():
    loggedin = session.get("guest")
    ref = session.get('reference')
    if loggedin != None:
        deets = Orders.query.join(Order_details,Orders.order_id==Order_details.det_orderid).join(Uniform,Order_details.det_itemid==Uniform.uni_id).filter(Orders.order_by == loggedin,Orders.order_ref==ref).add_columns(Order_details,Uniform).all()

        t = Orders.query.filter(Orders.order_ref==ref).first()

        return render_template('user/confirmation_page.html',deets=deets,total=t.order_totalamt)
    else:
        return redirect('/login')





@app.route('/asoebi', methods=['POST','GET'])
def asoebi():
    loggedin = session.get("guest")
    if loggedin != None:
        if request.method=='GET':
            uni = db.session.query(Uniform).all()
            return render_template('user/aso_ebi.html', uni=uni)
        else:
            uniform_selected = request.form.getlist('uniform')
            if uniform_selected:
                #insert into order table
                ref= generate_ref()
                session['reference'] = ref
                ord = Orders(order_by=loggedin,order_status='Pending',order_ref=ref)  
                
                db.session.add(ord)   
                db.session.commit() 

                #insert into order_details
                orderid = ord.order_id
                total = 0
                for i in uniform_selected:
                    price = get_price(i)
                    ord_det = Order_details(det_orderid=orderid,det_itemid=i,det_itemprice=price)
                    total = total + price
                    db.session.add(ord_det)
                
                ord.order_totalamt = total

                #insert into payment table too
                p = Payment(pay_orderid=ord.order_id,pay_guestid=loggedin,pay_amt=total,pay_ref=ref,pay_status='Pending')
                db.session.add(p)
                #commit all changes on all tables (orders,order_details,payment) to the db
                db.session.commit()

                return redirect('/confirmation')
            else:
                flash('Please make a selection')
                return redirect('/asoebi')
    else:
        return redirect('/login')





@app.route('/user/edit')
def edit_user_profile():
    loggedin = session.get("guest")
    if loggedin != None:
        guest_deets = db.session.query(Guests).filter(Guests.guest_id==loggedin).first()
        return render_template('user/editprofile.html',guest_deets=guest_deets)
    else:
        return redirect("/")



@app.route('/user/upload')
def upload_pix():
    loggedin = session.get("guest")
    guest_deets = db.session.query(Guests).get(loggedin)
    if loggedin != None:
        return render_template("user/upload_profile.html",guest_deets=guest_deets) 
    else:
        return redirect("/login")



@app.route('/user/submit_upload', methods=["POST"])
def submit_upload():
    loggedin = session.get("guest")
    if loggedin != None:
        #retrieve for data and upload 
        if request.files != "":
            allowed = ['.jpg',".png",".jpeg"]
            fileobj = request.files['profilepix'] 
            original_filename = fileobj.filename #dont use this,it can clash
            newname = random.random() * 100000000
            picturename, ext = os.path.splitext(original_filename) #splits file into 2 parts on the extension

            if ext in allowed:
                path = "weddingapp/static/uploads/"+str(newname)+ext
                fileobj.save(f"{path}")

                deets = db.session.query(Guests).get(loggedin)
                deets.guest_image = str(newname)+ext
                db.session.commit()
                flash("Image successfully uploaded") 
            else:
                flash("Invalid Format") 
            return redirect('/profile')            
        else:
            flash("Please select a valid image")
            return redirect('/user/upload')              
    else:
        return redirect("/login")
    



@app.route('/user/update',methods=['POST'])
def update_user():
    loggedin = session.get("guest")
    if loggedin != None:
        fname = request.form['fname']
        lname = request.form['lname']
        address = request.form['address']
        record = db.session.query(Guests).get(loggedin)
        record.guest_fname = fname
        record.guest_lname = lname
        record.guest_address = address
        db.session.commit()
        flash('Details updated!')
        return redirect('/profile') 
    else:
        return redirect('/login')

@app.route('/message')
def message_us():
    cform = ContactForm()
    return render_template('user/contactus.html', cform=cform)


@app.route('/submitcontact', methods=["POST"])
def insert_message():
    cform = ContactForm()
    if cform.validate_on_submit():
        fname = request.form['fullname']
        email = request.form['email']
        msg = request.form['message']
        # Insert into DB using the models class
        contact = Contact(con_fullname=fname,con_email=email,con_message=msg)
        db.session.add(contact)
        db.session.commit()
        flash('Message sent!')
        return redirect('/')
    else:
        return render_template('user/contactus.html',cform=cform)





@app.route('/registry')
def gift_registry():
    loggedin = session.get("guest")
    if loggedin != None:
        promised_gifts = []

        promised = db.session.query(Guest_gift).filter(Guest_gift.g_guestid==loggedin).all()
        if promised:
            for p in promised:
                promised_gifts.append(p.g_giftid)

        gifts = db.session.query(Gifts).all()
        return render_template("user/gift_registry.html", gifts=gifts,promised_gifts=promised_gifts)
    else:
        flash("You need to be logged")
        return redirect("/login")



@app.route('/ajaxtests/final', methods=['POST'])
def final_test():
    appended_data = request.form.get('missing')
    firstname = request.form['firstname']
    lastname = request.form['lastname']    
    
    #retrieve the file
    fileobj = request.files['image'] 
    original_filename = fileobj.filename 
    fileobj.save(f'weddingapp/static/images/{original_filename}')
    
    #insert into guest table
    return jsonify(firstname=firstname,lastname=lastname,appended_data=appended_data,filename=original_filename)
















@app.route('/submit/registry', methods=['POST'])
def submit_registry():
    loggedin = session.get("guest")
    if loggedin != None:
        selected = request.form.getlist('selected_gift') 
        db.session.execute(f"DELETE FROM guest_gift WHERE g_guestid='{loggedin}'") 
        db.session.commit()  

        for s in selected: #[2,6]
            gg = Guest_gift()
            db.session.add(gg)
            gg.g_giftid = s
            gg.g_guestid = loggedin
            db.session.commit()
        flash('Thank you. Gifts recorded')
        return redirect('/registry')
    else:
        flash("You need to be logged")
        return redirect("/login")
    


@app.route('/forum')
def forum():
    #create form forum.html with a textarea.
    return render_template('user/forum.html')

#Below are for ajax demo:
@app.route('/ajaxtests')
def ajaxtests():
    s = db.session.query(State).all()
    return render_template('user/testing.html', s=s)


@app.route('/ajaxtests/state')
def ajaxtests_state():
    selected=request.args.get('stateid')
    #write a query to fetch all LGAs where state_id == selected
    lgas = db.session.query(Lga).filter(Lga.state_id == selected).all()

    retstr= ""
    for i in lgas:
        retstr = retstr + f"<option value='{i.lga_id}'>{i.lga_name}</option>"

    return retstr











@app.route('/ajaxtests/checkusername', methods=['POST','GET'])
def ajaxtests_submit():
    user = request.values.get('username') #whether post/get
    #to do run a query to check guest table if email exists
    chk = db.session.query(Guests).filter(Guests.guest_email==user).first()
    if chk != None:
        return "<span class='alert alert-danger'>Username has been taken</span>"
    else:
        return "<span class='alert alert-success'>Username is available</span>"








@app.route('/send_forum',methods=['POST'])
def sendforum():
    loggedin = session.get('guest')
    if loggedin != None:
        d = request.form.get('suggestion')
        c = Comment(comment_guest=loggedin,comment_content=d)
        db.session.add(c)
        db.session.commit()
        if c.comment_id > 0:
            return "Thank you for posting your comment"            
        else:
            return "Please Try again"
    else:
        return "You need to be logged in to post a comment"














@app.route('/signup', methods=["POST","GET"])
def signup():
    sign = SignupForm()
    if request.method =="GET":
        return render_template('user/signup.html', sign=sign)
    else:
        if sign.validate_on_submit():
            fname = sign.firstname.data #request.form["firstname"]
            lname = request.form["lastname"]
            email = request.form["email"]
            password = request.form["password"]

            # from werkzeug.security import generate_password_hash, check_password_hash

            hashed = generate_password_hash(password)
            # insert to db
            g = Guests(guest_fname=fname,guest_lname=lname,guest_email=email,guest_pwd=hashed,guest_image="")



            db.session.add(g)
            db.session.commit()
            guestid = g.guest_id #retrieve the guestid
            session["guest"] = guestid #save the id in session so that u can use it elsewhere
            return redirect("/profile")        
        else:
            return render_template('user/signup.html', sign=sign)



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


@app.route('/test')
def random_route():
    return render_template('user/testing.html')


@app.route('/profile')
def user_profile():
    loggedin = session.get("guest")
    if loggedin != None:
        guest_deets = db.session.query(Guests).filter(Guests.guest_id==loggedin).first()
        return render_template('user/profile.html', guest_deets=guest_deets)
    else:
        flash("You must be logged in to view this page")
        return redirect("/login")

@app.route('/user/logout')
def user_logout():
    session.pop("guest",None)
    return redirect("/")