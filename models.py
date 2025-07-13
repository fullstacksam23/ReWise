from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class QuestionPaper(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(nullable=False)
    aiml: Mapped[bool] = mapped_column(default=False)
    cse: Mapped[bool] = mapped_column(default=False)
    ds: Mapped[bool] = mapped_column(default=False)
    it: Mapped[bool] = mapped_column(default=False)
    csbs: Mapped[bool] = mapped_column(default=False)
    eee: Mapped[bool] = mapped_column(default=False)
    ece: Mapped[bool] = mapped_column(default=False)
    mech: Mapped[bool] = mapped_column(default=False)
    ce: Mapped[bool] = mapped_column(default=False)
    year1: Mapped[bool] = mapped_column(default=False)
    year2: Mapped[bool] = mapped_column(default=False)
    year3: Mapped[bool] = mapped_column(default=False)
    year4: Mapped[bool] = mapped_column(default=False)
    paperyear: Mapped[str] = mapped_column(nullable=False)
    set: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    upload_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    filepath: Mapped[str] = mapped_column(nullable=False)
