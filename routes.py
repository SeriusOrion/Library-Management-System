from flask import Flask, render_template, request, redirect,url_for, flash
from werkzeug.security import generate_password_hash
from datetime import datetime
from models import db, User, Book, Section, Mybooks, AccessRequests,Feedback
from flask import Blueprint

app = Blueprint('routes', __name__)

@app.route('/')
def welcome():
    quote = "Welcome to our library management system!"
    return render_template('welcome.html', quote=quote)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':   
        name=request.form.get('name')
        username=request.form.get('username')
        password=request.form.get('password')
        if username=='' or password=='' or name=='':
            flash('Above field(s) cannot be empty.')
            return redirect(url_for('routes.register'))
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('routes.register'))
        user=User(username=username,passhash=generate_password_hash(password),name=name)
        db.session.add(user)
        db.session.commit()
        flash('Username successfully registered.')
        return redirect(url_for('routes.login'))
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username=='' or password=='':
            flash('Above field(s) cannot be empty.')
        user=User.query.filter_by(username=username).first()
        if not user:
            flash('User does not exist, Kindly register.')
            return redirect(url_for('routes.register'))
        if not user.check_password(password):
            flash('Incorrect password.')
            return redirect(url_for('routes.login'))
        if user.is_admin:
            return redirect(url_for('routes.admin'))
        else:
            return redirect(url_for('routes.udash',id=user.id))
    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin/sections')
def manage_sections():
    sections=Section.query.all()
    return render_template('asections.html',sections=sections)

@app.route('/admin/sections/add', methods=['GET','POST'])
def add_section():
    if request.method == 'POST':
        name=request.form.get('name')
        if not name:
            flash('Section cannot be empty.')
        if len(name)>64:
            flash('Section name cannot be greater than 64 characters.')
        else:
            sections=Section(name=name)
            db.session.add(sections)
            db.session.commit()
            flash('Section added successfully!')
            return redirect(url_for('routes.manage_sections'))
    return render_template('section/add.html')

@app.route('/admin/sections/view/<int:id>')
def view(id):
    section=Section.query.get(id)
    return render_template('section/view.html',section=section)

@app.route('/admin/sections/edit/<int:id>',methods=['GET','POST'])
def edit_section(id):
    sections=Section.query.get(id)
    if request.method == 'POST':
        name=request.form.get('name')
        if not name:
            flash('Section cannot be empty.')
        if len(name)>64:
            flash('Section name cannot be greater than 64 characters.')
        else:
            sections.name=name
            db.session.commit()
            flash('Section updated successfully!')
            return redirect(url_for('routes.manage_sections'))
    return render_template('section/edit.html',sections=sections)

@app.route('/admin/sections/delete/<int:id>',methods=['GET','POST'])
def delete_section(id):
    sections=Section.query.get(id)
    if request.method == 'POST':
        if sections:
            for book in sections.ebooks:
                db.session.delete(book)
            db.session.delete(sections)
            db.session.commit()
            flash('Section deleted successfully!')
            return redirect(url_for('routes.manage_sections'))
        else:
            flash('Section not found.')
            return redirect('routes.manage_sections')
    return render_template('section/delete.html',sections=sections)

@app.route('/admin/books')
def manage_books():
    books=Book.query.all()
    sections=Section.query.all()
    return render_template('abooks.html',books=books,sections=sections)

@app.route('/admin/books/add',methods=['GET','POST'])
def add_books():
    if request.method == 'POST':
        title=request.form.get('title')
        author=request.form.get('author')
        section_id=request.form.get('section')
        description=request.form.get('description')
        copies=request.form.get('copies')
        blink=request.form.get('blink')
        if not title or not author or not copies or blink:
            flash('Book cannot be empty.')
        if len(title)>64:
            flash('Book name cannot be greater than 64 characters.')
        book = Book(title=title, author=author, section_id=section_id, description=description, copies=copies,blink=blink)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!')
        return redirect(url_for('routes.manage_books'))
    sections = Section.query.all()
    return render_template('book/add.html',sections=sections)

@app.route('/admin/books/edit/<id>',methods=['GET','POST'])
def edit_books(id):
    sections=Section.query.filter(id==id).all()
    books=Book.query.get(id)
    if request.method == 'POST':
        title=request.form.get('title')
        author=request.form.get('author')
        description=request.form.get('description')
        copies=request.form.get('copies')
        section_id = request.form.get('section')
        if not all([title,author,copies]):
            flash('Field(s) cannot be empty.')
        if len(title)>64 or len(author)>64:
            flash('Characters out of range.')
        else:
            copies=int(copies)
            section_id=int(section_id)
            books.title=title
            books.author=author
            books.description=description
            books.copies=copies
            books.section_id=section_id
            db.session.commit()
            flash('Book updated successfully!')
            return redirect(url_for('routes.manage_books'))
    return render_template('book/edit.html',books=books,sections=sections)

@app.route('/admin/books/delete/<int:id>',methods=['GET','POST'])
def delete_books(id):
    mybooks=Mybooks.query.filter_by(book_id=id).all()
    books=Book.query.get(id)
    if request.method == 'POST':
        if books:
            for mybook in mybooks:
                db.session.delete(mybook)
                db.session.commit()
            db.session.delete(books)
            db.session.commit()
            flash('Book deleted successfully!')
            return redirect(url_for('routes.manage_books'))
        else:
            flash('Books not found.')
            return redirect(url_for('routes.manage_books'))

    sections=Section.query.get(id)
    return render_template('book/delete.html',books=books,sections=sections)
                           
