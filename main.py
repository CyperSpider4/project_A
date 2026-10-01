from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from uuid import uuid4


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_methods=["*"],
# )

# @app.get("/hello-word")
# def read_root():
#     return {"message": "Hello, world!"}


class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool


class TaskCreateSchema(BaseModel):
    title: str


tasks: list[TaskSchema] = []


@app.get("/tasks")
def read_tasks() -> list[TaskSchema]:
    return tasks


@app.post("/tasks")
def create_task(payload: TaskCreateSchema) -> TaskSchema:
    new_task = TaskSchema(
        id=str(uuid4()), title=payload.title, completed=False)

    tasks.append(new_task)
    return new_task
