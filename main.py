from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


class Post(BaseModel):
	title: str
	content: str
	published: bool = True
	rating: Optional[int] = None



my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {"title": "favourite foods", "content": "I like pizza", "id": 2}]


@app.get("/")
def root():
  return {"message": "welcome to my api"}


@app.get("/posts")
def get_posts():
	return {"data": my_posts}


@app.post("/posts")
def create_post(post: Post):
	print(post.rating)  				# post.title, post.content etc available
	print(post.model_dump())		# same as post.dict()
	
	return {"data": post}

#title(string), content(string), category, Boolean published

#why i am getting method not allowed???