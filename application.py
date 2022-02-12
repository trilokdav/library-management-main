from flask import *
from flaskext.mysql import MySQL
from random import *
from datetime import *
from datetime import datetime
from datetime import date
import os
import string
import requests
import math
import time
import requests
import json

app = Flask(__name__,template_folder ='template')



app.secret_key = os.urandom(34)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'lallantiwari'
app.config['MYSQL_DATABASE_DB'] = 'frappe'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql = MySQL(app)



#--------------------------------------------------------------------------------------------------

#MySQL Query Driver function

#Query can be directly passed as an argument without setting the coonection and committing the output

def mysql_query(sql):
	connection = mysql.connect()
	cursor = connection.cursor()
	if sql.strip().split(' ')[0].lower() == "select" :
		print(sql)
		cursor.execute(sql)
		print(cursor._executed)
		
		columns = [column[0] for column in cursor.description]
		results = []
		for row in cursor.fetchall():
			results.append(dict(zip(columns, row)))
		data = results
		cursor.close()
		connection.close()
		return data
	if sql.strip().split(' ')[0].lower() != "select" :
		cursor.execute(sql)
		print(cursor._executed)
		connection.commit()
		cursor.close()
		connection.close()
		return None

# How to use this function
# --> mysql_query("Select * from user_master;")
# --> mysql_query(" select * from user_master where emailid='{}';".format(email))

#Mysql Function Ended 

#--------------------------------------------------------------------------------------------



#---------------------------------------------------------------------------------------------

#Code For Library management 

#----------------------------------------------------------------------------------------------


#********************************************************************************************

#Function to display and import book details

@app.route('/',methods=['GET','POST'])
def book():
	bdata=mysql_query("SELECT * from books")
	if request.method=="POST":
		#----------------------------------------------------------------------------------------
		#add button for importing data from api
		if 'add' in request.form:
			#using try-catch statement for catching any exception
			try:
				no=request.form['nbooks']
				#converting the string value to integer
				no=int(no)
				#--------------------------------------
				title=request.form['title']
				author=request.form['author']
				isbn=request.form['isbn']
				pub=request.form['publisher']
				full_data=[]
				#Calculating how many time api should run 
				page=no/20
				bno=math.ceil(page)	
				#----------------------------------------
				#loop for importing data as per requirement and appending it into a list
				for i in range(1,bno+1):
					data=[]
					req=requests.get("https://frappe.io/api/method/frappe-library?page={}&title={}&authors={}&isbn={}&publisher={}".format(i,title,author,isbn,pub))
					data=req.json()
					full_data.append(data)
				#loop for iterating through the data fetched from the api
				for x in full_data:
					for i in range(0,no):
						bid=x['message'][i]['bookID']
						print(bid)
						#checking if the imported value already exists in the database or not
						check=mysql_query("SELECT book_id from books where book_id={}".format(bid))
						#if the details does not exists in the database
						if len(check)==0:
							connection = mysql.connect()
							cursor = connection.cursor()
							#Using normal cursor connection instead of mysql function for escaping aphostrphes
							#---------------------------------------------------------------------------------
							sql="INSERT INTO books(book_id,title,authors,average_rating,isbn,isbn13,language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
							#Date converted into yyyy-mm-dd fromat
							time=datetime.strptime(x['message'][i]['publication_date'],'%m/%d/%Y')
							sqldt=(x['message'][i]['bookID'],x['message'][i]['title'],x['message'][i]['authors'],x['message'][i]['average_rating'],x['message'][i]['isbn'],x['message'][i]['isbn13'],x['message'][i]['language_code'],x['message'][i]['  num_pages'],x['message'][i]['ratings_count'],x['message'][i]['text_reviews_count'],time,x['message'][i]['publisher'])
							cursor.execute(sql,sqldt)
							connection.commit()
						#-------------------------------------------------------------------------------------			
						#Stock Management is done through the api data :- Depending of the repeated details			
						#If the details exists in the database
						else:
							#if the details exists then the stock of the book will be increamented by 1
							mysql_query("UPDATE books set stock=stock+1 where book_id={}".format(bid))
							mysql_query("UPDATE books set total=total+1 where book_id={}".format(bid))
					#flash is used to give notification or warning to the user by flashing the entered message with its category
					flash('Books Data fetched Successfully','success')
				return redirect(url_for('book'))
			except:
				flash('Sufficient data was not found','warning')
				return redirect(url_for('book'))
		#----------------------------------------------------------------------------------------		
		#Del button for deleting data from database 
		if 'del' in request.form:
			bid=request.form['del']
			#fetching return dates of issued books
			tdata=mysql_query("SELECT return_date from transaction where book_id={}".format(bid))
			#-------------------------------------
			#if the book is not reuturned than its details cannot be deleted
			if len(tdata)==0:
				flash('Cannot Delete ! Book is Already Issued ','warning')	
			#if the book is returned then the details can be deleted	
			else:
				mysql_query("DELETE from books where book_id={}".format(bid))
				flash('Book Data Deleted Successfully !','success')		
			return redirect(url_for('book'))
		#----------------------------------------------------------------------------------------
		#Update button for updating books details
		if 'update' in request.form:
			bid=request.form['update']
			title=request.form['title']
			author=request.form['author']
			arating=request.form['rating']
			isbn=request.form['isbn']
			isbn13=request.form['isbn13']
			lcode=request.form['lcode']
			npage=request.form['pages']
			rcount=request.form['rcount']
			treview=request.form['treview']
			pdate=request.form['pdate']
			pub=request.form['publisher']
			connection = mysql.connect()
			cursor = connection.cursor()
			query="UPDATE books set title=%s,authors=%s,average_rating=%s,isbn=%s,isbn13=%s,language_code=%s,num_pages=%s,ratings_count=%s,text_reviews_count=%s,publication_date=%s,publisher=%s where book_id=%s"
			values=(title,author,arating,isbn,isbn13,lcode,npage,rcount,treview,pdate,pub,bid)
			cursor.execute(query,values)
			connection.commit()
			return redirect(url_for('book'))

	return render_template('book_details.html',bdata=bdata)