@app.route('/admin/manage_requests',methods=['GET','POST'])
def manage_requests():
    pending_requests = AccessRequests.query.filter_by(status='Pending').all()
    accepted_requests = AccessRequests.query.filter_by(status='Accepted').all()
    returned_requests = AccessRequests.query.filter_by(status='Returned').all()
    return render_template('manage_requests.html', requests=pending_requests, accepted_requests=accepted_requests,returned_requests=returned_requests)


@app.route('/admin/manage_requests/action/<int:request_id>/<action>')
def handle_request_action(request_id, action):
    access_request = AccessRequests.query.get(request_id)
    if access_request:
        user = User.query.filter_by(username=access_request.username).first()
        if action == 'grant':
            book=Book.query.get(access_request.book_id)
            print(book.id,book.title)
            book.copies-=1
            mybook = Mybooks(user_id=user.id,book_id=book.id,is_granted=True)
            db.session.add(mybook)
            access_request.status = 'Accepted'
            db.session.commit()
            flash('Access request is granted.')
        elif action =='reject':
            access_request.status = 'Rejected'
            db.session.commit()
            flash('Access request is rejected.')
        elif action =='revoke':
            book = Book.query.filter_by(title=access_request.ebook).first()
            user = User.query.filter_by(username=access_request.username).first()
            mybook = Mybooks.query.filter_by(user_id=user.id, book_id=book.id).first()
            if mybook.return_date<datetime.now():
                access_request.status = 'Revoked due to overdue'
                book.copies+=1
                revoked_book = Mybooks.query.filter_by(user_id=user.id, book_id=book.id).first()
                db.session.delete(revoked_book)
                db.session.commit()
                flash('Access request is automatically revoked.')
            else:
                access_request.status = 'Revoked'
                book.copies += 1
                revoked_book = Mybooks.query.filter_by(user_id=user.id, book_id=book.id).first()
                db.session.delete(revoked_book)
                db.session.commit()
                flash('Access request is manually revoked.')

    return redirect(url_for('routes.manage_requests'))

@app.route('/udash/<int:id>', methods=['GET', 'POST'])
def udash(id):
    user = User.query.get(id)
    my_books = Mybooks.query.filter_by(user_id=id).all()
    feedback = Feedback.query.filter(Feedback.user_id == id).all()
    if user and not user.is_admin:
        sections = Section.query.all()
        parameter = request.args.get('search', type=int)
        query = request.args.get('query', type=str)
        books = Book.query.all()  
        if parameter:
            books = [book for book in books if book.section_id == parameter]
        if query:
            l_query = query.lower()
            books = [book for book in books if l_query in book.title.lower() or l_query in book.author.lower()]
        return render_template('udash.html',id=user.id, my_books=my_books,feedback=feedback,user=user, books=books, sections=sections, parameter=parameter)
    else:
        flash("Kindly login.")
        return redirect(url_for('routes.login'))
    
@app.route('/request_access/<id>', methods=['POST'])
def request_access(id): 
    this_user=User.query.get(id)
    username = request.form.get('username')
    book_id = request.form.get('book_id')
    book=Book.query.get(book_id)
    num_requested_books = AccessRequests.query.filter_by(username=username).count()
    if num_requested_books > 5:
        flash('You have already requested the maximum number of books allowed.')
    access_request = AccessRequests(username=username, ebook=book.title,user_id=id,book_id=book.id)
    db.session.add(access_request)
    db.session.commit()
    return redirect(url_for('routes.udash',id=this_user.id))
    
@app.route('/mybooks',methods=['GET','POST'])
def mybooks():
    username=request.args.get('username')
    user=User.query.filter_by(username=username).first()
    book=Book.query.first()
    granted_books = Mybooks.query.filter_by(user_id=user.id).all()
    return render_template('mybooks.html',user=user,book=book, granted_books=granted_books)

@app.route('/return_book/<int:request_id>/<action>')
def return_book(request_id, action):
    my_book=Mybooks.query.get(request_id)
    ui=my_book.user_id
    bi=my_book.book_id
    this_user=User.query.get(ui)
    access_request = AccessRequests.query.filter_by(user_id=ui,book_id=bi,status='Accepted').first()
    print(access_request.id,access_request.username,access_request.book_id,action)
    if access_request:
        if action == 'returned':
            user = User.query.get(ui)
            book=Book.query.get(bi)
            if book:
                book.copies += 1
                returned_book = Mybooks.query.filter_by(user_id=ui, book_id=bi).first()
                if returned_book:
                    db.session.delete(returned_book)
                    db.session.commit()
                    access_request.status = 'Returned'
                    db.session.commit()
                    flash('The book is returned successfully.')
                else:
                    flash('The book was not found in the user\'s library.')
            else:
                flash('The requested book was not found.')
    return redirect(url_for('routes.udash',id=this_user.id))
 
@app.route('/give_feedback/<int:book_id>/<int:user_id>', methods=['GET', 'POST'])
def give_feedback(book_id,user_id):
    book_id=book_id
    user_id=user_id
    if request.method == 'POST':
        ui = request.form.get('user_id')
        bi = request.form.get('book_id')        
        feedback_text = request.form.get('feedback')
        feedback = Feedback(user_id=ui, book_id=bi, content=feedback_text)
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback submitted successfully')
        return redirect(url_for('routes.udash',id=ui))
    return render_template('feedback.html',book_id=book_id,user_id=user_id)

@app.route('/profile/<int:user_id>',methods=['GET','POST'])
def profile(user_id):
    user=User.query.get(user_id)
    if request.method=="POST":
        user.username=request.form.get('username')
        user.name=request.form.get('name')
        user.cpassword=request.form.get('cpassword')
        user.passhash=generate_password_hash(request.form.get('password'))
        db.session.add(user)
        db.session.commit()
        flash('Profile updated successfully')
    return render_template('profile.html',user=user)

@app.route('/logout')
def logout():
    flash('User successfully logged out.')
    return render_template('login.html')
