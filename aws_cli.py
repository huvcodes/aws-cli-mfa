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
# 2. Python v3.6 or above installed
# 3. Additional python modules to install
#   a. pip install colorama
#
#
# Assumptions:
# -----------------
# This python script has been tested on Windows operating system.
# Although the script might work as-is on a non-windows platform, minor changes may be needed to get the script working.
#

import colorama, json, os, shutil, subprocess, sys
from colorama import Fore, Style
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path
from subprocess import PIPE, Popen, CalledProcessError

# Initiating the coloroma class and auto reset the color codes after every print line
colorama.init(autoreset = True)

# Setting the file and directory paths
home_dir = os.path.expanduser('~')
aws_dir = os.path.join(home_dir, '.aws')
backup_dir = os.path.join(aws_dir, 'credentials_backup')
config_file = os.path.join(aws_dir, 'config')
credentials_file = os.path.join(aws_dir, 'credentials')



# -----------------------------------------------------------------------------------------
# Block for Welcome screen print statements - Begin

print(f'{Fore.CYAN}{Style.BRIGHT}\n----------------------------------------------------------------------------------------------')
print(f'{Fore.CYAN}{Style.BRIGHT}Welcome to AWS CLI 2F authentication !\nPlease read the pre-requisites and/or assumptions before proceeding.')
print(f'{Fore.CYAN}{Style.BRIGHT}----------------------------------------------------------------------------------------------')

# Block for Welcome screen print statements - End
# -----------------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------------
# Block to check if AWS credentials and config file exists or not - Begin

if (not os.path.exists(config_file)):
    print(f"{Fore.RED}{Style.BRIGHT}\nERROR : Could not locate 'config' file under .aws directory.\nScript aborting here !\n")
    sys.exit(1)

if (not os.path.exists(credentials_file)):
    print(f"{Fore.RED}{Style.BRIGHT}\nERROR : Could not locate 'credentials' file under .aws directory.\nScript aborting here !\n")
    sys.exit(1)

# Block to check if AWS credentials and config file exists or not - End
# -----------------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------------
# Block to set AWS profile - Begin

print(f"{Fore.YELLOW}{Style.DIM}\nNOTE: Checking for AWS profile preference.")
print(f"{Fore.YELLOW}{Style.DIM}If you do not specify any profile name, the script will authenticate you with 'default' AWS profile settings specified in your credentials file.\n")
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

# Setting value for permanent profile
aws_profile_permanent = aws_profile + '_permanent' 

config = ConfigParser()
config.read({config_file})
if (not config.has_section(aws_profile)):
    print(f"{Fore.RED}{Style.BRIGHT}\nERROR : AWS profile '{aws_profile}' is not present in the config file. Script aborting here !\n")
    sys.exit(1)
else:
    # print(f"{Fore.GREEN}{Style.BRIGHT}\n'{aws_profile}' profile is present in the file [{config_file}]")
    mfa_serial_arn = config.get(aws_profile, 'mfa_serial')
    # print(f'{Fore.YELLOW}{Style.DIM}MFA Serial ARN available in config file is --> {mfa_serial_arn}')
    if (not mfa_serial_arn):
        print(f"{Fore.RED}{Style.BRIGHT}\nERROR : Profile '{aws_profile}' does not contain any mfa_serial details in the config file. Script aborting here !\n")
        sys.exit(1)


credentials = ConfigParser()
credentials.read({credentials_file})
if (not credentials.has_section(aws_profile_permanent)):
    print(f"{Fore.RED}{Style.BRIGHT}ERROR : AWS profile (permanent) '{aws_profile_permanent}' is not present in the credentials file. Script aborting here !\n")
    sys.exit(1)

if (not credentials.has_section(aws_profile)):
    print(f"{Fore.RED}{Style.BRIGHT}ERROR : AWS profile [{aws_profile}] is not present in the credentials file. Script aborting here !\n")
    sys.exit(1)

# Block to check if [profile] exists in config and credentials file - End
# -----------------------------------------------------------------------------------------
     


# -----------------------------------------------------------------------------------------
# Block to receive MFA code and allow authentication - Begin

