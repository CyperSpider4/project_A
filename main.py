from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status, HTTPException, Depends
from uuid import uuid4
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:5432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))


class TaskORM(Base):
    __tablename__ = "tasks"
    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)


class CategoryORM(Base):
    __tablename__ = "categories"
    name: Mapped[str]


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool


class TaskCreateSchema(BaseModel):
    title: str


class TaskUpdateSchema(BaseModel):
    title: str | None = None
    completed: bool | None = None


class Category(BaseModel):
    id: str
    name: str


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: str | None = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def task_orm_to_model(task_orm: TaskORM) -> TaskSchema:
    return TaskSchema(id=task_orm.id, title=task_orm.title, completed=task_orm.completed)


def category_orm_to_model(category_orm: CategoryORM) -> Category:
    return Category(id=category_orm.id, name=category_orm.name)


@app.get("/tasks")
def read_tasks(db: Session = Depends(get_db)) -> list[TaskSchema]:
    tasks_from_db = db.scalars(select(TaskORM)).all()
    return [task_orm_to_model(t) for t in tasks_from_db]


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema, db: Session = Depends(get_db)) -> TaskSchema:
    new_task = TaskORM(title=payload.title, completed=False)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return task_orm_to_model(new_task)


@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema, db: Session = Depends(get_db)) -> TaskSchema:
    task_for_update = db.get(TaskORM, task_id)
    if task_for_update is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if payload.title is not None:
        task_for_update.title = payload.title
    if payload.completed is not None:
        task_for_update.completed = payload.completed

    db.commit()
    db.refresh(task_for_update)
    return task_orm_to_model(task_for_update)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)) -> None:
    task_for_delete = db.get(TaskORM, task_id)
    if task_for_delete is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    db.delete(task_for_delete)
    db.commit()


@app.get("/categories")
def read_categories(db: Session = Depends(get_db)) -> list[Category]:
    categories_from_db = db.scalars(select(CategoryORM)).all()
    return [category_orm_to_model(c) for c in categories_from_db]


@app.post("/categories", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> Category:
    new_category = CategoryORM(name=payload.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return category_orm_to_model(new_category)


@app.patch("/categories/{category_id}")
def update_category(category_id: str, payload: CategoryUpdate, db: Session = Depends(get_db)) -> Category:
    category_for_update = db.get(CategoryORM, category_id)
    if category_for_update is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    if payload.name is not None:
        category_for_update.name = payload.name

    db.commit()
    db.refresh(category_for_update)
    return category_orm_to_model(category_for_update)


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, db: Session = Depends(get_db)) -> None:
    category_for_delete = db.get(CategoryORM, category_id)
    if category_for_delete is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    db.delete(category_for_delete)
    db.commit()

