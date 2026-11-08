from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.models.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    from app.models.task import TaskORM
    Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()
app = FastAPI(lifespan=lifespan)


app.add_middleware(
     CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


app.include_router(api_router)

# def task_orm_to_model(task_orm: TaskORM) -> TaskSchema:
#     return TaskSchema(id=task_orm.id, title=task_orm.title, completed=task_orm.completed)


# def category_orm_to_model(category_orm: CategoryORM) -> Category:
#     return Category(id=category_orm.id, name=category_orm.name)



# @app.get("/categories")
# def read_categories(db: Session = Depends(get_db)) -> list[Category]:
#     categories_from_db = db.scalars(select(CategoryORM)).all()
#     return [category_orm_to_model(c) for c in categories_from_db]


# @app.post("/categories", status_code=status.HTTP_201_CREATED)
# def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> Category:
#     new_category = CategoryORM(name=payload.name)
#     db.add(new_category)
#     db.commit()
#     db.refresh(new_category)
#     return category_orm_to_model(new_category)


# @app.patch("/categories/{category_id}")
# def update_category(category_id: str, payload: CategoryUpdate, db: Session = Depends(get_db)) -> Category:
#     category_for_update = db.get(CategoryORM, category_id)
#     if category_for_update is None:
#         raise HTTPException(status_code=404, detail="Категория не найдена")

#     if payload.name is not None:
#         category_for_update.name = payload.name

#     db.commit()
#     db.refresh(category_for_update)
#     return category_orm_to_model(category_for_update)


# @app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_category(category_id: str, db: Session = Depends(get_db)) -> None:
#     category_for_delete = db.get(CategoryORM, category_id)
#     if category_for_delete is None:
#         raise HTTPException(status_code=404, detail="Категория не найдена")
#     db.delete(category_for_delete)
#     db.commit()

