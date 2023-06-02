import os
from flask import Flask
from flask import request
from flask import redirect 
from flask import render_template
from models import db
from models import Fcuser
from flask import session
from flask_wtf.csrf import CSRFProtect
from forms import RegisterForm, LoginForm

app = Flask(__name__)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            fcuser = Fcuser()
            fcuser.userid = form.data.get('userid')
            fcuser.username = form.data.get('username')
            fcuser.password = form.data.get('password')
            fcuser.amount = 0  # 초기 금액을 0으로 설정
            fcuser.coin = 0  # 초기 코인 수를 0으로 설정

            db.session.add(fcuser)
            db.session.commit()

            return redirect('/')  # 회원가입 완료 후 '/'로 리다이렉션

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # 로그인 폼 생성
    if form.validate_on_submit():
        session['userid'] = form.data.get('userid')

        # 사용자 정보 가져오기
        fcuser = Fcuser.query.filter_by(userid=session['userid']).first()
        if fcuser is not None:
            username = fcuser.username
            amount = fcuser.amount
            coin = fcuser.coin
            session['username'] = username
            session['amount'] = amount
            session['coin'] = coin

        return redirect('/')  # 로그인에 성공하면 홈화면으로 redirect

    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect('/')


@app.route('/')
def hello():
    userid = session.get('userid', None)
    return render_template('main.html', userid=userid)


if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__))  # db파일을 절대경로로 생성
    dbfile = os.path.join(basedir, 'db.sqlite')  # db파일을 절대경로로 생성

    print("basedir:", basedir)
    print("dbfile:", dbfile)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile # sqlite를 사용함
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True 
    # 사용자 요청의 끝마다 커밋(데이터베이스에 저장,수정,삭제등의 동작을 쌓아놨던 것들의 실행명령)을 한다.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 수정사항에 대한 track을 하지 않는다. True로 한다면 warning 메시지유발
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'

    csrf = CSRFProtect()
    csrf.init_app(app)

    db.init_app(app)
    with app.app_context():
      db.create_all()  # db 생성

    app.run(host='127.0.0.1', port=5000, debug=True)
    # 포트번호는 기본 5000, 개발단계에서는 debug는 True
