import boto3
from boto3.dynamodb.conditions import Attr
import config






class DatabaseManager():

    def __init__(self) -> None:


        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=config.AWS_SERVER_PUBLIC_KEY,
            aws_secret_access_key=config.AWS_SERVER_SECRET_KEY,
            region_name="eu-west-3",
        )


        self.profile_table = self.dynamodb.Table("npchill")
        self.profile_template = {
            "birthday_date_day": "",
            "birthday_date_month": "",
            "birthday_ping": True,

        }

        



    def get_profile(self, user_id: str) -> dict:
        try:
            return self.profile_table.get_item(Key={'user_id':user_id})['Item']
        except:
            return {}

    def get_all_profiles(self):
        return self.profile_table.scan()['Items']

    def get_users_birthday(self, month):
        return self.profile_table.scan(FilterExpression=Attr('birthday_date_month').eq(month))['Items']


    def insert_one(self, user_id: str, profile: dict) -> int:     # Return HTTP status code
        response = self.profile_table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression='SET birthday_date_day = :a, birthday_date_month = :b, birthday_ping = :c',
            ExpressionAttributeValues={
                ':a': profile['birthday_date_day'],
                ':b': profile['birthday_date_month'],
                ':c': True,

            },
            ReturnValues='ALL_NEW'
        )
        return response["ResponseMetadata"]["HTTPStatusCode"]
    

    def update_birthday(self, user_id, day, month):
        response = self.profile_table.update_item(
            Key={
                'user_id': str(user_id)
            },
            UpdateExpression='SET birthday_date_day = :a, birthday_date_month = :b',
            ExpressionAttributeValues={
                ':a': day,
                ':b': month

            },
            ReturnValues='ALL_NEW'
        )
        return response["ResponseMetadata"]["HTTPStatusCode"]