#**********************************************************************************************

#Function for displaying member details

@app.route('/member_details',methods=['GET','POST'])
def member():
	mdata=mysql_query("SELECT * from members")
	#----------------------------------------------------------------------------------------
	#del button for deleting the member data from the database
	if request.method=="POST":
		if 'del' in request.form:
			mid=request.form['del']
			check=mysql_query("SELECT book_id from transaction where member_id={} and return_date is Null".format(mid))
			if len(check)==0:
				mysql_query("DELETE from members where members.member_id={}".format(mid))
				flash('Member Delete Successfully !','success')
			else:
				flash('Cannot Delete Member ! Issued book is not returned','danger')
			return redirect(url_for('member'))
		#----------------------------------------------------------------------------------------	
		#update for updating member Data into the database
		if 'update' in request.form:
			mid=request.form['update']
			name=request.form['name']
			phone=request.form['number']
			address=request.form['address']
			mysql_query("UPDATE members SET member_name='{}',member_phone={},member_address='{}' where member_id={}".format(name,phone,address,mid))
			flash('Member Details Updated Successfully !','success')
			return redirect(url_for('member'))
		#----------------------------------------------------------------------------------------	
		#add button for adding new member into the database
		if 'add' in request.form:
			name=request.form['name']
			phone=request.form['number']
			email=request.form['email']
			address=request.form['address']
			#Checking if details are already available in the database or not
			edata=mysql_query("SELECT member_id from members where member_email='{}' OR member_phone='{}' ".format(email,phone))
			#---------------------------------------------------------------------
			#If details does not exists than new member will be added to the database
			if len(edata)==0:
				mysql_query("INSERT INTO members(member_name,member_phone,member_address,member_email) value('{}',{},'{}','{}')".format(name,phone,address,email))
				flash('Member Registered Successfully !','success')	
			#if details already exists than it will give a warning
			else:
				flash('Member Already Exists !','warning')
			return redirect(url_for('member'))
		#----------------------------------------------------------------------------------------	
		#Settle button to settle the outstanding amount of the member
		if 'settle' in request.form:
			amount=request.form['amount']
			mid=request.form['member']
			print(amount)
			mysql_query("UPDATE members set outstanding_amount=outstanding_amount-{},total_amount=total_amount+{} where member_id={}".format(amount,amount,mid))
			flash('Outstanding Amount Settled Successfully !', 'success')
			return redirect(url_for('transaction'))

	return render_template('member_details.html',mdata=mdata)


