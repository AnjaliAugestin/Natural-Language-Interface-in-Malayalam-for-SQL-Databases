from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_bcrypt import Bcrypt
import nltk
import csv
from csv import DictReader
from mlmorph import Analyser
from googletrans import Translator
import mysql.connector as sql_db


app = Flask(__name__)
bcrypt = Bcrypt(app)


# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'mbase'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ummu@123'
app.config['MYSQL_DB'] = 'authorize'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/', methods = ['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'user_id' in request.form and 'password' in request.form:
        # Create variables for easy access
        user_id = request.form['user_id']
        password1 = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor = cnx.cursor(dictionary=True,buffered=True)
        cursor.execute("SELECT * FROM registered WHERE user_id =%s", (user_id,))
        account = cursor.fetchone()
        if account:
            # account = cursor.fetchone()
            password2 = account['password']
            if bcrypt.check_password_hash(password2.encode('utf-8'),password1):
        
        # cursor.execute('SELECT * FROM registered WHERE user_id = %s AND password = %s', (user_id, hashPassword,))
        # # Fetch one record and return result
        # account = cursor.fetchone()
        # print(account)
        # # If account exists in accounts table in out database
        # if account :
        #     # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['user_id'] = account['user_id']
                session['name'] = account['name']
                # Redirect to home page
                cursor.close()
                return render_template('interface.html', name = session['name'])
            else :
                msg = "Incorrect password!"
                return render_template('login_register.html', msg = msg)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username!'
            return render_template('login_register.html', msg = msg)

    # Show the login form with message (if any)
    return render_template('login_register.html')


# http://localhost:5000/python/logout - this will be the logout page
@app.route('/login/logout/')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('user_id', None)
   session.pop('name', None)
   # Redirect to login page
   return redirect(url_for('home'))


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'user_id' in request.form and 'password' in request.form and 'email' in request.form and 'name' in request.form and 'type' in request.form:
        user_id = request.form['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE user_id = %s ', [user_id])
        # Fetch one record and return result
        account1 = cursor.fetchone()
        # Create variables for easy access
        if account1:
            user_id = request.form['user_id']
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            hashPassword = bcrypt.generate_password_hash(password).decode('utf-8')
            type = request.form['type']

            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM registered WHERE user_id = %s', [user_id,])
            account2 = cursor.fetchone()
            # If account exists show error and validation checks
            if account2:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', user_id):
                msg = 'Username must contain only characters and numbers!'
            elif not user_id or not password or not email:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                cursor.execute('INSERT INTO registered VALUES (%s, %s, %s, %s, %s)', [user_id, name, email, hashPassword, type,])
                mysql.connection.commit()
                # session['userid'] = account2['user_id']
                # session['name'] = account2['name']
                # session['email'] = account2['email']
                # session['password'] = account2['password']

                return render_template('successful_reg.html')
            return render_template('login_register.html')
        else:
            msg = 'no user ID found'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('login_register.html', msg = msg)

@app.route("/login/interface")
def interface():
    return render_template('interface.html', name = session['name'])


