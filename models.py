from flask_sqlalchemy import SQLAlchemy
import random

db = SQLAlchemy()  # SQLAlchemy를 사용해 데이터베이스 저장


class Fcuser(db.Model):
    __tablename__ = 'fcuser'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(64))
    userid = db.Column(db.String(32))
    username = db.Column(db.String(8))
    amount = db.Column(db.Numeric(asdecimal=False), default=0)
    coin = db.Column(db.Numeric(asdecimal=False), default=0)

class Market(db.Model):
    __tablename__ = 'market'  # 테이블 이름: market
    id = db.Column(db.Integer, primary_key=True)
    coin_name = db.Column(db.String(32)) # 코인 이름
    coin_quantity = db.Column(db.Integer, default=100)  # 장터에 남은 코인 수량
    coin_price = db.Column(db.Integer, default=100)  # 코인 가격

class Trade(db.Model):
    __tablename__ = 'trade'  # 테이블 이름: trade
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.String(100), nullable=False)
    buyer_id = db.Column(db.String(100), nullable=True)
    coin_quantity = db.Column(db.Integer, nullable=False)
    coin_price = db.Column(db.Integer, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

    # coin_quantity와 coin_price를 자동으로 계산하는 메서드
    def calculate_coin_price(self):
        self.coin_price = random.randint(80, 130)

    def calculate_coin_quantity(self):
        pass