#************************************************************************************************

#Function For managing book issue and return

@app.route('/book_issued',methods=['GET','POST'])
def transaction():
	tdata=mysql_query("SELECT * from transaction join members using(member_id) join books using(book_id) order by transaction_id DESC")
	mdata=mysql_query("SELECT * from members")
	bdata=mysql_query("SELECT * from books")
	#----------------------------------------------------------------------------------------
	if request.method=="POST":
		#issueb button for issuing book to the members
		if "issueb" in request.form:
			name=request.form['name']
			book=request.form['book']
			tdate=date.today()
			#After fetching the details checking if the required book is in stock or not
			bstock=mysql_query("SELECT stock from books where book_id={}".format(book))
			#Checking the outstanding amount of the member who is issuing the book
			outstanding=mysql_query("SELECT outstanding_amount from members where member_id={}".format(name))
			#Checking if the earlier issued book is returned or not
			returnb=mysql_query("SELECT return_date from transaction where member_id={} order by transaction_id DESC limit 1".format(name))
			noissue=mysql_query("SELECT transaction_id from transaction where member_id={}".format(name))
			#condition to check if the book is in stock
			if bstock[0]['stock']>=1:
				#Earlier issued book is returned or not, or no book is issued yet
				if len(noissue)==0 or returnb[0]['return_date'] is not None:
					#if the oustanding amount is less than 500 or not
					if outstanding[0]['outstanding_amount']<500:
						#if the user meets all the condition then the book will be issued
						mysql_query("INSERT INTO transaction(book_id,member_id,issue_date) values({},{},'{}')".format(book,name,tdate))
						mysql_query("UPDATE books set stock=stock-1 where book_id={}".format(book))
						flash("Book Issued Successfully !",'success')					
					#Flashing message for exceeding outstanding amount	
					else :
						flash('Outstanding amount is exceeding Rs.500','warning')	
				#Flashing message for book not returned
				else:
					flash('Prior issued book is not returned','warning')		
			#Flashing message for book is out of stock
			else:
				flash('Book is out of stock', 'warning')	
			return redirect(url_for('transaction'))
		#----------------------------------------------------------------------------------------	
		#return button for returning the book
		if 'return' in request.form:
			tid=request.form['return']
			bid=request.form['book']
			mid=request.form['member']
			rdate=date.today()
			rent=request.form['rent']
			paid=request.form['paid']
			mid=request.form['member']
			#checking if the book rent is paid at the time of returning the book or not
			#--------------------------------------------------------------------------
			#If the rent is paid at the time of returning book
			if paid=="yes":
				#return date is set
				mysql_query("UPDATE transaction set return_date='{}',rent={},rent_paid='{}' where transaction_id={}".format(rdate,rent,paid,tid))	
				#the total amount paid by user will be updated
				mysql_query("UPDATE members set total_amount=total_amount+{} where member_id={}".format(rent,mid))				
				#updating the book stocks
				mysql_query("UPDATE books set stock=stock+1 where book_id={}".format(bid))
				flash('Book returned Successfully and rent is paid', 'success')
			#if the rent is not paid at the time of returning the book
			elif paid=="no":
				#outstanding amount is fechted from database
				amt=mysql_query("SELECT outstanding_amount from members where members.member_id={}".format(mid))
				rent1=int(rent)
				final_amt=rent1+amt[0]['outstanding_amount']
				#if the outstanding is getting greater the 500 when not paying the rent at the time
				#of the return then the book cannot be returned member has to settle the outstanding amount
				if final_amt<500:
					mysql_query("UPDATE transaction set return_date='{}',rent={} where transaction_id={}".format(rdate,rent,tid))
					mysql_query("UPDATE members set outstanding_amount=outstanding_amount+{} where member_id={}".format(rent,mid))
					flash('Book returned Successfully and rent is not paid', 'info')
					mysql_query("UPDATE books set stock=stock+1 where book_id={}".format(bid))
				else:
					flash('Cannot Return Book ! Outstanding amount is exceeding 500','danger')
			return redirect(url_for('transaction'))
		#----------------------------------------------------------------------------------------
		#settle button to settle the outstanding amount
		if 'settle' in request.form:
			amount=request.form['amount']
			tid=request.form['settle']
			mid=request.form['member']
			print(amount)
			mysql_query("UPDATE members set outstanding_amount=outstanding_amount-{},total_amount=total_amount+{} where member_id={}".format(amount,amount,mid))
			flash('Outstanding Amount Settled Successfully !','success')
			mysql_query("UPDATE transaction set rent_paid='yes' where member_id=(select member_id from members where outstanding_amount=0 and member_id={})".format(mid))
			return redirect(url_for('transaction'))

	return render_template('transaction_details.html',tdata=tdata,mdata=mdata,bdata=bdata)


