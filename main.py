from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()


class Post(BaseModel):
	title: str
	content: str
	published: bool = True
	rating: Optional[int] = None


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


@app.get("/posts")
def get_posts():
	return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
	post_dict = post.model_dump()
	post_dict['id'] = randrange(0, 1000000)
	my_posts.append(post_dict)
	return {"data": post_dict}

# there is inter collision between /posts/latest_post and /posts/{id}, so order matters and we put latest_post route above because of that

@app.get("/posts/latest_post")
def get_latest_post():
  post = my_posts[int(len(my_posts)) - 1]
  print(type(post))
  return {"details": post}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):

  post = find_post(id)
  if not post:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"page with id {id} was not found!")
    #response.status_code = status.HTTP_404_NOT_FOUND
    #return {"message": f"page with id {id} was not found bruh!"}
  return {"message": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)	
def delete_post(id: int):
	index = find_index_post(id)
	if index == None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"page with id {id} was not found!")		
	my_posts.pop(index)
	return Response(status_code=status.HTTP_204_NO_CONTENT)



