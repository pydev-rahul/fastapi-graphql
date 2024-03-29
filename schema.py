from pydantic import BaseModel
from datetime import date
from datetime import datetime, timedelta
import graphene
from graphene_pydantic import PydanticInputObjectType, PydanticObjectType
from models import User as u, RegisterUser as ModelRegisterUser
from db import SessionLocal, session, local_collection,history_collection
from hash import Hash, create_access_token,create_refresh_token, ALGORITHM, JWT_SECRET_KEY
from fastapi import  Depends, HTTPException, status, Request
from decorators import authenticate
import jwt
from jwt.exceptions import ExpiredSignatureError

class LoginRequest(BaseModel):
    username: str
    password: str

sessiondata = SessionLocal()
class User(BaseModel):
    id:int
    first_name: str
    last_name: str
    age: int

    class Config:
        orm_mode = True

class UserGrapheneModel(PydanticObjectType):
    class Meta:
        model = User

class UserGrapheneInputModel(PydanticInputObjectType):
    class Meta:
        model = User
        exclude_fields = ('id')


class RegisterUser(BaseModel):
    id:int
    email: str
    password: str

    class Config:
        orm_mode = True

class RegisterUserGrapheneModel(PydanticObjectType):
    class Meta:
        model = RegisterUser

class RegisterUserGrapheneInputModel(PydanticInputObjectType):
    class Meta:
        model = RegisterUser
        exclude_fields = ('id')

class FBDetails(BaseModel):
    id:str 
    fb_name:str
    fb_account_id:int
    fb_account_active:bool
    class Config:
        orm_mode = True
        arbitrary_types_allowed= True

class FBDetailsGrapheneModel(PydanticObjectType):
    class Meta:
        model = FBDetails

class FBDetailsInputModel(PydanticInputObjectType):
    class Meta:
        model = FBDetails
        exclude_fields = ('id')

class FBHistoryRecord(BaseModel):
    id:str 
    fb_account_id:int
    fb_post_id:int
    fb_post_likes:int
    fb_post_comments:int
    fb_post_shares:int
    date_time: date= datetime.now()#datetime(2022, 12, 29, 12, 2, 28, 539624)

    class Config:
        orm_mode = True
        arbitrary_types_allowed= True

class FBHistoryRecordGrapheneModel(PydanticObjectType):
    class Meta:
        model = FBHistoryRecord

class FBHistoryRecordInputModel(PydanticInputObjectType):
    class Meta:
        model = FBHistoryRecord
        exclude_fields = ('id')


class SummaryDetails(BaseModel):
    comments:int
    likes:int
    shares:int
    class Config:
        orm_mode = True

class SummaryDetailsGrapheneModel(PydanticObjectType):
    class Meta:
        model = SummaryDetails

class LoginDetails(BaseModel): 
    username:str
    password:str
    class Config:
        orm_mode = True
class LoginInputModel(PydanticInputObjectType):
    class Meta:
        model = LoginDetails


class TokenGrapheneModel(BaseModel):
    access_token:str
    refresh_token:str
    class Config:
        orm_mode = True

class TokenGrapheneoutputModel(PydanticObjectType):
    class Meta:
        model = TokenGrapheneModel


