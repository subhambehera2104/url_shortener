from flask import Flask,render_template,request,redirect,url_for
import hashlib
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #disable tracking modifications not needed in the tutorial
db= SQLAlchemy(app)

class Url(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    original_url=db.Column(db.String(1023))
    short_url=db.Column(db.String(1023))
    created= db.Column(db.DateTime)

@app.route('/')
def index():
    urls = Url.query.order_by(Url.created.desc()).limit(10).all()
    return render_template('index.html', urls=urls)

@app.errorhandler(404)
def page_not_found(error):
     return render_template('404.html'), 404
     
def generate_short_url(original_url):
    hash_object = hashlib.md5(original_url.encode())
    hash_hex = hash_object.hexdigest()
    short_url = hash_hex[:7]
    return short_url

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['url']
    short_url = generate_short_url(original_url)

    url = Url(original_url=original_url, short_url=short_url)
    db.session.add(url)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/short_url/<short_url>')
def redirect_url(short_url):
    result=Url.query.filter_by(short_url=short_url).first() 
    if result:
        return redirect(result.original_url)
    else:
        abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

@app.route('/delete/<id>')
def delete(id):
    url= Url.query.get(id) 
    db.session.delete(url) # delete from todo where id=todo_id
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003, debug=True)
  