@app.route("/login/interface/generate", methods=['POST', 'GET'])
def generate():
    malayalam_query = request.form['malayalam_query']
    # *** TOKENIZATION ***

    # Tokenize the query using the Malayalam language tokenizer
    tokens = nltk.word_tokenize(malayalam_query, language='malayalam')
    tokens_copy = tokens.copy()

    # print(tokens)
    # print(tokens_copy)


    # *** LEMMATIZATION ***

    # Open the CSV file and read the data into a list
    with open('lemmatization_dataset.csv', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        csv_data = list(csv_reader)

    # Define which columns to use as keys and values
    key_column = 0
    value_column = 1

    # Create an empty dictionary to store the key-value pairs
    key_value_dict = {}

    # Iterate through each row of the CSV data
    for row in csv_data:
        # Extract the key and value from the selected columns
        # print(row[key_column])
        key = row[key_column]
        value = row[value_column]
    
        # Add the key-value pair to the dictionary
        key_value_dict[key] = value  

    lemmas = []

    for token in tokens:
        #print(key_value_dict[token])
        try:
            # print(key_value_dict[token])
            lemmas.append(key_value_dict[token])
        except KeyError:
            # print(token)
            lemmas.append(token)
        except:
            print("Something else went wrong")

    print(lemmas)

    # *** lexicon lookup ***

    def student_table_lookup(lemmas):
        with open('student_lexicon.csv', encoding='utf-8') as csvfile:
            reader = DictReader(csvfile)
            element = []
            for row in reader:
                # print(row)
                for lemma in lemmas: 
                    # print(lemma )

                    # check the arguments against the row
                    if (row['malayalam_words'] == lemma):
                        # print(dict(row))
                        element.append(dict(row))
                        # lemmas.remove(lemma)
        return element

    def faculty_table_lookup(lemmas):
        with open('faculty_lexicon.csv', encoding='utf-8') as csvfile:
            reader = DictReader(csvfile)
            element = []
            for row in reader:
                # print(row)
                for lemma in lemmas: 
                    # print(lemma )

                    # check the arguments against the row
                    if (row['malayalam_words'] == lemma):
                        # print(dict(row))
                        element.append(dict(row))
                        # lemmas.remove(lemma)
        return element

    def course_table_lookup(lemmas):
        with open('course_lexicon.csv', encoding='utf-8') as csvfile:
            reader = DictReader(csvfile)
            element = []
            for row in reader:
                # print(row)
                for lemma in lemmas: 
                    # print(lemma )

                    # check the arguments against the row
                    if (row['malayalam_words'] == lemma):
                        # print(dict(row))
                        element.append(dict(row))
                        # lemmas.remove(lemma)
        return element

    def table_lookup(lemmas):
        with open('table_lexicon.csv', encoding='utf-8') as csvfile:
            reader = DictReader(csvfile)
            element = []
            for row in reader:
                # print(row)
                for lemma in lemmas: 
                    # print(lemma )

                    # check the arguments against the row
                    if (row['malayalam_words'] == lemma):
                        # print(dict(row))
                        element.append(dict(row))
                        # lemmas.remove(lemma)
        return element

    def operation_condition_lookup(lemmas):
        with open('operation_condition_lexicon.csv', encoding='utf-8') as csvfile:
            reader = DictReader(csvfile)
            element = []
            for row in reader:
                # print(row)
                for lemma in lemmas: 
                    # print(lemma ) 

                    # check the arguments against the row
                    if (row['malayalam_words'] == lemma):
                        # print(dict(row))
                        element.append(dict(row))
                        # lemmas.remove(lemma)
        return element
    attributes = [] 
    conditions = []
    operation = ""
    # operation and condition identification
    condtions_operations = operation_condition_lookup(lemmas)

    for item in condtions_operations:
        if item['semantic_meaning'] == 'condition' or item['semantic_meaning'] == 'all_attributes':
            conditions.append(item['english_words'])

        elif item['semantic_meaning'] == 'operation':
            operation = item['english_words']
            print(f"operation = {operation}")

    print(f"condition = {conditions}")


    # print(table_operation_lookup(lemmas))
    # table and attributes identification

    # for lemma in lemmas:

    #     # print()

    #     if lemma == "പഠിക്കുക":
    #         # student table lexicon lookup
    #         print(student_table_lookup(lemmas))
    #         break 

    #     if lemma == "പഠിപ്പിക്കുക":
    #         # faculty table lexicon lookup      
    #         print(faculty_table_lookup(lemmas))
    #         break 

        
    #     # table operation lookup
    # print(table_lookup(lemmas))

    flag = 0

    for lemma in lemmas:

        if lemma == "പഠിക്കുക":
            flag = 1
            break

        if lemma == "പഠിപ്പിക്കുക":
            flag = 2
            break 

    if flag == 1:
        table = "student"
        student_attributes = student_table_lookup(lemmas)
        attributes = []
        for item in student_attributes:
            attributes.append(item['english_words'])
        print(f"table= {table} \nattributes= {attributes}")

    elif flag == 2:
        table = "faculty"
        faculty_attributes = faculty_table_lookup(lemmas)
        attributes = []
        for item in faculty_attributes:
            attributes.append(item['english_words'])
        print(f"table= {table} \nattributes= {attributes}")
        

    elif flag == 0:  
        #print(table_lookup(lemmas))
        table = table_lookup(lemmas)
        # print(table)
        for item in table:
            if(item['english_words'] == 'student'):
                table = "student"
                student_attributes = student_table_lookup(lemmas)
                attributes = []
                for attribute in student_attributes:
                    attributes.append(attribute['english_words'])
                print(f"table= {item['english_words']} \nattributes= {attributes}")
            if(item['english_words'] == 'faculty'):
                table = "faculty"
                faculty_attributes = faculty_table_lookup(lemmas)
                attributes = []
                for attribute in faculty_attributes:
                    attributes.append(attribute['english_words'])
                print(f"table= {item['english_words']} \nattributes= {attributes}")
            if(item['english_words'] == 'course'):
                table = 'course'
                course_attributes = course_table_lookup(lemmas)
                attributes = []
                for attribute in course_attributes:
                    attributes.append(attribute['english_words'])
                print(f"table= {item['english_words']} \nattributes= {attributes}")
            


    # *** PoS Tagging ***

    analyser = Analyser()

    translator = Translator()


    # Tokenize the query using the Malayalam language tokenizer

    genitive = []
    locative = []
    foreign_words = []
    numbers = []
    locations = ['kasargod', 'kannur', 'malappuram','kozhikode','palakkad','thrissur','idukki','pathanamthitta','ernakulam','kottayam','kollam','alappuzha','thiruvananthapuram','wayanad']

    # for token in tokens_copy:
    #     pos_tag = analyser.analyse(token)
    #     for i in pos_tag:
    #         # print(i[0])
    #         if i[0].__contains__('<np><genitive>'):
    #             genitive.append(i[0]. split('<')[0])
    #             break

    #         if i[0].__contains__('<np><locative>'):
    #             locative.append(i[0]. split('<')[0])
    #             break

    #         if i[0].__contains__('<fw>'):
                
    #             foreign_words.append(i[0]. split('<')[0])
    #             break

    #         if i[0].__contains__('<num>'):
    #             numbers.append(i[0]. split('<')[0])
    #             break

    #*****function to remove attributes******
    
    def remove_attribute(table_name,attributes):
        if table_name == 'student':
            id = 'std_id'
            attributes.remove("std_id")
        elif table_name == 'faculty':
            id = 'faculty_id'
            attributes.remove('faculty_id')
        elif table_name == 'course':
            id = 'course_id'
            attributes.remove('course_id')
        else:
            id = 'dept_id'
            attributes.remove('dept_id')
        return id



    nongene = ['കുട്ടി','അദ്ധ്യാപിക','അദ്ധ്യാപകൻ','ആയ','ശമ്പളം','വേതനം','തുക','രൂപ','ഇൽ','ഇ']
    departments = ['it','cs','ec','me','eee']
    pos_tagger = []
    less = ['താഴെ', 'കുറവ്']
    greater = ['മുകളിൽ','കൂടുതൽ','മേലെ','മേൽ','മുകൾ']
    salaries = ['ശമ്പളം','വേതനം', 'തുക', 'രൂപ', 'പൈസ', 'ശംബളം']

    for token in tokens_copy:
        pos = analyser.analyse(token)
        pos_tagger.append(pos)

    # print(pos_tagger)
    # print(pos_tagger[3][0])

    # print(len(tokens_copy))
    for j in range(0, len(tokens_copy)): 
        # print(j)
        pos_tag = analyser.analyse(tokens_copy[j])
        print(pos_tag)
        try:
            print(f"word = {pos_tagger[j+2][0][0]}")
        except:
            pass
    
        #for i in pos_tag:
            #print(i)
            # print(i[1 ])
            # word = i[0]
        # print(pos_tag[0][0][-1:-4:-1])
        # print(pos_tag[0][0][-1:-5:-1])
        # print(len(pos_tag))
        try:
            print(pos_tag[0])
        except:
            print("no tagging ")
            continue 
        c = 0

        #*********genitive identification ********



        try:
            print(pos_tag[0][0][-1:-4:-1])
            print(pos_tag[0][0][-1:-5:-1])
            print(len(pos_tag))

            print(pos_tag[1])
            print(pos_tag[1][0])
            if pos_tag[1].__contains__('<np><genitive>'):
                c = c +1
            print(c)

        except:
            print("nothing")

        #try :
        if len(pos_tag)==1:
            if pos_tag[0][0][-1:-4:-1] == (">n<") or pos_tag[0][0][-1:-5:-1] == (">pn<"):
                if pos_tag[0][0].split('<')[0] not in nongene:
                # genitive.append(i[0]. split('<')[0])
                # name = translator.translate(i[0]. split('<')[0], dest='en').text 
                    if pos_tag[0][0].__contains__('ഓ<cnj>') or pos_tagger[j+2][0][0].__contains__('ഓ<cnj>') or pos_tagger[j+1][0][0].__contains__('ഓ<cnj>'):
                        genitive.append(f"{pos_tag[0][0].split('<')[0]},")
                        if 'mname' in attributes:
                            attributes.remove('mname')

                    else :
                        genitive.append(pos_tag[0][0].split('<')[0])
                        if 'mname' in attributes:
                            attributes.remove('mname')
                
        try:
            if pos_tag[1][0].__contains__('<np><genitive>') :
                if pos_tag[1][0].split('<')[0] not in nongene:
                    if pos_tag[0][0].__contains__('ഓ<cnj>') or pos_tagger[j+2][0][0].__contains__('ഓ<cnj>') or pos_tagger[j+1][0][0].__contains__('ഓ<cnj>'):
                        genitive.append(f"{pos_tag[0][0].split('<')[0]},")
                        if 'mname' in attributes:
                            attributes.remove('mname')

                    else :
                        genitive.append(pos_tag[0][0].split('<')[0])
                        if 'mname' in attributes:
                            attributes.remove('mname')

        except:
            print("no 1st element")

        # except:
        #     if pos_tag[0][0][-1:-4:-1] == (">n<") or pos_tag[0][0][-1:-5:-1] == (">pn<") and len(pos_tag)==1:
        #         if pos_tag[0][0].split('<')[0] not in nongene:
        #             genitive.append(pos_tag[0][0].split('<')[0])
        #        # break

        if (pos_tag[0][0].__contains__('<np><genitive>') and len(pos_tag) == 1):
            if pos_tag[0][0].__contains__('ഓ<cnj>') or pos_tagger[j+2][0][0].__contains__('ഓ<cnj>'):
                genitive.append(f"pos_tag[0][0].split('<')[0]")
                if 'mname' in attributes:
                    attributes.remove('mname')
            else:
                genitive.append(pos_tag[0][0].split('<')[0])
                if 'mname' in attributes:
                    attributes.remove('mname')


    # *******Locative Identification********
        def checking_or_location():

            try:
                if pos_tagger[j+1][0][0].__contains__('ഓ<cnj>'):
                    return True
            except:           
                pass   
            try:
                if pos_tagger[j+1][3][0].__contains__('ഓ<cnj>'):
                    return True

            except:
                pass

            try:
                if pos_tagger[j+2][0][0].__contains__('ഓ<cnj>'):
                    return True

            except:
                pass

            try:
                if pos_tagger[j+3][3][0].__contains__('ഓ<cnj>'):
                    return True

            except:
                pass

            try:
                if pos_tag[0][0].__contains__('ഓ<cnj>'):
                    return True

            except:
                pass
        

        if (pos_tag[0][0].__contains__('<np><locative>') or pos_tag[0][0].__contains__('<np>ഉം<cnj>') or pos_tag[0][0].__contains__('<n><locative>') or pos_tag[0][0].__contains__('<np>') or pos_tag[0][0].__contains__('<n>') ) :
            try:
                location = translator.translate(pos_tag[0][0]. split('<')[0], dest='en').text.lower()
                if location in locations:
                    if checking_or_location() is True :
                        locative.append(f'{location},')
                        if 'location' in attributes:
                            attributes.remove('location')
                    else : 
                        locative.append(location)
                        if 'location' in attributes:
                            attributes.remove('location')

            except:
                msg="your internet connection is not stable"
                return render_template('interface.html', msg=msg)

                # sys.exit(1) 

            
            #break

        #*******Foreign word Identification********

        def checking_or_fw():
            try:
                if pos_tagger[j+1][0][0].__contains__('ഓ<cnj>'):
                    print ("ഒന്ന് ")
                    return True
            except:
                pass

            try:
                if pos_tagger[j+2][0][0].__contains__('ഓ<cnj>'):
                    print ("രണ്ട് ")
                    return True
            except:
                pass

            try:
                if tokens_copy[j+1].__contains__('ലോ'):
                    print ("മൂന്")
                    return True
            except:
                pass

            try:
                if tokens_copy[j+1].__contains__('യോ'):
                    print ("നാല് ")
                    return True
            except:
                pass

        if pos_tag[0][0].__contains__('<fw>'):

            try:
                if tokens_copy[j -1]=="അദ്ധ്യയനവർഷം" or tokens_copy[j-1]=="വർഷം" or tokens_copy[j+1]=="വർഷത്തിൽ" or tokens_copy[j+1]=="അദ്ധ്യയനവർഷത്തിൽ" or  tokens_copy[j+1]=="അദ്ധ്യയനവർഷത്തിലോ" or tokens_copy[j+1]=="വർഷത്തിലോ"  :
                    print('ഇഫ് worked ')
                    if checking_or_fw() is True:
                        foreign_words.append(f"acyear = '{pos_tag[0][0]. split('<')[0]},' ")
                        attributes.remove('acyear')
                    else:
                        foreign_words.append(f"acyear = '{pos_tag[0][0]. split('<')[0]}' ")
                        attributes.remove('acyear')
    
                
                elif pos_tag[0][0].split('<')[0].lower() in departments:
                    print ("elif workedddddd ")
                    if checking_or_fw() is True:
                        foreign_words.append(f"dept_name = '{pos_tag[0][0].split('<')[0]},' ")
                        attributes.remove('dept_name')
                    else:
                        foreign_words.append(f"dept_name = '{pos_tag[0][0].split('<')[0]}' ")
                        attributes.remove('dept_name')
                # print(pos_tag[0][0].split('<')[0].lower())

                else:
                    if pos_tag[0][0].split('<')[0] != 'ഡിപാർട്ട്മെൻറ്' and pos_tag[0][0].split('<')[0] != 'ക്രെഡിറ്റ്' and pos_tag[0][0].split('<')[0] != 'ഐഡി' and pos_tag[0][0].split('<')[0]. lower() != 'id' and table == 'course':
                        if checking_or_fw() is True:
                            foreign_words.append(f"course_name = '{pos_tag[0][0].split('<')[0]},' ")
                            attributes.remove('course_name')
                        else:
                            foreign_words.append(f"course_name = '{pos_tag[0][0].split('<')[0]}' ")
                            attributes.remove('course_name')
            except:
                #oreign_words.append(pos_tag[0][0]. split('<')[0])
                print('exceptionnnnnnnnnnnnnnnnnnnn')
            
            # foreign_words.append(i[0]. split('<')[0])
            #break


            
        #*******Numbers Identification********


        def checking_or_num():
            try:
                if tokens_copy[j+1].__contains__("ഓ"):
                    print ("ഒന്ന് ")
                    return True
            except:
                pass
            try:
                if tokens_copy[j+2].__contains__("ഓ"):
                    print ("രണ്ട്  ")
                    return True
            except:
                pass
            try:
                if pos_tagger[j+1][0][0].__contains__("ഓ<cnj>"):
                    print ("മൂന്ന്  ")
                    return True
            except:
                pass
            try:
                if pos_tagger[j+2][0][0].__contains__("ഓ<cnj>"):
                    print ("നാല് ")
                    return True
            except:
                pass



        if pos_tag[0][0].__contains__('<num>'):

            try:
                print(f"word2  = {pos_tagger[j+2][0][0].split('<')[0]}")
            except :
                pass
            try:
                if (tokens_copy[j+3].__contains__("ഐഡി") or tokens_copy[j+3].lower() == "id" or tokens_copy[j-1].__contains__("ഐഡി") or tokens_copy[j-1].lower()=='id') and tokens_copy[j-1] not in salaries:
                    # if tokens_copy[j-1] not in salaries:
                    if pos_tagger[j+2][0][0].split('<')[0] in less :
                        if checking_or_num() is True:
                            numbers.append(f"{remove_attribute(table, attributes)} < {pos_tag[0][0]. split('<')[0]},")
                        else:
                            numbers.append(f"{remove_attribute(table, attributes)} < {pos_tag[0][0]. split('<')[0]}")
                            remove_attribute(table,attributes)
                    elif pos_tagger[j+2][0][0].split('<')[0] in greater :
                        if checking_or_num() is True:
                            numbers.append(f"{remove_attribute(table, attributes)} > {pos_tag[0][0]. split('<')[0]},")
                            remove_attribute(table,attributes)
                        else:
                            numbers.append(f"{remove_attribute(table, attributes)} > {pos_tag[0][0]. split('<')[0]}")
                            remove_attribute(table,attributes)
                    else:
                        if checking_or_num() is True:
                            numbers.append(f"{remove_attribute(table, attributes)} = {pos_tag[0][0]. split('<')[0]},")
                            remove_attribute(table,attributes)
                        else:
                            numbers.append(f"{remove_attribute(table, attributes)} = {pos_tag[0][0]. split('<')[0]}")
                            remove_attribute(table,attributes)

                elif (tokens_copy[j-1] == "ക്രെഡിറ്റ്" or tokens_copy[j+3] == "ക്രെഡിറ്റ്") and table=='course':
                    if pos_tagger[j+2][0][0].split('<')[0] in less :
                        if checking_or_num() is True:
                            numbers.append(f"credit < {pos_tag[0][0]. split('<')[0]},")
                            attributes.remove('credit')
                        else:
                            numbers.append(f"credit < {pos_tag[0][0]. split('<')[0]}")
                            attributes.remove('credit')
                    elif pos_tagger[j+2][0][0].split('<')[0] in greater :
                        if checking_or_num() is True:
                            numbers.append(f"credit > {pos_tag[0][0]. split('<')[0]},")
                            attributes.remove('credit')
                        else:
                            numbers.append(f"credit > {pos_tag[0][0]. split('<')[0]}")
                            attributes.remove('credit')
                    else:
                        if checking_or_num() is True:
                            numbers.append(f"credit = {pos_tag[0][0]. split('<')[0]},")
                            attributes.remove('credit')
                        else:
                            numbers.append(f"credit = {pos_tag[0][0]. split('<')[0]}")
                            attributes.remove('credit')

                else:
                    if pos_tagger[j+2][0][0].split('<')[0] in less :
                        if checking_or_num() is True:
                            numbers.append(f"salary < {pos_tag[0][0]. split('<')[0]},")
                            attributes.remove('salary')
                        else:
                            numbers.append(f"salary < {pos_tag[0][0]. split('<')[0]}")
                            attributes.remove('salary')
                    elif pos_tagger[j+2][0][0].split('<')[0] in greater :
                        if checking_or_num() is True:
                            numbers.append(f"salary > {pos_tag[0][0]. split('<')[0]},")
                            attributes.remove('salary')
                        else:
                            numbers.append(f"salary > {pos_tag[0][0]. split('<')[0]}")
                            attributes.remove('salary')
                    else:
                        if checking_or_num() is True:
                            numbers.append(f"salary = {pos_tag[0][0]. split('<')[0]},")
                            attributes.remove('salary')
                        else:
                            numbers.append(f"salary = {pos_tag[0][0]. split('<')[0]}")
                            attributes.remove('salary')


            except:
                pass 
            # if 'greater' in conditions:
            #     try:
            #         if tokens_copy[j+3] == "ഐഡി" or tokens_copy[j+3].lower() == "id" or tokens_copy[j-1]=='ഐഡി' or tokens_copy[j-1].lower()=='id':
            #             numbers.append(f"id > {pos_tag[0][0]. split('<')[0]} ")
            #             remove_attribute(table,attributes)
            #         elif tokens_copy[j-1] == "ക്രെഡിറ്റ്" or tokens_copy[j+3] == "ക്രെഡിറ്റ്":
            #             numbers.append(f"credit > {pos_tag[0][0]. split('<')[0]} ")
            #             attributes.remove('credit')
            #         else:
            #             numbers.append(f"salary > {pos_tag[0][0]. split('<')[0]} ")
            #             attributes.remove('salary')
            #     except:
            #         #numbers.append(pos_tag[0][0]. split('<')[0])
            #         pass 


            # elif 'less' in conditions:
            #     try:
            #         if tokens_copy[j+3] == "ഐഡി" or tokens_copy[j+3].lower() == "id" or tokens_copy[j-1]=='ഐഡി' or tokens_copy[j-1].lower()=='id':
            #             numbers.append(f"id < {pos_tag[0][0]. split('<')[0]} ")
            #             remove_attribute(table,attributes)
            #         elif tokens_copy[j-1] == "ക്രെഡിറ്റ്" or tokens_copy[j+3] == "ക്രെഡിറ്റ്":
            #             numbers.append(f"credit < {pos_tag[0][0]. split('<')[0]} ")
            #             attributes.remove('credit')
            #         else:
            #             numbers.append(f"salary < {pos_tag[0][0]. split('<')[0]} ")
            #             attributes.remove('salary')
            #     except:
            #         #numbers.append(pos_tag[0][0]. split('<')[0])
            #         pass 


            # else:
            #     try:
            #         if tokens_copy[j -1]=="ഐഡി" or tokens_copy[j-1]. lower()=="id" or tokens_copy[j+1]=="ഐഡി" or tokens_copy[j+1].lower()=="id":
            #             numbers.append(f"id = {pos_tag[0][0]. split('<')[0]} ")
            #             remove_attribute(table,attributes)
            #         elif tokens_copy[j-1] == "ക്രെഡിറ്റ്" or tokens_copy[j+3] == "ക്രെഡിറ്റ്":
            #             numbers.append(f"credit = {pos_tag[0][0]. split('<')[0]} ")
            #             attributes.remove('credit')
            #         else :
            #             numbers.append(f"salary = {pos_tag[0][0].split('<')[0]} ")
            #             attributes.remove('salary')
            #     except:
            #         #numbers.append(pos_tag[0][0]. split('<')[0])
            #         pass 

            # # numbers.append(i[0]. split('<')[0])
            # # break

    print(f"genitive = {genitive}")
    print(f"locative = {locative}")
    print(f"foreign_words = {foreign_words}")
    print(f"numbers = {numbers}")


    def identify_condition_and(gen,loc,fw,num):
        conditional_expression = []
        if len(gen) != 0:
            conditional_expression = [f"mname = '{x}' " for x in gen if not x.__contains__(',')]
        if len(loc) != 0:
            conditional_expression += [f"location = '{x}' " for x in loc if not x.__contains__(',')]
        if len(fw) != 0:
            conditional_expression += [x for x in fw if not x.__contains__(',')]
        if len(num) != 0:
            conditional_expression += [x for x in num if not x.__contains__(',')]
        return conditional_expression

    print(identify_condition_and(genitive,locative,foreign_words,numbers))

    def identify_condition_or(gen,loc,fw,num):
        conditional_expression = []
        if len(gen) != 0:
            conditional_expression = [f"mname = '{x.split(',')[0]}'" for x in gen if x.__contains__(',')]
        if len(loc) != 0:
            conditional_expression += [f"location = '{x.split(',')[0]}'" for x in loc if x.__contains__(',')]
        if len(fw) != 0:
            conditional_expression += [x.split(',')[0] for x in fw if x.__contains__(',')]
        if len(num) != 0:
            conditional_expression += [x.split(',')[0] for x in num if x.__contains__(',')]

        return conditional_expression

    print(identify_condition_or(genitive,locative,foreign_words,numbers))


    # b=0
    # if ('faculty_id' in attributes and 'salary' in attributes):
    #     b=1
    # else:
    #     b=0
    # print(b)
    
    def remove_items(list, item):
        # using list comprehension to perform the task
        res = [i for i in list if i != item]
        return res
    
    msg = ''

    if len(table) == 0 :
        msg = 'could not identify table !!!'
        return render_template('interface.html', msg = msg, name = session['name'])
        
    if operation == '' :
        msg = 'could not identify operation !!!'
        return render_template('interface.html', msg = msg, name = session['name'])
    
    else:
        if operation == 'select':
            if 'all' in conditions :

                conditions = remove_items(conditions, 'all')
                
                if len(conditions) == 0 and len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 0 and len(identify_condition_or(genitive,locative,foreign_words,numbers)) == 0 and len(attributes) == 0:
                    sql_query = f"{operation} * from {table} ;"

                else:
                    if len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 1 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 0 :
                        sql_query = f"{operation} * from {table} where {' and '.join([str(elem) for elem in identify_condition_and(genitive,locative,foreign_words,numbers)])} ;"

                    elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 0 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 1:
                        sql_query = f"{operation} * from {table} where {' or '.join([str(elem) for elem in identify_condition_or(genitive,locative,foreign_words,numbers)])} ;"
                    
                    elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 0 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 0 and len(attributes) != 0:
                        sql_query = f"{operation} {', '.join([str(elem) for elem in attributes])} from {table} ;"

                    elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) > 1 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 0 :
                        sql_query = f"{operation} * from {table} where {' and '.join([str(elem) for elem in identify_condition_and(genitive,locative,foreign_words,numbers)])} ;"

                    elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 0 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) > 1 :
                        sql_query = f"{operation} * from {table} where {' or '.join([str(elem) for elem in identify_condition_or(genitive,locative,foreign_words,numbers)])} ;"

                    else:
                        sql_query = f"{operation} * from {table} where {' and '.join([str(elem) for elem in identify_condition_and(genitive,locative,foreign_words,numbers)])} and {' or '.join([str(elem) for elem in identify_condition_or(genitive,locative,foreign_words,numbers)])} ;"
            
            else:
                if len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 0 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 0 and len(attributes) > 1:
                    sql_query = f"{operation} {', '.join([str(elem) for elem in attributes])} from {table} ;"

                elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 1 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 0 :
                    sql_query = f"{operation} {', '.join([str(elem) for elem in attributes])} from {table} where {' and '.join([str(elem) for elem in identify_condition_and(genitive,locative,foreign_words,numbers)])} ;"

                elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 0 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 1:
                        sql_query = f"{operation} {', '.join([str(elem) for elem in attributes])} from {table} where {' or '.join([str(elem) for elem in identify_condition_or(genitive,locative,foreign_words,numbers)])} ;"

                elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) > 1 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 0 :
                        sql_query = f"{operation} {', '.join([str(elem) for elem in attributes])} from {table} where {' and '.join([str(elem) for elem in identify_condition_and(genitive,locative,foreign_words,numbers)])} ;"

                elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 0 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) > 1 :
                        sql_query = f"{operation} {', '.join([str(elem) for elem in attributes])} from {table} where {' or '.join([str(elem) for elem in identify_condition_or(genitive,locative,foreign_words,numbers)])} ;"

                else:
                    sql_query = f"{operation} {', '.join([str(elem) for elem in attributes])} from {table} where {' and '.join([str(elem) for elem in identify_condition_and(genitive,locative,foreign_words,numbers)])} and {' or '.join([str(elem) for elem in identify_condition_or(genitive,locative,foreign_words,numbers)])} ;"

        elif operation == 'delete' :
            if len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 0 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 0 :
                sql_query = f"{operation} from {table} ; "
            
            elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 1 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 0 :
                sql_query = f"{operation} from {table} where {' and '.join([str(elem) for elem in identify_condition_and(genitive,locative,foreign_words,numbers)])} ; "
            
            elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 0 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 1 :
                sql_query = f"{operation} from {table} where {' or '.join([str(elem) for elem in identify_condition_or(genitive,locative,foreign_words,numbers)])} ; "
            
            elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) > 1 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) == 0 :
                sql_query = f"{operation} from {table} where {' and '.join([str(elem) for elem in identify_condition_and(genitive,locative,foreign_words,numbers)])}  ; "

            elif len(identify_condition_and(genitive,locative,foreign_words,numbers)) == 0 and len(identify_condition_or (genitive,locative,foreign_words,numbers)) > 1 :
                sql_query = f"{operation} from {table} where {' or '.join([str(elem) for elem in identify_condition_or(genitive,locative,foreign_words,numbers)])}  ; "

            else:
                sql_query = f"{operation} from {table} where {' and '.join([str(elem) for elem in identify_condition_and(genitive,locative,foreign_words,numbers)])} and {' or '.join([str(elem) for elem in identify_condition_or(genitive,locative,foreign_words,numbers)])} ;"


        print(sql_query)


    return render_template('interface.html', MQ = malayalam_query, SQ = sql_query, msg = msg, name = session['name'])