class Query(graphene.ObjectType):
    list_users = graphene.List(UserGrapheneModel)
    get_single_user = graphene.Field(UserGrapheneModel, user_id=graphene.NonNull(graphene.Int))
    list_of_register_users = graphene.List(RegisterUserGrapheneModel)
    get_single_register_user = graphene.Field(RegisterUserGrapheneModel, user_id=graphene.NonNull(graphene.Int))
    list_of_fb_details = graphene.List(FBDetailsGrapheneModel)
    active_fb_accounts = graphene.List(FBDetailsGrapheneModel)
    get_data = graphene.List(FBHistoryRecordGrapheneModel,from_date=graphene.NonNull(graphene.Date),to_date=graphene.NonNull(graphene.Date))
    get_data_summary = graphene.Field(SummaryDetailsGrapheneModel,from_date=graphene.NonNull(graphene.Date),to_date=graphene.NonNull(graphene.Date))
    login = graphene.Field(TokenGrapheneoutputModel,username=graphene.NonNull(graphene.String),password=graphene.NonNull(graphene.String))


    @staticmethod
    async def resolve_list_users(parent, info):
        a = await u.get_all()
        return list(User(id=i.id,first_name=i.first_name,last_name=i.last_name,age=i.age) for i in a)
    
    @staticmethod
    def resolve_get_single_user(parent, info, user_id):
        obj = u.get(id=user_id)
        print(obj)
        return obj

    @authenticate
    def resolve_list_of_register_users(parent, info):
        """
        Display all the register users username and password. 
    
    
        Parameters:
        arg1 (object): Default argument of mutation.
        arg2 (object): Default argument of mutation.

    
        Returns:
        list: All User's details dict with it's information
        """
        all_register_users = session.query(ModelRegisterUser).all()
        return all_register_users    
    
    @authenticate
    def resolve_get_single_register_user(parent, info,user_id):
        """
        Geting single register User from given id 
    
    
        Parameters:
        arg1 (object): Default argument of mutation.
        arg2 (object): Default argument of mutation.
        arg3 (int): Id of perticuler User.

    
        Returns:
        Dict: All the information of perticuler User which stored in DB. 
        """
        fetched_user = session.query(ModelRegisterUser).filter(ModelRegisterUser.id==user_id).first()
        return fetched_user
    
    @authenticate
    def resolve_list_of_fb_details(parent, info):
        """
        Geting all the User's facebook account details we crawled.
    
    
        Parameters:
        arg1 (object): Default argument of mutation.
        arg2 (object): Default argument of mutation.

    
        Returns:
        List: User's facebook account all details which is stored in mongo db. 
        """
        all_fb_details = local_collection.find()
        final_data = []
        for data_dict in list(all_fb_details):
            data_dict["id"]= str(data_dict["_id"])
            data_dict.pop("_id")
            final=FBDetails(**data_dict)
            final_data.append(final)

        return final_data

    @authenticate
    def resolve_active_fb_accounts(parent, info):
        """
        Geting all the User's active facebook account details.
    
    
        Parameters:
        arg1 (object): Default argument of mutation.
        arg2 (object): Default argument of mutation.

    
        Returns:
        List: All the active accounts of facebook which we crawled. 
        """
        data = local_collection.find({"fb_account_active":True})
        final_data = []
        for data_dict in list(data):
            data_dict["id"]= str(data_dict["_id"])
            data_dict.pop("_id")
            final=FBDetails(**data_dict)
            final_data.append(final)
        return final_data
    
    @authenticate
    def resolve_get_data(parent, info,from_date, to_date):
        """
        Getting the FB engagements by a specific range of datetime with the latest engagements of the day only.
    
    
        Parameters:
        arg1 (object): Default argument of mutation.
        arg2 (object): Default argument of mutation.
        arg3 (Datetime): From Date.
        arg4 (Datetime): To Date.

    
        Returns:
        List: All FB engagements by a specific range of datetime with the latest engagements of the day only.
        """
        start_date = datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, 0)
        end_date = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, 0)
        
        query =[{
                "$match": {
                    "date_time": {
                            "$gte": start_date,
                            "$lt": end_date
                        }
                    }
                },
                {
                    "$sort": {
                        "date_time": 1
                    }
                },
                {
                    "$group": {
                        "_id": { "$dayOfMonth": "$date_time" },
                        "lastRecord": { "$last": "$$ROOT" },
                        # "totalAmount": { "$sum": "$fb_post_likes" },
                    }
                },
                {
                    "$sort": {
                        "_id": 1
                    }
                }]
        aggregate_data = history_collection.aggregate(query)
        list_query_Data = list(aggregate_data)
        final_data =[]
        for data in list_query_Data:
            data = data["lastRecord"]
            data["id"]= str(data["_id"])
            data.pop("_id")
            final=FBHistoryRecordGrapheneModel(**data)
            final_data.append(final)
        return final_data

    @authenticate
    def resolve_get_data_summary(parent, info,from_date, to_date):
        """
        Getting the FB engagements summary data by a specific range of datetime with the latest engagements of the day only.
    
    
        Parameters:
        arg1 (object): Default argument of mutation.
        arg2 (object): Default argument of mutation.
        arg3 (Datetime): From Date.
        arg4 (Datetime): To Date.

        Returns:
        List: All FB engagements summary data by a specific range of datetime with the latest engagements of the day only.
        """
        start_date = datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, 0)
        end_date = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, 0)
        
        query =[{
                "$match": {
                    "date_time": {
                            "$gte": start_date,
                            "$lt": end_date
                        }
                    }
                },
                {
                    "$sort": {
                        "date_time": 1
                    }
                },
                {
                    "$group": {
                        "_id": { "$dayOfMonth": "$date_time" },
                        "lastRecord": { "$last": "$$ROOT" },
                    }
                },
                 {
                    "$project": {
                        "likes": { "$sum": "$lastRecord.fb_post_likes" },
                        "comments": { "$sum": "$lastRecord.fb_post_comments" },
                        "shares": { "$sum": "$lastRecord.fb_post_shares" },
                    }
                },
                {
                    "$sort": {
                        "_id": 1
                    }
                }]
        aggregate_data = history_collection.aggregate(query)
        list_query_Data = list(aggregate_data)
        final_data ={
            "likes":0,
            "comments":0,
            "shares":0,
        }

        for data in list_query_Data:
            final_data["likes"]+= data["likes"]
            final_data["comments"]+= data["comments"]
            final_data["shares"]+= data["shares"]
        
        final=SummaryDetailsGrapheneModel(comments=final_data["likes"], likes=final_data["comments"], shares=final_data["shares"])
        return final

    @staticmethod
    def resolve_login(parent, info,username,password):
        user = session.query(ModelRegisterUser).filter(ModelRegisterUser.email==username).first()
        
        if not user:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
            )

        if not Hash.verify(user.password, password):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect Password"
            )

        access_token= create_access_token(username),
        refresh_token= create_refresh_token(username),

        print(access_token)    
        tokens = TokenGrapheneModel(access_token=access_token[0],refresh_token=refresh_token[0])

        return tokens


