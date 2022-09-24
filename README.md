# aws-cli-mfa
Python script to ease (automate) the process of 2FA(MFA) authenticated session for AWS CLI. The utility script is implemented as per instructions in this [official AWS blog](https://aws.amazon.com/premiumsupport/knowledge-center/authenticate-mfa-cli).


### Pre-requisites
  1. Latest version of AWS CLI tools installed - https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
  2. Python v3.6 or above installed
  3. Additional python modules to install
     - `pip install colorama`


### Assumptions
This python script has been tested on Windows operating system. Although the script might work as-is on a non-windows platform, minor changes may be needed to get the script working.


## Structuring your config file
  - ```config``` file should be stored under ```.aws``` directory ```(C:\Users\<your_home_directory>\.aws)```
  - ```config``` file should contain the mfa serial arn.
  - Sample ```config``` file
    ```ini
    # Default pointing to Dev Account
    [default]
    region = ap-southeast-2
    output = json
    mfa_serial = arn:aws:iam::xxxxxxxxxxxx:mfa/aaaaaaaaaaaa

    # Dev account profile
    [dev]
    region = ap-southeast-2
    output = json
    mfa_serial = arn:aws:iam::xxxxxxxxxxxx:mfa/aaaaaaaaaaaa

    # Test account profile
    [acc_test]
    region = us-east-1
    output = json
    mfa_serial = arn:aws:iam::xxxxxxxxxxxx:mfa/cccccccccccc

    # Prod account profile
    [prod_account]
    region = eu-west-2
    output = json
    mfa_serial = arn:aws:iam::xxxxxxxxxxxx:mfa/pppppppppppp
    ```


## Structuring your credentials file
  - ```credentials``` file should be stored under ```.aws``` directory ```(C:\Users\<your_home_directory>\.aws)```
  - Each profile in the ```credentials``` file should have two sections.
    - **_profile-name_permanent_** section where you will save your api/cli keys (aws_access_key_id and aws_secret_access_key) as permanent credentials
    - **_profile-name_** which will have empty values. The script will overwrite this section with the STS token obtained after 2FA process.
  - Sample ```credentials``` file
    ```ini
    [default_permanent]
    aws_access_key_id = XXXXXXXXXXXXXXXXXXXX
    aws_secret_access_key = ***********************************

    [default]
    aws_access_key_id = 
    aws_secret_access_key = 
    aws_session_token = 

    [dev_permanent]
    aws_access_key_id = YYYYYYYYYYYYYYYYYYYY
    aws_secret_access_key = ***********************************

    [dev]
    aws_access_key_id = 
    aws_secret_access_key = 
    aws_session_token = 

    [acc_test_permanent]
    aws_access_key_id = BBBBBBBBBBBBBBBBBBBB
    aws_secret_access_key = ***********************************

    [acc_test]
    aws_access_key_id = 
    aws_secret_access_key = 
    aws_session_token = 

    [prod_account_permanent]
    aws_access_key_id = AAAAAAAAAAAAAAAAAAAA
    aws_secret_access_key = ***********************************

    [prod_account]
    aws_access_key_id = 
    aws_secret_access_key = 
    aws_session_token = 
    ```


## Working of the script

#### Preparation
  - Download and save the script in any location of your choice.
    - For ease of use, save it under ```.aws``` directory where your config and credentials files are also available.
  - ```config``` file under ```.aws``` directory is configured as illustrated [in this section](#structuring-your-config-file).
  - ```credentials``` file under ```.aws``` directory is configured as illustrated [in this section](#structuring-your-credentials-file).

#### Running the script
01. Run the script using command,
    ```python .\aws_cli.py``` (for Windows OS)
    ```./awscli.py``` (for non-Windows OS)  
02. If required files (```config```, ```credentials```) are not available under ```.aws``` directory, script will fail with errors.
      
    ![Config and Credentials files missing](https://github.com/huvcodes/images-ss/blob/main/aws-cli-mfa/file_missing_errors.png)
03. If required files are available, you will see the welcome message and prompt to provide the profile name.
      
    ![Welcome message](https://github.com/huvcodes/images-ss/blob/main/aws-cli-mfa/welcome_screen.png)
04. Specify the profile name which you want to connect to. If you press enter without specifying any value, it will authenticate you with "default" settings as per your config and credentials files.
    - If you provide invalid profile name, the script will fail with an error.
        
      ![Invalid Profile Name](https://github.com/huvcodes/images-ss/blob/main/aws-cli-mfa/invalid_profile_name.png)
    - If profile name and configuration is correct, the script will prompt you to provide 2FA(MFA) code.
        
      ![Valid Profile Name](https://github.com/huvcodes/images-ss/blob/main/aws-cli-mfa/valid_profile_name.png)
05. Enter the 2FA(MFA) code
    - For valid 2FA(MFA) code, you will be successfully authenticated with AWS CLI.
      ![Successful Authentication](https://github.com/huvcodes/images-ss/blob/main/aws-cli-mfa/successfuk_authentication.png)
    - Profile section in ```credentials``` file will be updated with the AWS STS token
      ```ini
      [dev]
      aws_access_key_id = A1B2C3D4E5F6G7H8I9J0
      aws_secret_access_key = <random generated key>
      aws_session_token = <random generated token>
      ```
        
      ![STS Token](https://github.com/huvcodes/images-ss/blob/main/aws-cli-mfa/sts_token.png)
    - A copy of the credentials file will be backed up under ```C:\Users\<your_home_directory>\.aws\credentials_backup``` directory
      - You may delete these backup files only keeping the last few (or recent copies) for your reference.
        
      ![Credentials Backup](https://github.com/huvcodes/images-ss/blob/main/aws-cli-mfa/credentials_backup.png)
06. Run few AWS CLI commands to test your 2FA authentication.
07. After your AWS CLI session is expired, repeat steps 1-6.


#### Session Expiration
The session is currently set to expire after 14400 seconds (4 hours). You can change the value according to your needs.

```ini
session_time = 14400
```


