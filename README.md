# SimpleGXWEBHOOK

Simple and Dumb [Grafana webhook](https://grafana.com/docs/grafana/next/alerting/old-alerting/notifications/#webhook) with [aiohttp](https://docs.aiohttp.org/en/stable/) for XMPP with [Slixmpp](https://slixmpp.readthedocs.io/en/latest/)

# TODO

- Test: Reconnect
- Test: Presence bug
- Support OMEMO
- Gunicorns threads
- Json validation ? (No doc about which fields can be null...)

# Launch :

grafana-webhook.py -h for help

Theses variables can be environment variables :

- JID
- PASSWORD
- RECIPIENT
- PORT
- BINDADDRESS

# Install with Ansible (example):

```
ANSIBLE_NOCOWS=1 ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook \
-i '192.168.178.79,' \
-u myuser \
--ask-become-pass --ask-pass \
--become-method="sudo" \
-e 'ansible_python_interpreter=/usr/bin/python3' \
provisioning/install.yml
```