class CreateUser(graphene.Mutation):
    class Arguments:
        user_details = UserGrapheneInputModel()

    Output = UserGrapheneModel

    @authenticate
    async def mutate(parent, info, user_details):
        data = await u.create(**user_details)
        user2 = await u.get(data)
        final_data = User(**user2).dict()
        user = User(**final_data)
        return user

class CreateRegisterUser(graphene.Mutation):
    class Arguments:
        user_details = RegisterUserGrapheneInputModel()

    Output = RegisterUserGrapheneModel

    @staticmethod
    async def mutate(parent, info, user_details):
        """
        Register user via mutation and store username and hashed password.
    
    
        Parameters:
        arg1 (object): Default argument of mutation.
        arg2 (object): Default argument of mutation.
        arg3 (dict): User's register details like username and password.

    
        Returns:
        dict: Register user details with username and hashed password.
        """
        hash_password = Hash.bcrypt(user_details.password)
        
        registeruser = ModelRegisterUser(email=user_details.email,password =hash_password)
        sessiondata.add(registeruser)
        sessiondata.commit()
        sessiondata.refresh(registeruser)
        return registeruser

class CreateFBDetails(graphene.Mutation):
    class Arguments:
        fb_details = FBDetailsInputModel()

    Output = FBDetailsGrapheneModel

    @authenticate
    async def mutate(parent, info, fb_details):
        """
        Storing facebook account details of user's 
    
    
        Parameters:
        arg1 (object): Default argument of mutation.
        arg2 (object): Default argument of mutation.
        arg3 (dict): User's facebook details like Name, AccounId , IsActivate account.

    
        Returns:
        dict: User's facebook account all details which is stored in mongo db.
        """

        result = local_collection.insert_one(fb_details.__dict__)
        fb_details["id"] =str(result.inserted_id)
        final=FBDetails(**fb_details)
        return final

class CreateFBHistorydetails(graphene.Mutation):
    class Arguments:
        fb_history_details = FBHistoryRecordInputModel()

    Output = FBHistoryRecordGrapheneModel

    @authenticate
    async def mutate(parent, info, fb_history_details):
        """
        Storing facebook account post details.
    
    
        Parameters:
        arg1 (object): Default argument of mutation.
        arg2 (object): Default argument of mutation.
        arg3 (dict): User's facebook account details like PostId, Comment, Likes, Shares.

    
        Returns:
        dict: User's facebook post's all details which is stored in mongo db.
        """
        result = history_collection.insert_one(fb_history_details.__dict__)
        fb_history_details["id"] =str(result.inserted_id)
        final=FBHistoryRecord(**fb_history_details)
        return final

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_myuser = CreateRegisterUser.Field()
    create_fbdetails= CreateFBDetails.Field()
    create_fbhistorydetails= CreateFBHistorydetails.Field()
    
