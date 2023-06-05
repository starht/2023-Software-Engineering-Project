import os, random
from flask import Flask, request, redirect, render_template, session, flash
from flask_wtf.csrf import CSRFProtect
from forms import RegisterForm, LoginForm, BuyCoinForm, TradeCoinForm, IncreaseBalanceForm, DecreaseBalanceForm
from models import db, Fcuser, Market, Trade
from random import randint

app = Flask(__name__)

# market 데이터 생성
def create_initial_market_data():
    # 이미 데이터가 있는지 확인
    market_data = Market.query.all()
    if market_data:
        return

    # 초기 코인 데이터 생성
    coins = [
        {'coin_name': 'Dongguk', 'coin_quantity': 100, 'coin_price': 100}
    ]

    for coin in coins:
        market = Market(coin_name=coin['coin_name'],
                        coin_quantity=coin['coin_quantity'],
                        coin_price=coin['coin_price'])
        db.session.add(market)
    db.session.commit()


# Fcuser 모델에 coin_balance, amount_balance 프로퍼티 추가
class Fcuser(db.Model):
    # ...

    @property
    def coin_balance(self):
        return self.coin

    @property
    def amount_balance(self):
        return self.amount

# 거래 완료 시 세션 정보 업데이트
def update_session_info():
    if 'userid' in session:
        userid = session['userid']
        fcuser = Fcuser.query.filter_by(userid=userid).first()
        if fcuser:
            session['coin'] = fcuser.coin_balance
            session['amount'] = fcuser.amount_balance


@app.route('/register', methods=['GET', 'POST'])  # 회원가입 페이지
def register():
    form = RegisterForm()  # 회원가입 폼 생성
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

            return redirect('/')  # 회원가입 완료 후 홈화면으로 리다이렉션

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])  # 로그인 페이지
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
        

        # 로그인 성공 시 세션 정보 업데이트
        update_session_info()
        return redirect('/')  # 로그인에 성공하면 홈화면으로 redirect
        
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET']) # 로그아웃 페이지
def logout():
    session.pop('userid', None)
    return redirect('/') # 로그아웃 후 홈화면으로 redirect


@app.route('/buy_coin', methods=['GET', 'POST'])
def buy_coin():
    form = BuyCoinForm()

    if 'userid' not in session:  # 사용자가 로그인한 상태인지 확인합니다.
        return redirect('/login')

    # 로그인한 사용자의 정보를 가져옵니다.
    userid = session['userid']
    fcuser = Fcuser.query.filter_by(userid=userid).first()
    market = Market.query.first()

    if fcuser is None:
        return "Error: User not found"

    if form.validate_on_submit():
        coin_quantity = form.coin_quantity.data

        # 구매 처리
        if coin_quantity > 0 and fcuser is not None and market is not None:
            if market.coin_quantity >= coin_quantity:
                total_price = market.coin_price * coin_quantity
                if fcuser.amount >= total_price:
                    fcuser.coin += coin_quantity
                    fcuser.amount -= total_price
                    market.coin_quantity -= coin_quantity
                    db.session.commit()

                    # 세션에 업데이트된 정보 저장
                    session['amount'] = fcuser.amount
                    session['coin'] = fcuser.coin

        return redirect('/')  # 구매 후 홈페이지로 리다이렉트합니다.
        
    return render_template('buy_coin.html', form=form, userid=userid, fcuser=fcuser, market=market)


@app.route('/trade_coin', methods=['GET', 'POST'])
def trade_coin():
    form = TradeCoinForm()

    if 'userid' not in session:
        return redirect('/login')

    userid = session['userid']
    fcuser = Fcuser.query.filter_by(userid=userid).first()

    if fcuser is None:
        return "Error: User not found"

    if form.validate_on_submit():
        coin_quantity = form.coin_quantity.data
        coin_price = form.coin_price.data

        trade = Trade(seller_id=userid, coin_quantity=coin_quantity, coin_price=coin_price)
        db.session.add(trade)
        db.session.commit()

        flash('거래글이 작성되었습니다.', 'success')
        return redirect('/trade_create')

    current_coin_price = randint(80, 130)  # 랜덤한 코인 가격 생성
    session['current_coin_price'] = current_coin_price  # 세션에 코인 가격 저장

    trades = Trade.query.filter_by(buyer_id=None, is_completed=False).all()
    return render_template('trade_coin.html', userid=session['userid'], trades=trades, form=form, current_coin_price=current_coin_price)
    

