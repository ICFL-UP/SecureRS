# SecureRS
Secure Readiness Storage - A model prototype that will securely verify, encrypt and store Potential Digital Evidence.

## About
This tool was designed for research in the field of Digital Forensics.

This prototype solution was created with Digital Forensic Readiness processes for secure storage and retrieval or potential digital evidence. This solution is generic and can be used for any application that requires secure storage. There is also an API built in that allows integration with any system or tool. From the admin panel you can create and manage API keys and routes.

For more details with a step by step guide please consult the  [`UserManual.pdf`](https://github.com/AvinashSingh786/SecureRS/raw/master/UserManual.pdf).  
## Docker
If you are familiar with docker this is the fastest way to get SecureRS up and running.
Simply run:
```bash
docker build . --tag "securers"
docker run -d --name securers -p 8443:8443 --mount source=${pwd},destination=/SecureRS securers

```

## Installation


This tool can be run from a docker container that can be built using the dockerfile. Alternatively, you can clone this repository and install the python requirements. This tool only works for Python3 and was tested with Python3.7. It is recommended you run this in a virtual environment to further ensure compatibility and added security. 

```bash
git clone git@github.com:AvinashSingh786/SecureRS.git
cd SecureRS
python3 -m pip install --user virtualenv
sudo apt-get install python3-venv python3-magic # for Linux
python3 -m venv venv
source venv/bin/activate # for Linux
.\venv\Scripts\activate # for Windows
pip3 install python-magic-bin # for Windows
(venv)$ pip install -r requirements.txt 

```

## Usage
Run the following commands to configure and run the engine.

```bash
(venv)$ python manage.py makemigrations pde  # This sets up the storage engine and databases
(venv)$ python manage.py migrate          # This creates the databases and interfaces
(venv)$ python manage.py createsuperuser  # Create a super user that you will use as the admin
(venv)$ python manage.py runsslserver 0.0.0.0:8000  
``` 

## Features
- OTP Login + Download (TOTP, YubiKey)
- REST API for Ingestion
- Two Factor Auth
- Secure Cookies
- Integrity Verification
- Encrypted Storage
- Security Headers
- Email Config
- Session Security 
- Customizable 
#
# IMPORTANT!
If you plan on using this tool in production please change the following in the settings.py file:
- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS 
- COMPANY_NAME 
- DEFF_PASSWORD 
- DEFF_SALT 
- SESSION_SECURITY_EXPIRE_AFTER 
- SESSION_SECURITY_WARN_AFTER 
- EMAIL_USE_TLS 
- EMAIL_HOST 
- EMAIL_PORT
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD
 
## Screenshots
Below are screenshots of the tool.
<img src="https://github.com/AvinashSingh786/SecureRS/blob/master/screenshots/Screenshot%202021-07-12%20160738.png?raw=true" />
<img src="https://github.com/AvinashSingh786/SecureRS/blob/master/screenshots/Screenshot%202021-07-12%20164401.png?raw=true" />
<img src="https://github.com/AvinashSingh786/SecureRS/blob/master/screenshots/Screenshot%202021-07-12%20164418.png?raw=true" />
<img src="https://github.com/AvinashSingh786/SecureRS/blob/master/screenshots/Screenshot%202021-07-12%20164456.png?raw=true" />
 
## Testing environments
  - Windows 10
  - Windows 8.1
  - Windows 7
  - Windows XP

## Contributing
 
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Wanted
 
  - Bug reports.
  - Feedback.


## License
 
MIT License

## Publications
- Singh, A., Ikuesan, R.A. and Venter, H. (2022) ‘Secure storage model for digital forensic readiness’, IEEE Access, 10, pp. 19469–19480. doi:10.1109/access.2022.3151403. 

## Update log
- V1 (13/07/2021) 
  - Initial Release
- V2 (06/07/2023)
  - Now make use of Django 4
  - Upgraded encryption to use AES for speed
  - Handles larger files
  - Uses a custom fileupload handler for hashing before being touched by Django handlers
  - Bug fixes and UI improvements
  - Due to encryption changes, this version is no longer compatible with previous releases