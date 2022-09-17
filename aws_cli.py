#!/usr/bin/env python3
# 
# ====================================================================================================================
# Python script for automating AWS CLI 2FA(MFA) login
# ====================================================================================================================
#
# ASSUMPTIONS & PRE-REQUISITES:
# --------------------------------------------------------
# 
# Pre-Requisites:
# -----------------
# 1. Latest version of AWS CLI installed
# 2. Python v3.x installed
# 3. Additional python modules to install
#   a. pip3 install coloroma
#
#
# Assumptions:
# -----------------
# 1. AWS Profile and Credentials files configured properly.
# 2. MFA authentication script fails if AWS CLI is not configured properly.
#

import colorama, json, os, sys, subprocess
from colorama import Fore, Style
from configparser import ConfigParser
from pathlib import Path
from subprocess import PIPE, Popen, CalledProcessError

# Initiating the coloroma class and auto reset the color codes after every print line
colorama.init(autoreset = True)

# Setting the file and directory paths
home_dir = os.path.expanduser('~')
aws_dir = os.path.join(home_dir, '.aws')
config_file = os.path.join(aws_dir, 'config')
credentials_file = os.path.join(aws_dir, 'credentials')
temp_creds_file = os.path.join(aws_dir, 'temp_creds')


# -----------------------------------------------------------------------------------------
# Block for Welcome screen print statements - Begin

print(f'{Fore.CYAN}{Style.BRIGHT}\n----------------------------------------------------------------------------------------------')
print(f'{Fore.CYAN}{Style.BRIGHT}Welcome to AWS CLI 2F authentication !\nPlease read the pre-requisites and/or assumptions before proceeding.')
print(f'{Fore.CYAN}{Style.BRIGHT}----------------------------------------------------------------------------------------------')

# Block for Welcome Console Print statements - End
# -----------------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------------
# Block to check if AWS credentials and config file exists or not - Begin

if (not os.path.exists(config_file)):
    print(f"{Fore.RED}{Style.BRIGHT}\nERROR : Could not locate 'config' file under .aws directory.\nScript aborting here !\n")
    sys.exit(1)

if (not os.path.exists(credentials_file)):
    print(f"{Fore.RED}{Style.BRIGHT}\nERROR : Could not locate 'credentials' file under .aws directory.\nScript aborting here !\n")
    sys.exit(1)

if (not os.path.exists(temp_creds_file)):
    print(f"{Fore.RED}{Style.BRIGHT}\nERROR : Could not locate 'temp_creds' file under .aws directory.\nScript aborting here !\n")
    sys.exit(1)

# Block to check if AWS credentials and config file exists or not - End
# -----------------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------------
# Block to set AWS profile - Begin

print(f"{Fore.YELLOW}{Style.DIM}\nNOTE: Checking for AWS profile preference.\nIf you do not specify any profile name, the script will authenticate you with 'default' AWS profile settings specified in your credentials file.\n")
print(f'Specify your AWS profile name : ', end = '')
aws_profile = input()

if(not aws_profile):
    print(f"{Fore.GREEN}{Style.BRIGHT}\nINFO: AWS profile name not provided. Continuing with 'default' profile settings.")
    aws_profile = 'default'
# else:
    # print(f'Profile name provided is - [{aws_profile}]\n')

# Block to set AWS profile - End
# -----------------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------------
# Block to check if [profile] exists in config and credentials file - Begin

config = ConfigParser()
config.read({config_file})
if (not config.has_section(aws_profile)):
    print(f"\n{Fore.RED}{Style.BRIGHT}ERROR : AWS profile '{aws_profile}' is not present in the config file. Script aborting here !\n")
    sys.exit(1)
# else:
#    print(f"{Fore.GREEN}{Style.BRIGHT}\n'{aws_profile}' profile is present in the file [{config_file}]")


credentials = ConfigParser()
credentials.read({credentials_file})
if (not credentials.has_section(aws_profile)):
    print(f"{Fore.RED}{Style.BRIGHT}ERROR : AWS profile '{aws_profile}' is not present in the credentials file. Script aborting here !\n")
    sys.exit(1)
else:
    # print(f"{Fore.GREEN}{Style.BRIGHT}'{aws_profile}' profile is present in the file [{credentials_file}]")
    # mfa_serial_arn = credentials[aws_profile]['mfa_serial']
    mfa_serial_arn = credentials.get(aws_profile, 'mfa_serial')
    print(f'{Fore.YELLOW}{Style.DIM}MFA Serial ARN available in credentials file is --> {mfa_serial_arn}')

temp_credentials = ConfigParser()
temp_credentials.read({temp_creds_file})

# Block to check if [profile] exists in config and credentials file - End
# -----------------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------------
# Block to check if any existing STS session exists with specified AWS profile - Begin

print(f'{Fore.YELLOW}{Style.DIM}\nChecking if any existing STS session exists with specified AWS profile')

# aws sts get-caller-identity call to verify caller identity
sts_caller_identity_cmd = f'aws sts get-caller-identity --profile {aws_profile} --output json'

