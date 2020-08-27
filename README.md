# Grafana to Mattermost API

## TL;DR

* Install virtualenv
  * apt-get install python3-venv
  * python3 -m venv flask
  * source flask/bin/activate
  * pip install -r requirements.txt
* copy config.py.example to config.py and modify to your liking.
* run `FLASK_APP=app FLASK_ENV=development flask run --host=0.0.0.0` terminal/screen/tmux and look at your debug output
* ...
* profit!(?)

## Installation for "production"

* Install Gunicorn
* Modify systemd/gunicorn.service and copy it to /etc/systemd/system/gunicorn.service
* copy systemd/gunicorn.socket to /etc/systemd/system/gunicorn.socket
* Modify systemd/gunicorn.conf and copy it to /etc/tmpfiles.d/gunicorn.conf and run `systemd-tmpfiles --create`
* Run `systemctl daemon-reload` and `systemctl enable gunicorn.service` and `systemctl start gunicorn` to get it running.
* Create a nginx config

Nginx config, I use /transformer, feel free to change it to / if it's in your root.

```nginx
    location /transformer {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Host $http_host;
      # we don't want nginx trying to do something clever with
      # redirects, we set the Host: header above already.
      proxy_redirect off;
      proxy_pass http://unix:/run/gunicorn/api-transformer.socket:/;
    }

```
