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



@app.get("/")
def root():
  return {"message": "welcome to my api"}


@app.post("/posts")
def create_post(post: Post):
	print(post.rating)  				# post.title, post.content etc available
	print(post.model_dump())		# same as post.dict()
	
	return {"data": post}

#title(string), content(string), category, Boolean published