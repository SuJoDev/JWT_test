from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, JSON, Index
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Base(DeclarativeBase):
    pass

class UsersModel(Base):
    __tablename__ = "Users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()

    __table_args__ = (Index('ix_username', 'username'),)

    # def verify_password(self, plain_password: str) -> bool:
    #     return pwd_context.verify(plain_password, self.password)