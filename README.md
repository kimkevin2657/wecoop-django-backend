# WECOOP-DJANGO [![](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![](https://img.shields.io/badge/django-v4.0-green.svg)](https://www.python.org/downloads/)  

## Root Directory Structure
```
├── .cloudformation      # infra structure
├── .github              # github action
├── backend              # django project
└── nginx                # nginx config
```


## Backend Directory Structure
```
└── backend
    ├── api              # django api directory
    ├── app              # django app directory
    ├── config           # django project config directory
    └── templates        # django template directory
```


## Dependency
- [패키지](./backend/requirements.txt)


## Settings AWS Profile
vi ~/.aws/config
```
...
[profile {profile_name}]
aws_access_key_id=**
aws_secret_access_key=**
region = ap-northeast-2
```


## Install Virtual Environment & Dependency
```bash
# ./backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Set Environments
```
AWS_DEFAULT_PROFILE={profile_name}
DJANGO_SETTINGS_MODULE=config.settings.local
```


## RunServer
```bash
python manage.py runserver 0:8000
```



## API Document
- https://api.wecoop.link/swagger


# CICD Pipeline
![CICD](./.github/CICD.jpeg)
