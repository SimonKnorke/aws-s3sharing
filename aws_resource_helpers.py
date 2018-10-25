""""
Helper functions to access AWS resources

Author: Simon Wohlfahrt
Created: 2019-10-25
"""

import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import ProfileNotFound


def aws_login(prompt, bucket_region):
    """Whether uses credentials of existing aws profile or starts default session"""
    while True:
        aws_profile = input(prompt)
        if aws_profile == '\q':
            print('--> Quit process...')
            return None, None, None
        elif aws_profile != '':
            try:
                boto3.setup_default_session(profile_name=aws_profile, region_name=bucket_region)  # idalab, knorke
                s3_client = boto3.client('s3')
                s3_resource = boto3.resource('s3')
                iam_client = boto3.client('iam')
                break
            except ProfileNotFound:
                print('ProfileNotFoundError: profile "{}" does not exist. Please try again.\n'
                      'INFO: You can check ~/.aws/config or ~/.aws/credentials for your profiles '
                      'or add a new profile with "aws configure --profile <profile-name>"'.format(aws_profile))
                continue

        else:
            access_key = input('AWS Access Key ID: ')
            secret_key = input('AWS Secret Access Key: ')
            config_dict = {'region_name': bucket_region, 'aws_access_key_id': access_key, 'aws_secret_access_key': secret_key}
            s3_client = boto3.client('s3', **config_dict)
            s3_resource = boto3.resource('s3',  **config_dict)
            iam_client = boto3.client('iam',  **config_dict)
            break
    return s3_client, s3_resource, iam_client


def get_all_bucket_names(s3_resource):
    try:
        return [bucket.name for bucket in s3_resource.buckets.all()]
    except ClientError as e:
        if e.response["Error"]["Code"] == "AccessDenied":
            print('ClientError (AccessDenied): You are not allowed to list the S3 buckets.'
                  ' Ask admin to add you username to the IAM group!')
        else:
            raise e
        print('--> Terminate process...')
        return None


def get_all_user_names(iam_client):
    try:
        all_user_names = [key['UserName'] for key in iam_client.list_users()['Users']]
        return all_user_names
    except ClientError as e:
        if e.response["Error"]["Code"] == "AccessDenied":
            print('ClientError (AccessDenied): You are not allowed to list users.'
                  ' Ask admin to add you username to the IAM group!')
        else:
            raise e
        print('--> Terminate process...')
        return None


def get_password_policy(iam_client):
    try:
        account_password_policy = iam_client.get_account_password_policy()['PasswordPolicy']
        return account_password_policy
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            return None
        else:
            raise e


def print_password_policy(account_password_policy):
    if account_password_policy is None:
        print('INFO: There is no password policy, so you can type what you want...')
    else:
        print('INFO!\tAccount password policy:')
        for key in account_password_policy:
            if account_password_policy[key]:
                print('\t{}: {}'.format(key, account_password_policy[key]))


#def print_password_policy(iam_client):
#    try:
#        account_password_policy = iam_client.get_account_password_policy()['PasswordPolicy']
#        print('INFO!\tAccount password policy:')
#        for key in account_password_policy:
#            if account_password_policy[key]:
#                print('\t{}: {}'.format(key, account_password_policy[key]))
#    except ClientError as e:
#        if e.response["Error"]["Code"] == "NoSuchEntity":
#            print('INFO: There is no password policy, so you can type what you want...')
#        else:
#            raise e


def create_s3_bucket(s3_client, bucket_name, bucket_region, bucket_already_exists):
    if not bucket_already_exists:
        try:
            response = s3_client.create_bucket(Bucket=bucket_name,
                                               CreateBucketConfiguration={'LocationConstraint': bucket_region})
        except ClientError as e:
            raise e