@app.route('/trade_coin/select_trade', methods=['POST'])
def select_trade():
    if 'userid' not in session:
        return redirect('/login')

    userid = session['userid']
    fcuser = Fcuser.query.filter_by(userid=userid).first()

    if fcuser is None:
        return "에러: 사용자를 찾을 수 없습니다."

    trade_id = request.form.get('trade_id')
    trade = Trade.query.get(trade_id)

    if trade is None:
        return "에러: 거래를 찾을 수 없습니다."

    if trade.buyer_id is not None:
        return "에러: 거래는 이미 구매자에게 선택되었습니다."

    trade.buyer_id = userid
    trade.is_completed = True

    # 구매자와 판매자의 Fcuser 인스턴스를 가져옵니다.
    buyer = Fcuser.query.filter_by(userid=trade.buyer_id).first()
    seller = Fcuser.query.filter_by(userid=trade.seller_id).first()

    if buyer is None or seller is None:
        return "에러: 구매자 또는 판매자를 찾을 수 없습니다."

    # 구매자와 판매자의 코인 수량과 계좌 잔액을 업데이트합니다.
    buyer.coin += trade.coin_quantity
    buyer.amount -= (trade.coin_quantity * session['current_coin_price'])  # 세션에서 코인 가격을 가져옴

    seller.coin -= trade.coin_quantity
    seller.amount += (trade.coin_quantity * session['current_coin_price'])  # 세션에서 코인 가격을 가져옴

    # trade의 coin_price를 session['current_coin_price']으로 업데이트합니다.
    trade.coin_price = session['current_coin_price']

    db.session.commit()

    # 세션 정보 업데이트
    update_session_info()

    flash('거래가 선택되었습니다.', 'success')
    return redirect('/trade_coin')


@app.route('/trade_coin/create_trade', methods=['POST'])
def create_trade():
    if 'userid' not in session:
        flash('로그인이 필요합니다.', 'danger')
        return redirect('/login')

    seller = Fcuser.query.filter_by(userid=session['userid']).first()
    if not seller:
        flash('판매자 정보를 찾을 수 없습니다.', 'danger')
        return redirect('/trade_coin')

    coin_quantity = int(request.form['coin_quantity'])

    if coin_quantity <= 0:
        flash('코인의 수량은 1 이상이어야 합니다.', 'danger')
        return redirect('/trade_coin')

    # 판매자의 코인 수량 확인
    if seller.coin < coin_quantity:
        flash('보유한 코인 수량이 부족합니다.', 'danger')
        return redirect('/trade_coin')

     # 거래 생성
    trade = Trade()
    trade.seller_id = seller.userid
    trade.buyer_id = None
    trade.coin_quantity = coin_quantity
    trade.calculate_coin_price()

    db.session.add(trade)
    db.session.commit()

    flash('거래가 생성되었습니다.', 'success')
    return redirect('/trade_coin')


@app.route('/increase_balance', methods=['POST'])
def increase_balance():
    form = IncreaseBalanceForm()

    if 'userid' not in session:
        return redirect('/login')

    # 로그인한 사용자의 정보를 가져옵니다.
    userid = session['userid']
    fcuser = Fcuser.query.filter_by(userid=userid).first()

    if form.validate_on_submit():

        if fcuser is None:
            return "Error: User not found"

        amount_to_increase = form.amount_to_increase.data
        if amount_to_increase > 0:
            fcuser.amount += amount_to_increase
            db.session.commit()

            # 세션에 업데이트된 정보 저장
            session['amount'] = fcuser.amount

        return redirect('/')

    return render_template('increase_balance.html', form=form, userid=userid, fcuser=fcuser)


@app.route('/decrease_balance', methods=['POST'])
def decrease_balance():
    form = DecreaseBalanceForm()

    if 'userid' not in session:
        return redirect('/login')

    # 로그인한 사용자의 정보를 가져옵니다.
    userid = session['userid']
    fcuser = Fcuser.query.filter_by(userid=userid).first()

    if form.validate_on_submit():

        if fcuser is None:
            return "Error: User not found"

        amount_to_decrease = form.amount_to_decrease.data
        if amount_to_decrease > 0 and fcuser.amount >= amount_to_decrease:
            fcuser.amount -= amount_to_decrease
            db.session.commit()

            # 세션에 업데이트된 정보 저장
            session['amount'] = fcuser.amount

        return redirect('/')

    return render_template('decrease_balance.html', form=form, userid=userid, fcuser=fcuser)


@app.route('/')
def hello():
    userid = session.get('userid', None)
    market = Market.query.first()
    trades = Trade.query.all()  # Retrieve all Trade objects
    return render_template('main.html', userid=userid, market=market, trades=trades)


if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__))  # db파일을 절대경로로 생성
    dbfile = os.path.join(basedir, 'db.sqlite')  # db파일을 절대경로로 생성

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        dbfile  # sqlite를 사용함
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    # 사용자 요청의 끝마다 커밋(데이터베이스에 저장,수정,삭제등의 동작을 쌓아놨던 것들의 실행명령)을 한다.
    # 수정사항에 대한 track을 하지 않는다. True로 한다면 warning 메시지유발
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'

    csrf = CSRFProtect()
    csrf.init_app(app)

    db.init_app(app)
    with app.app_context():
        db.create_all()  # db 생성
        create_initial_market_data()  # 초기 market 데이터 생성
        
    app.run(host='127.0.0.1', port=5000, debug=True)
    # 포트번호는 기본 5000, 개발단계에서는 debug는 True
