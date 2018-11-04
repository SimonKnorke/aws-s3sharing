""""
script to create new S3 bucket and iam_client user with read write permission on this folder only

author: Simon
created: 2019-10-18
"""

import json
import re
from aws_resource_helpers import *

VALID_REGIONS = ['ap-south-1', 'eu-west-3', 'eu-west-2', 'eu-west-1', 'ap-northeast-2', 'ap-northeast-1', 'sa-east-1',
                 'ca-central-1', 'ap-southeast-1', 'ap-southeast-2', 'eu-central-1', 'us-east-1', 'us-east-2',
                 'us-west-1', 'us-west-2']
DEFAULT_REGION = 'eu-central-1'
BUCKET_NAME_PATTERN = '(?=^.{3,63}$)(?!^(\d+\.)+\d+$)' \
                      '(^(([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])\.)*([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])$)'
CLIENT_POLICY_NAME = 's3ClientPolicy'
CLIENT_PASSWORD_RESET_REQUIRED = False


def main():
    print('INFO: Your AWS User account should be added to IAM group "S3ShareGroup" or'
          ' have permissions IAMFullAccess and AmazonS3FullAccess.\n'
          '--> Starting AWS S3 client script... (you can quit with "\q")')

    bucket_region = get_valid_region('Region (or press enter for {}): '.format(DEFAULT_REGION))
    if bucket_region is None:
        return

    s3_client, s3_resource, iam_client = aws_login('Aws profile name (or enter to skip): ', bucket_region)
    if s3_client is None:
        return

    all_bucket_names = get_all_bucket_names(s3_resource)
    all_user_names = get_all_user_names(iam_client)
    if all_bucket_names is None or all_user_names is None:
        return

    bucket_name, bucket_already_exists = get_valid_bucket_name('Name of S3 bucket: ', all_bucket_names, s3_client)
    user_name = get_valid_user_name('New User name (for bucket access): ', all_user_names)

    account_password_policy = get_password_policy(iam_client)
    print_password_policy(account_password_policy)

    user_password = input('Set user password: ')

    print_final_check(bucket_name, bucket_region, user_name, user_password)

    if continuation_prompt('Continue?', 'y'):
        response = create_s3_bucket(s3_client, bucket_name, bucket_region, bucket_already_exists)
        if response is None:
            return

        bucket_link = 'https://s3.console.aws.amazon.com/s3/buckets/{}/'.format(bucket_name)

        response = iam_client.create_user(UserName=user_name)
        response = iam_client.create_login_profile(UserName=user_name, Password=user_password,
                                                   PasswordResetRequired=CLIENT_PASSWORD_RESET_REQUIRED)
        policy_json = create_bucket_user_policy(bucket_name)
        response = iam_client.put_user_policy(PolicyDocument=policy_json, PolicyName=CLIENT_POLICY_NAME,
                                              UserName=user_name)

        login_filename = '{}_login.txt'.format(user_name)
        response_string = 'Link to bucket: {}\nIAM User name: {}\nPassword: {}'.format(
            bucket_link, user_name, user_password)

        print('--> Successfully created S3 bucket and IAM User. Created login file "{}"'.format(login_filename))
        print(response_string)
        with open(login_filename, 'w') as f:
            f.write(response_string)
    else:
        return


def continuation_prompt(prompt, required_answer):
    continuation_answer = input('{} ({}): '.format(prompt, required_answer))
    if continuation_answer == required_answer:
        return True
    else:
        print('--> Terminate process...')
        return False


def get_valid_region(prompt):
    while True:
        bucket_region = input(prompt)
        if bucket_region == '\q':
            print('--> Quit process...')
            return None
        elif bucket_region == '':
            bucket_region = DEFAULT_REGION
            print('--> Used default region "{}"'.format(DEFAULT_REGION))
            break
        elif bucket_region not in VALID_REGIONS:
            print('--> ValueError: Region "{}" is not available. Please try again.\n'
                  'INFO: Valid regions are: {}'.format(bucket_region, VALID_REGIONS))
            continue
        else:
            print('--> Used region "{}"'.format(bucket_region))
            break
    return bucket_region


def get_valid_bucket_name(prompt, all_bucket_names, s3_client):
    bucket_already_exists = False
    print('INFO:\tYou can choose existing bucket or create a new one (name has to be unique across AWS!).')
    while True:
        bucket_name = input(prompt)
        if bucket_name in all_bucket_names:
            answer = input('WARNING: Bucket "{}" already exists. Continue with existing one?\n(y/n): '.format(bucket_name))
            if answer == 'y':
                bucket_already_exists = True
                print('--> Used existing bucket "{}"...'.format(bucket_name))
                break
            else:
                continue
        elif not re.match(BUCKET_NAME_PATTERN, bucket_name):
            print('InvalidBucketNameError: The specified bucket name "{}" is not valid. Please try again!'.format(bucket_name))
            continue
        elif bucket_is_not_unique(s3_client, bucket_name):
            print('BucketAlreadyExistsError: Your bucket already exists across the AWS platform. Please try again!')
            continue
        else:
            break
    return bucket_name, bucket_already_exists


def get_valid_user_name(prompt, all_user_names):
    while True:
        user_name = input(prompt)
        if len(user_name) == 0:
            print('ValueError: Please enter at least one character.')
            continue
        elif user_name in all_user_names:
            print('WARNING: User "{}" already exists. Please enter new one...'.format(user_name))
            continue
        else:
            print('--> Used user name "{}".'.format(user_name))
            break
    return user_name


def print_final_check(bucket_name, bucket_region, user_name, user_password):
    print('FINAL CHECK:\tS3 bucket "{}" will be created in region "{}".'.format(bucket_name, bucket_region))
    print('\t\tIam User: "{}", User password: "{}"'.format(user_name, user_password))


def create_bucket_user_policy(bucket_name):
    """USER POLICY: Allow 1) ListBucket option to folder and 2) put, get, delete option to objects inside"""

    policy_dict = {'Version': '2012-10-17',
                   'Statement': [{'Sid': 'VisualEditor0',
                                  'Effect': 'Allow',
                                  'Action': 's3:ListBucket',
                                  'Resource': 'arn:aws:s3:::{}'.format(bucket_name)},
                                 {'Sid': 'VisualEditor1',
                                  'Effect': 'Allow',
                                  'Action': ['s3:PutObject', 's3:GetObject', 's3:DeleteObject'],
                                  'Resource': 'arn:aws:s3:::{}/*'.format(bucket_name)}]}
    policy_json = json.dumps(policy_dict)
    return policy_json


if __name__ == '__main__':
    main()
