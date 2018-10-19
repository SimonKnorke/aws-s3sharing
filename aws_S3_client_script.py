""""
script to create new S3 bucket and iam_client user with read write permission on this folder (and nothing else)

author: Simon
created: 2019-10-18
"""

import boto3
import json

# USER_ACCESS_KEY =
# USER_SECRET_KEY =

CLIENT_POLICY_NAME = 's3ClientPolicy'
DEFAULT_REGION = 'eu-central-1'


def main():
    bucket_region = input('Region (or enter to continue): ')
    if bucket_region == '':
        bucket_region = DEFAULT_REGION
        print('--> Used default region "{}"'.format(bucket_region))

    aws_profile = input('Aws profile name (or enter to continue): ')
    if aws_profile != '':
        boto3.setup_default_session(profile_name=aws_profile, region_name=bucket_region)  # idalab, knorke
        s3_client = boto3.client('s3')
        iam_client = boto3.client('iam')
    else:
        user_access_key = input('AWS Access Key ID: ')
        user_secret_key = input('AWS Secret Access Key: ')
        s3_client = boto3.client('s3', region_name=bucket_region,
                                 aws_access_key_id=user_access_key,
                                 aws_secret_access_key=user_secret_key)
        iam_client = boto3.client('iam', region_name=bucket_region,
                                 aws_access_key_id=user_access_key,
                                 aws_secret_access_key=user_secret_key)

    bucket_name = input('Name of S3 bucket: ')

    user_name = input('User name: ')
    login_filename = '{}_login.txt'.format(user_name)
    user_password = input('Set user password: ')
    answer = input('INFO: S3 bucket "{}" will be created in region "{}"\nIam user "{}", password "{}"\nContinue? (y/n): '.format(
        bucket_name, bucket_region, user_name, user_password))

    if answer != 'y':
        print('--> Terminate process...')
        return
    else:
        # S3 BUCKET STUFF
        response = s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': bucket_region}, )
        bucket_link = 'https://s3.console.aws.amazon.com/s3/buckets/{}/'.format(bucket_name)

        # IAM USER STUFF
        response = iam_client.create_user(UserName=user_name)
        response = iam_client.create_login_profile(
            UserName=user_name,
            Password=user_password,
            PasswordResetRequired=False)

        # USER POLICY: Allow 1) ListBucket option to folder and 2) put, get, delete option to objects inside
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
        response = iam_client.put_user_policy(
            PolicyDocument=policy_json,
            PolicyName=CLIENT_POLICY_NAME,
            UserName=user_name,
        )

        with open(login_filename, 'w') as f:
            f.write('Link to bucket: {}\nIAM User name: {}\nPassword: {}'.format(bucket_link, user_name, user_password))

        print('--> Successfully created S3 bucket and IAM User. Created login file "{}"'.format(login_filename))
        print('Link to bucket: {}\nIAM User name: {}\nPassword: {}'.format(bucket_link, user_name, user_password))


if __name__ == '__main__':
    print('INFO: Your AWS account should have permissions IAMFullAccess and AmazonS3FullAccess.')
    print('--> Starting AWS S3 client script...')
    main()
