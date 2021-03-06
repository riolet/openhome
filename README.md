# OpenHome

...



## Getting Started

These instructions are for running a development version locally.

Download the project
```bash
cd ~/projects
git clone https://github.com/riolet/openhome/
cd openhome
```

Setup python and database (postgres in this case)
```bash
sudo apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib

sudo su - postgres
psql

CREATE DATABASE openhomedb;
CREATE USER my_user_name WITH PASSWORD 'my_password'; 
ALTER ROLE my_user_name SET client_encoding TO 'utf8';
ALTER ROLE my_user_name SET default_transaction_isolation TO 'read committed';
ALTER ROLE my_user_name SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE openhomedb TO my_user_name;
\q

exit
```

Configure local project settings, by making file: openhome/openhome/local_settings.py and filling it with the text below.

Port number defaults to 5432 and is found in /etc/postgresql/&lt;version&gt;/main/postgresql.conf

Database, user, and password values must match the previous step.
```python
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'abc123secret_key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'openhomedb',
        'USER': 'my_user_name',
        'PASSWORD': 'my_password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```


_[Optional]_ Create virtual environment for python
```bash
# working dir: ~/projects/openhome

python3 -m venv env
source env/bin/activate
```

Install required packages:
```bash
# working dir: ~/projects/openhome

pip3 install -r requirements.txt
```

Finish setting up the database
```bash
# working dir: ~/projects/openhome
python3 manage.py makemigrations
python3 manage.py migrate
```

Make administrative account for website
```bash
python manage.py createsuperuser
# supply name, email, password
```

Loading some test data
```bash
python3 manage.py loaddata property/fixtures/dev_fixture.json
```

Launch development webserver
```bash
python3 manage.py runserver 
```

Navigate to website in browser at [http://localhost:8000](http://localhost:8000)

## Run with SSL

install stunnel
```bash
sudo apt install stunnel4
```

make a folder in your project
```bash
cd ~/projects/openhome
mkdir stunnel
cd stunnel
```

make some security keys
```bash
openssl genrsa 1024 > stunnel.key
openssl req -new -x509 -nodes -sha1 -days 365 -key stunnel.key > stunnel.cert
cat stunnel.key stunnel.cert > stunnel.pem
```

Make a file called `dev_https` containing:
```
pid=

cert = stunnel/stunnel.pem
sslVersion = TLSv1.2
foreground = yes
output = stunnel.log

[https]
accept=8000
connect=8001
TIMEOUTclose=1
```

Navigate to your project folder (with manage.py) and make a script called `runhttps` as follows:
```bash
stunnel4 stunnel/dev_https &
HTTPS=1 python manage.py runserver 8001
```

Make the script runnable and run it
```bash
chmod a+x runhttps
```











