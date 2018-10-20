
# AWS helpers

One Paragraph of project description goes here

### Prerequisites

What things you need:


- AWS account with permissions `S3FullAccess` and `IAMFullAccess`.
> This is important since you want to create a new S3 bucket and an IAM user that has the appropriate permissions.
- aws cli profile or aws credentials ready
> Best practice would be to configure your aws profile with the aws-cli (command line interface). Read [this](https://docs.aws.amazon.com/cli/latest/userguide/cli-multiple-profiles.html) for more information.
> `aws configure --profile "your-profile-name"`


### Installing

Get your Python env ready

```
$ pipenv install
``` 

### Creating S3 bucket link + user with read/write only

Execute the script `aws_S3_client_script.py`

```
python aws_S3_client_script.py
```
Follow the instructions and enter the required information:
```
1) Region for your S3 bucket (eu-central-1 is default)
2) Aws profile (optional) or Aws credentials
3) Bucket name
4) User name
5) User password
Continue?: Enter "y" for yes
Done.
```
The script will also create a `user-name.txt` file to store the login information that you have to send to the client.

## Authors

* **Simon Wohlfahrt** 




