from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from  . import models 
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


class Post(BaseModel):
	title: str
	content: str
	published: bool = True

while True:	

		try:
			conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='111222333@pak', cursor_factory=RealDictCursor)
			cursor = conn.cursor()
			print("Database connection was successful!")
			break
		except Exception as error:
			print("Connection to database failed!")
			print("Error: ", error)
time.sleep(2)


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {"title": "favourite foods", "content": "I like pizza", "id": 2}]

def find_post(id):
  for p in my_posts:
    if p['id'] == id:
      return p


def find_index_post(id):
  for i, p in enumerate(my_posts):
			if p['id'] == id:
				return i


@app.get("/")
def root():
  return {"message": "welcome to my api"}


@app.get("sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
  posts = db.query(models.Post).all()
  return {"data": "success"}



@app.get("/posts")
def get_posts():
  cursor.execute("""SELECT * FROM posts""")
  posts = cursor.fetchall()
  return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
  cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
  new_post = cursor.fetchone()
  conn.commit()
  print(new_post)
  return {"data": new_post}
	# return {"data": "created post"}

# there is inter collision between /posts/latest_post and /posts/{id}, so order matters and we put latest_post route above because of that



@app.get("/posts/{id}")
def get_post(id: int, response: Response):
  cursor.execute("""SELECT * from posts WHERE id = %s """, (id,)) # we put (id,) inplace of str(id) as (id,) creates a single-item tuple, and psycopg2 execute() method expects second arg values to be sequence like tuple or list, and we don't need to convert id to a string; psycopg2 handles the type conversion automatically. 
  post = cursor.fetchone()

  if not post:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"page with id {id} was not found!")
    #response.status_code = status.HTTP_404_NOT_FOUND
    #return {"message": f"page with id {id} was not found bruh!"}
  return {"message": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)	
def delete_post(id: int):
  
  cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
  deleted_post = cursor.fetchone()
  conn.commit()

  if deleted_post == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"page with id {id} was not found!")
  return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
  
  cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, id))
  updated_post = cursor.fetchone()
  conn.commit()

  if updated_post == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"page with id {id} was not found!")
  return {"data": updated_post}