try:
    sts_caller_identity_result = subprocess.Popen(sts_caller_identity_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sts_caller_identity_output, error = sts_caller_identity_result.communicate()

    if sts_caller_identity_output:
        print(f'\n-----------------------------------------------')
        print(f'{Fore.GREEN}{Style.DIM}CLI tool identified an existing AWS session for the profile [{aws_profile}]')
        try:
            sts_caller_identity_json = json.loads(sts_caller_identity_output)
            connected_account = sts_caller_identity_json['Account']
            connected_arn = sts_caller_identity_json['Arn']
        except json.decoder.JSONDecodeError:
            print(f'{Fore.RED}{Style.BRIGHT} ERROR: Error parsing the json output of sts get-caller-identity call')
            sys.exit(1)

        print(f'Connected to Account : {connected_account}')
        print(f'Connected as : {connected_arn}')
        print(f'-----------------------------------------------\n')
    
    if error:
        print(f'{Fore.RED}{Style.BRIGHT}\nERROR: Msg --> ', error.strip())
        sys.exit(1)

except CalledProcessError as e:
    print(f'{Fore.RED}{Style.BRIGHT}\nERROR: CalledError --> ', e.output)
            
# Block to check if any existing STS session exists with specified AWS profile - End
# -----------------------------------------------------------------------------------------




# -----------------------------------------------------------------------------------------
# Block to check if user wants to continue in same session or wants a new session - Begin

# print(f"{Fore.BLUE}{Style.BRIGHT}Specify your AWS profile name : ", end='')
print(f'\nDo you want to continue in the existing session or do you want to create a new AWS CLI session ?')
print(f"\nPress [Y] or [y] to continue OR [N] or [n] to create a new session : ", end = '')
continueFlag = input()

if (continueFlag =='Y' or continueFlag =='y'):
    print(f'\nThanks for confirming, you can continue using AWS CLI in the existing session.\nScript will abort its execution now.!')
    sys.exit()
elif (continueFlag =='N' or continueFlag =='n'):
    # Reading MFA token input for new session
    print(f'{Fore.BLUE}{Style.BRIGHT}\nProvide your valid 6-digit MFA token : ', end='')
    mfa_token = input()

    # Check if MFA token provided is null or empty
    if(not mfa_token):
        print(f'{Fore.RED}{Style.BRIGHT}\nERROR : MFA token provided is either null or empty. Script aborting here !\n')
        sys.exit(1)
    else:
        sts_command = f'aws sts get-session-token --profile {aws_profile} --token-code {mfa_token} --serial-number {mfa_serial_arn} --duration-seconds 900'
        # print(f'\nDEBUG: STS commmand called is --> {sts_command}\n')

        try:
            sts_result = subprocess.Popen(sts_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sts_output, error = sts_result.communicate()
            if sts_output:
                # print(f'\nParsing the sts call json output.\n{sts_output}')
                try:
                    sts_json = json.loads(sts_output)
                    # Setting the sts-token credentials
                    temp_credentials['temporary']['aws_access_key_id'] = sts_json['Credentials']['AccessKeyId']
                    temp_credentials['temporary']['aws_secret_access_key'] = sts_json['Credentials']['SecretAccessKey']
                    temp_credentials['temporary']['aws_session_token'] = sts_json['Credentials']['SessionToken']

                    # Update credentials file with the sts token
                    try:
                        with open(temp_creds_file, "w") as file:
                            temp_credentials.write(file)
                        print(f"{Fore.GREEN}{Style.BRIGHT}\nCongratulations...!! You are now successfully 2FA authenticated with AWS CLI. Well done... !\n")
                    except:
                        print(f"{Fore.RED}{Style.BRIGHT}\nError detected while updating credentials file with the sts token. Please check !\n")
                        sys.exit(1)

                except json.decoder.JSONDecodeError:
                    print(f'{Fore.RED}{Style.BRIGHT} ERROR: Error parsing the json output of sts get-session-token call')
                    sys.exit(1)
            
            if error:
                # print(f"{Fore.RED}{Style.BRIGHT}\nERROR: Return Code --> ", sts_result.returncode)
                print(f"{Fore.RED}{Style.BRIGHT}\nERROR: Msg --> ", error.strip())
                sys.exit(1)
        
        except CalledProcessError as e:
            # print(f"{Fore.RED}{Style.BRIGHT}\nERROR: CalledError --> ", e.returncode)
            print(f"{Fore.RED}{Style.BRIGHT}\nERROR: CalledError --> ", e.output)
        except OSError as e:
            # print(f"{Fore.RED}{Style.BRIGHT}\nERROR: OSError --> Error Number - ", e.errno)
            print(f"{Fore.RED}{Style.BRIGHT}\nERROR: OSError --> Error Str - ", e.strerror)
        except:
            print(f"{Fore.RED}{Style.BRIGHT}\nERROR: --> Unhandled exception :: ", sys.exc_info()[0])

else:
    print(f'\n{Fore.RED}{Style.BRIGHT}Invalid response received. Script aborting now. Bye\n')
    sys.exit()

            
# Block to check if user wants to continue in same session or wants a new session  - End
# -----------------------------------------------------------------------------------------
