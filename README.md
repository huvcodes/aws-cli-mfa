# aws-cli-mfa
Python script to ease (automate) the process of 2FA(MFA) authenticated session for AWS CLI. The utility script is implemented as per the guidance in this [official AWS blog](https://aws.amazon.com/premiumsupport/knowledge-center/authenticate-mfa-cli).


### Pre-requisites
  1. Latest version of AWS CLI tools installed - https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
  2. Python v3.x or above installed
  3. Additional python modules to install
     - `pip install coloroma` (if using Linux or Mac OS)
     - `pip3 install coloroma` (if using Windows OS)


### Assumptions
  1. AWS Profile and Credentials configured properly
  2. MFA authentication script fails if AWS CLI is not configured properly


## How does the script work?



## How to run the script?

#### Preparation
  - Download and save the script in any location of your choice.
    - For ease of use, save it under .aws directory where your config and credentials files are also available.
  - ```config``` file under .aws directory is configured as illustrated in the section below.
  - ```credentials``` file under .aws directory is configured as illustrated in the section below.
  - ```temp_credentials``` file under .aws directory is configured as illustrated in the section below.

#### Running the script
  - Run the script using the command,
    - ```python aws_cli.py``` (for Windows OS)
    - ```awscli.py``` (for Linux and Mac OS)
  - You will see the welcome message and prompt to provide the profile name.<img src="/images/welcome_screen.jpg">
  - Provide the profile name 

## Sample config and credentials file
### config file
### credentials file
 - a. pip3 install coloroma (or pip install coloroma)