@app.route("/login/interface/execute", methods=['POST', 'GET'])
def execute():

    mydb = sql_db.connect(
    host="localhost",
    user="root",
    password="Ummu@123",
    database="student"
    )

    msg = ''

    sql_query = request.form['sql_query']
    print(sql_query)

    try:
        mycursor = mydb.cursor()
        mycursor.execute(sql_query)
        data = mycursor.fetchall()
        # num_fields = len(mycursor.description)
        headings = [i[0] for i in mycursor.description]
        print(headings)
        return render_template('interface.html', headings = headings, data = data, SQ = sql_query, name = session['name'])

    except:
        msg = "invalid sql query !!!"
        return render_template('interface.html', msg = msg, name = session['name'])


@app.route("/login/interface/view_profile", methods=['POST', 'GET'])
def view_profile():
    logged_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM registered WHERE user_id = %s ', (logged_id,))
    # Fetch one record and return result
    account = cursor.fetchone()
    name = account['name']
    user_id = account['user_id']
    email = account['email']
    password = account['password']
    return render_template('viewprofile.html', name = name, user_id = user_id, email = email, password = password)


@app.route("/login/interface/contact", methods=['POST', 'GET'])
def contact():
    return render_template('contact.html')


@app.route("/login/interface/documentation", methods=['POST', 'GET'])
def documentation():
    return render_template('documentation.html')


if __name__ == '__main__':
    app.run(debug=True)