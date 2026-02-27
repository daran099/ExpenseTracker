import enum
from sqlalchemy import Enum
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

#model for users
class UserBase(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(100), unique=True)

#model for transactions type
class TransactionType(enum.Enum):
    income = "income"
    expense = "expense"

#model for transactions
class TransactionBase(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    amount: Mapped[float] = mapped_column(Float)
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, native_enum=False), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

