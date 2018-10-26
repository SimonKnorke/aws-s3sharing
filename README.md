
# AWS S3 file sharing

This repository will help you to create an environment for file sharing with your client via Amazon S3.

### Prerequisites

What things you need:

- AWS User account with sufficient permissions. Whether being added to IAM group `S3ShareGroup` or you have permissions anyway (e.g. as an Administrator). The exact permissions are further below.

- named aws profile stored in the config and credentials files or your aws credentials within range.

> Best practice would be to configure your aws profile in the aws-cli (command line interface), so you won't have to enter your credentials as an input later.
> `aws configure --profile <your-profile-name>`  
Read [this](https://docs.aws.amazon.com/cli/latest/userguide/cli-multiple-profiles.html) for more information on how to create a profile.


### Run the script

Get your Python env ready
```
$ pipenv install
$ pipenv shell
```

And run the main script  
```
python main.py
```

### How does the script work?

The first step of the script is to get input information from the User and to check all required permissions.  
In the second part it actually creates the AWS resources.

##### First part: User input
1) Region for your S3 bucket (eu-central-1 is default) .  
2) Aws profile (optional) or Aws credentials. If you skip the profile option you have to enter your credentials (`Access Key ID`, `Secret Access Key`).   
3) Bucket name: Here enter the name of the new bucket you want to use for data sharing with a client. In case you already created a bucket that you want to use, type its name and pass the warning with "y".   
4) User name: This is the IAM user account for your client, e.g. "DB-demo-client".   
5) User password: Set the password according to the printed policy, if there exists one.  
6) Continue?: Last confirmation by the User before the AWS resources are actually created.

##### Second part: Create AWS resources 
-   S3 bucket (unless you specified an existing one)   
- IAM User (initially without any permissions)  
- User profile (user password)  
- Put User policy (with allowed actions to put, get and delete objects)   

Done! Bucket link and user login information will be printed and also stored as a file `<user-name>.txt`, ready to be sent out to the client.

### What kind of permissions do you need?
To successfully execute the script you need the following permissions on AWS resources:

##### IAM:       
- CreateUser
- ListUsers
- GetAccountPasswordPolicy
- CreateLoginProfile
- PutUserPolicy

##### S3:            
- CreateBucket
- ListAllMyBuckets

These permissions should be bundled in an IAM group that can then be attached to the corresponding User names.
The policy in json-format looks like this:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "iam:CreateUser"
            ],
            "Resource": [
                "arn:aws:s3:::*",
                "arn:aws:iam::*:user/*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "iam:GetAccountPasswordPolicy",
                "s3:ListAllMyBuckets",
                "iam:ListUsers"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": "iam:CreateLoginProfile",
            "Resource": "arn:aws:iam::*:user/*"
        },
        {
            "Sid": "VisualEditor3",
            "Effect": "Allow",
            "Action": "iam:PutUserPolicy",
            "Resource": "arn:aws:iam::*:user/*"
        }
    ]
}
```

### What is the client allowed to do?

The permission policy of the created client user looks as follows:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::<client-folder>"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::<client-folder>/*"
        }
    ]
}
```

Consequently the client is only allowed to see the <client-folder> and to put, get or delete the objects in <client-folder>.

## Authors

* **Simon Wohlfahrt** 