#---------------------------------------------------------------------------------------------

#Code For Library management Ended

#----------------------------------------------------------------------------------------------


#**********************************************************************************************


#---------------------------------------------------------------------------------------------

#Code For Report generation

#----------------------------------------------------------------------------------------------


#Function for Generating reports

@app.route('/reports',methods=['GET','POST'])
def report():
	if request.method=="POST":
		if 'report1' in request.form:
			mname=[]
			tvalue=[]
			maxdata=mysql_query("SELECT * from members order by total_amount DESC")
			#converting values into list for the chart
			for x in maxdata:
				mname.append(x['member_name'])
				tvalue.append(x['total_amount'])
			return render_template('reports.html',maxdata=maxdata,mname=mname,tvalue=tvalue)
		#the most popular book is taken out on the total issued number 
		if 'report2' in request.form:
			tissue=[]
			bname=[]
			bookdata=mysql_query("SELECT b.book_id,b.title,b.authors,b.publication_date,b.stock,b.total,b.publisher,count(t.book_id) from transaction t,books b where b.book_id = t.book_id group by t.book_id order by count(t.book_id) DESC")
			#converting values into list for the chart
			for i in bookdata:
				tissue.append(i['count(t.book_id)'])
				bname.append(i['title'])
			return render_template('reports.html',bookdata=bookdata,tissue=tissue,bname=bname)
	return render_template('reports.html')


#---------------------------------------------------------------------------------------------

#Code For Report generation Ended

#----------------------------------------------------------------------------------------------


#**********************************************************************************************


#--------------------------------------------------------------------------------------------

# For accessing the login page and to view book details use '/login' after the local host address 

#---------------------------------------------------------------------------------------------
#Function for Guest view
@app.route('/login',methods=['GET','POST'])
def login():
	if request.method=="POST":
		if 'check' in request.form:
			email=request.form['email']
			data=mysql_query("SELECT member_id from members where member_email='{}'".format(email))
			if data:
				return redirect(url_for('checkbooks'))
			else:
				print("wrong data entered")
	return render_template('login.html')


#Function for showing book details for the guest view users
@app.route('/checkbooks',methods=['GET','POST'])
def checkbooks():
	bdata=mysql_query("SELECT * from books")
	return render_template('checkbooks.html',bdata=bdata)


#--------------------------------------------------------------------------------------------

# Login code ended

#---------------------------------------------------------------------------------------------


if __name__ == "__main__":
	app.run(debug = True)