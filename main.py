import uvicorn
from models import User as ModelUser
from app import app
import graphene
from starlette_graphene3 import GraphQLApp, make_graphiql_handler,make_playground_handler
from schema import Query,Mutation, LoginRequest
from typing import List
import models
from db import engine, get_db
from sqlalchemy.orm import Session
import models

models.Base.metadata.create_all(bind=engine)



schema = graphene.Schema(query=Query,mutation=Mutation)

# app.add_route("/graphql", GraphQLApp(schema, playground=True,on_get=make_graphiql_handler()))
app.add_route("/graphql", GraphQLApp(schema, on_get=make_playground_handler()))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
