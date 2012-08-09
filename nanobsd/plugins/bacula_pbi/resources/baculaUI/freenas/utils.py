from subprocess import Popen, PIPE
import os
import platform

bacula_pbi_path = "/usr/pbi/bacula-sd-" + platform.machine()
bacula_etc_path = os.path.join(bacula_pbi_path, "etc")
bacula_mnt_path = os.path.join(bacula_pbi_path, "mnt")
bacula_fcgi_pidfile = "/var/run/bacula_fcgi_server.pid"
bacula_fcgi_wwwdir = os.path.join(bacula_pbi_path, "www")
bacula_control = "/usr/local/etc/rc.d/bacula"
bacula_icon = os.path.join(bacula_pbi_path, "default.png")
bacula_oauth_file = os.path.join(bacula_pbi_path, ".oauth")


def get_rpc_url(request):
    return 'http%s://%s/plugins/json-rpc/v1/' % ('s' if request.is_secure() \
            else '', request.get_host(),)


def get_bacula_oauth_creds():
    f = open(bacula_oauth_file)
    lines = f.readlines()
    f.close()

    key = secret = None
    for l in lines:
        l = l.strip()

        if l.startswith("key"):
            pair = l.split("=")
            if len(pair) > 1:
                key = pair[1].strip()

        elif l.startswith("secret"):
            pair = l.split("=")
            if len(pair) > 1:
                secret = pair[1].strip()

    return key, secret

bacula_advanced_vars = {
    'allow': {
        "type": "textbox",
        "opt": "-a",
        },
    "blocklist": {
        "type": "checkbox",
        "on": "-b",
        "off": "-B",
        },
}
