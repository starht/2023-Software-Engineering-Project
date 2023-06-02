from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # SQLAlchemy를 사용해 데이터베이스 저장


class Fcuser(db.Model):
    __tablename__ = 'fcuser'  # 테이블 이름 : fcuser
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(64))  # 패스워드를 받아올 문자열길이
    userid = db.Column(db.String(32))  # 유저아이디를 받아올 문자열길이
    username = db.Column(db.String(8))
    amount = db.Column(db.Integer, default=0)  # 금액 필드 추가, 초기값 0
    coin = db.Column(db.Integer, default=0)  # 코인 필드 추가, 초기값 0

class Market(db.Model):
    __tablename__ = 'market'  # 테이블 이름: market
    id = db.Column(db.Integer, primary_key=True)
    coin_name = db.Column(db.String(32)) # 코인 이름
    coin_quantity = db.Column(db.Integer, default=100)  # 장터에 남은 코인 수량
    coin_price = db.Column(db.Integer, default=100)  # 코인 가격