session_time = 14400
minutes, seconds = divmod(session_time, 60)
hours, minutes = divmod(minutes, 60)
# days, hours = divmod (hours, 24)

# Reading MFA code input for new session
print(f'{Fore.YELLOW}{Style.BRIGHT}\nProvide your valid 6-digit MFA code : ', end='')
mfa_code = input()

# Check if MFA code provided is null or empty
if(not mfa_code):
    print(f'{Fore.RED}{Style.BRIGHT}\nERROR : MFA code provided is either null or empty. Script aborting here !\n')
    sys.exit(1)
else:
    # Backup the current credentials file
    try:
        if (not os.path.exists(backup_dir)):
            print(f'\nCredentials backup directory does not exist. Creating the directory now')
            # os.mkdir(os.path.join(aws_dir, 'credentials_backup'))
            os.mkdir(backup_dir)

        backup_file_name = datetime.now().strftime("credentials_backup_%Y-%m-%d_%H%M%S")
        backup_file = os.path.join(backup_dir, backup_file_name) 
        shutil.copyfile(credentials_file, backup_file)
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Credentials file backed up as '{backup_file_name}' under '[{backup_dir}]' directory")
    except OSError as e:
        print(f"{Fore.RED}{Style.BRIGHT}\nERROR: OSError --> Error Str - ", e.strerror)
        sys.exit(1)
    
    
    # Substituting temporary profile with permanent credentials to obtain CLI STS
    try:
        # print(f'\nSubstituting temporary profile with permanent credentials to obtain CLI STS')
        credentials[aws_profile]['aws_access_key_id'] = credentials.get(aws_profile_permanent, 'aws_access_key_id')
        credentials[aws_profile]['aws_secret_access_key'] = credentials.get(aws_profile_permanent, 'aws_secret_access_key')
        credentials.remove_option(aws_profile, "aws_session_token")
        with open(credentials_file, "w") as file:
            credentials.write(file)
    except IOError as err:
        print(f"{Fore.YELLOW}{Style.BRIGHT}\nWARNING: Replacing '{aws_profile}' with permanent credentails may have some issue(s). Please check !")
        print(f"{Fore.YELLOW}{Style.BRIGHT}\nWARNING: IOError --> ", e.output)
        # sys.exit(1)
    except:
        print(f"{Fore.YELLOW}{Style.BRIGHT}\nWARNING: Replacing '{aws_profile}' with permanent credentails may have some issue(s). Please check !\n")
        # sys.exit(1)


    # Firing STS command
    sts_command = f'aws sts get-session-token --profile {aws_profile} --token-code {mfa_code} --serial-number {mfa_serial_arn} --duration-seconds {session_time}'
    # print(f'\nDEBUG: STS commmand called is --> {sts_command}\n')

    try:
        sts_result = subprocess.Popen(sts_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sts_output, error = sts_result.communicate()
        if sts_output:
            # print(f'\nParsing the sts call json output.\n{sts_output}')
            try:
                sts_json = json.loads(sts_output)
                # Setting the sts-token credentials
                credentials[aws_profile]['aws_access_key_id'] = sts_json['Credentials']['AccessKeyId']
                credentials[aws_profile]['aws_secret_access_key'] = sts_json['Credentials']['SecretAccessKey']
                credentials[aws_profile]['aws_session_token'] = sts_json['Credentials']['SessionToken']
                # session_expiry = sts_json['Credentials']['Expiration']

                # Update credentials file with the sts token
                try:
                    with open(credentials_file, "w") as file:
                        credentials.write(file)
                    print(f'{Fore.GREEN}{Style.BRIGHT}\nCongratulations...!! You are now successfully 2FA authenticated with AWS CLI. !')
                    # print(f'{Fore.GREEN}{Style.BRIGHT}The session will expire at [{session_expiry}] UTC timezone!')
                    print (f'{Fore.GREEN}{Style.BRIGHT}The session will expire after {int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds')
                    print(f'{Fore.GREEN}{Style.BRIGHT}Bye...\n')
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


# Block to receive MFA code and allow authentication - End
# -----------------------------------------------------------------------------------------
