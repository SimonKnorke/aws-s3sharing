
# AWS S3 file sharing

This repository should help you creating an environment to share files with your client via Amazon S3.

### Prerequisites

What things you need:

- AWS User account with sufficient permissions. Whether being added to IAM group `S3ShareGroup` or you have permissions `S3FullAccess` and `IAMFullAccess` anyway (Administrator).

- aws cli profile or your aws credentials ready.

> Best practice would be to configure your aws profile with the aws-cli (command line interface), so you won't have to enter your credentials as an input later.
> `aws configure --profile <your-profile-name>`  
Read [this](https://docs.aws.amazon.com/cli/latest/userguide/cli-multiple-profiles.html) for more information.


### Installing

Just get your Python env ready .  
`$ pipenv install ` 

`$ pipenv shell` 

And execute the main script .  
```
python main.py
```

### How the script works
At first the script will request some input information from the User and checks the permissions. 
1) Region for your S3 bucket (eu-central-1 is default) .  
2) Aws profile (optional) or Aws credentials. If you skip the profile option you have to enter your credentials (`Access Key ID`, `Secret Access Key`).   
3) Bucket name: Here enter the name of the new bucket you want to use for data sharing with a client. In case you already created a bucket that you want to use, type its name and pass the warning with "y".   
4) User name: This is the IAM user account for your client, e.g. "DB-demo-client".   
5) User password: Set the password according to the printed policy, if there exists one.  
6) Continue?: Last confirmation by the User before the AWS resources are actually created:  
-   S3 bucket (unless you specify existing one)   
- IAM User (initially without any permissions)  
- User profile (user password)  
- User policy (with allowed actions to put, get and delete objects)   

Done! Bucket link and user login information will be printed and also stored in a file `<user-name>.txt`, ready to be sent out to the client.



## Authors

* **Simon Wohlfahrt** 




