#3rd Party import
from flask import render_template, redirect, request,flash,session,url_for
#local import
from weddingapp import app, db,csrf
from weddingapp.models import *

@app.after_request
def after_request(response):
    response.headers["Cache-Control"]="no-cache,no-store,must-revalidate"
    return response 


@app.route('/admin/edit/<id>')
def edit(id):
    deets = Gifts.query.get(id)
    return render_template('admin/edit_gift.html', deets=deets)

@app.route('/admin/update', methods=['POST'])
def update_gift():
    #retrieve form data
    newname = request.form['giftname']
    id = request.form["id"]
    gift = db.session.query(Gifts).get(id)
    gift.gift_name=newname
    db.session.commit()
    flash("Gift was successfully updated")
    return redirect(url_for("manage_gifts"))




@app.route('/admin/delete/<id>')
def delete_gift(id):
    #delete
    x = db.session.query(Gifts).get(id)
    db.session.delete(x)
    db.session.commit()
    flash('Gift Deleted!')
    return redirect(url_for('manage_gifts'))
    

@app.route('/admin/guests')
def manage_guests():
    #Protect this pg for only logged in admin#
    if session.get('adminid') != None and session.get('adminname')!= None:
        guests = db.session.query(Guests).all()
        return render_template('admin/all_guests.html', guests=guests)
    else:
        return redirect('/admin')


@app.route('/admin/managegifts')
def manage_gifts():
    #Protect this pg for only logged in admin#
    if session.get('adminid') != None and session.get('adminname')!= None:
        gifts = db.session.query(Gifts).order_by(Gifts.gift_id.desc()).offset(1).limit(2).all()
        return render_template('admin/all_gifts.html', gifts=gifts)
    else:
        return redirect('/admin')



@app.route('/admin/add/gift', methods=['GET','POST'])
def add_gift():
    if session.get('adminid') != None and session.get('adminname')!= None:
        if request.method =='GET':
            return render_template('admin/newgift.html')#create this page with input field to insert gift item
        else:
            #retrieve form data (giftname), insert into db, redirect to
            #the gift listing page (/admin/managegifts)
            giftname = request.form['giftname']
            #add: instantiate an obj of d model, add to session, commit
            g = Gifts(gift_name=giftname)
            db.session.add(g)
            db.session.commit()
            if g.gift_id > 0:#see all gift
                return redirect(url_for('manage_gifts'))
            else:
                flash("It wasnt added, plesae try again")
                return redirect(url_for('add_gift'))
    else:
        flash('Invalid credentials')
        return redirect('/admin')










@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('adminid') != None and session.get('adminname')!= None:
        return render_template('admin/admin_dashboard.html')
    else:
        flash('Invalid credentials')
        return redirect('/admin')
        


@app.route('/admin', methods=['POST','GET'])
@csrf.exempt
def admin_home():
    if request.method=='GET':
        return render_template('admin/admin_login.html')
    else:
        #form submitted, retrieve form data,check in the db if its correct, 
        #set something inside the session and redirect to the dashboard
        username = request.form['username']
        pwd = request.form['pswd']

        ad = Admin.query.filter(Admin.admin_username==username,Admin.admin_pwd==pwd).first() 
        if ad:
            adminid = ad.admin_id 
            admin_fullname = ad.admin_name
            session['adminid'] = adminid  
            session['adminname']  = admin_fullname
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
            return redirect('/admin')



@app.route('/admin/logout')
def admin_logout():
    session.pop('adminid',None)
    session.pop('adminname',None)
    #TO DO: implement logout and redirect them to login page (/admin)
    return redirect('/admin')

