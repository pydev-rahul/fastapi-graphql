# Fastapi with GraphQL

## For Build
Run the below command.
    docker-compose build


## For Migrations and Migrate: 
    docker-compose run web alembic revision --autogenerate

    docker-compose run web alembic upgrade head

## To run Project
    docker-compose up
**and go to**:

    http://localhost:8000


## Functionality We build with GraphQL
* Created API's as per requirements which requires Authorization Token.
* Created mutation for register user and it'll store data in PostgreSql with hashed password.
* Created query for login user it'll generate Token to authorize the User.
* Created Two collection which name is **local**(For facebook account data) and second one is **history**(for fb engagements data).
    * Created mutation's to store data in both collections.
* Created query to get active FB accounts.
* Created query to get the FB engagements by a specific range of datetime with the latest engagements of the day only.
* Created query to summarizing total likes, total shares, total comments of the latest engagements of the day by a specific range of datetime .
