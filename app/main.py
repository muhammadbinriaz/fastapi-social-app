from fastapi import FastAPI, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from  . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
  return {"message": "welcome to my api"}



@app.get("/posts", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):

  posts = db.query(models.Post).all()
  return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):

  new_post = models.Post(**post.model_dump())
  db.add(new_post)
  db.commit()
  db.refresh(new_post)
  return new_post


@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, response: Response,  db: Session = Depends(get_db)):

  post = db.query(models.Post).filter(models.Post.id == id).first()

  if not post:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"page with id {id} was not found!")
  return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)	
def delete_post(id: int, db: Session = Depends(get_db)):

  post_query = db.query(models.Post).filter(models.Post.id == id)

  if post_query.first() == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"page with id {id} was not found!")

  post_query.delete(synchronize_session=False)
  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):

  post_query = db.query(models.Post).filter(models.Post.id == id)
  post = post_query.first()

  if post == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"page with id {id} was not found!")

  post_query.update(updated_post.model_dump(), synchronize_session=False)
  db.commit()

  return post_query.first()
