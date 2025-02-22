import atexit
import json
import os
import platform
import shutil
import stat
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path
from threading import Timer

import requests
pAddress = ''
def _get_command():
    system = platform.system()
    if system == "Darwin":
        command = "ngrok"
    elif system == "Windows":
        command = "ngrok.exe"
    elif system == "Linux":
        command = "ngrok"
    else:
        raise Exception("{system} is not supported".format(system=system))
    return command


def _check_ngrok_available():
    cmd = "where" if platform.system() == "Windows" else "which"
    try:
        res = subprocess.call([cmd, "ngrok"])
        return False if res else True  # subprocess will return 1 if not found otherwise 0
    except:
        print("Try installing ngrok")
        return False


def _run_ngrok(port, auth_token):
    command = _get_command()
    if not _check_ngrok_available():
        ngrok_path = str(Path(tempfile.gettempdir(), "ngrok"))
        _download_ngrok(ngrok_path)
        executable = str(Path(ngrok_path, command))
        os.chmod(executable, stat.S_IEXEC)  # Make file executable for the current user.
    else:
        executable = "ngrok"

    if auth_token:
        os.system(f"{executable} authtoken {auth_token}")

    ngrok = subprocess.Popen([executable, "http", str(port)])
    atexit.register(ngrok.terminate)
    localhost_url = "http://localhost:4040/api/tunnels"  # Url with tunnel details
    time.sleep(1)
    tunnel_url = requests.get(localhost_url).text  # Get the tunnel information
    j = json.loads(tunnel_url)

    tunnel_url = j["tunnels"][0]["public_url"]  # Do the parsing of the get
    tunnel_url = tunnel_url.replace("https", "http")
    return tunnel_url


def _download_ngrok(ngrok_path):
    if Path(ngrok_path).exists():
        return
    system = platform.system()
    if system == "Darwin":
        url = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip"
    elif system == "Windows":
        url = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip"
    elif system == "Linux":
        url = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip"
    else:
        raise Exception(f"{system} is not supported")
    download_path = _download_file(url)
    with zipfile.ZipFile(download_path, "r") as zip_ref:
        zip_ref.extractall(ngrok_path)


def _download_file(url):
    local_filename = url.split("/")[-1]
    r = requests.get(url, stream=True)
    download_path = str(Path(tempfile.gettempdir(), local_filename))
    with open(download_path, "wb") as f:
        shutil.copyfileobj(r.raw, f)
    return download_path


def start_ngrok(port, auth_token):
    global pAddress
    ngrok_address = _run_ngrok(port, auth_token)
    pAddress = ngrok_address
    print('updating')
    print(f" * Running on {ngrok_address}")
    print(f" * Traffic stats available on http://127.0.0.1:4040")
    return ngrok_address

def getPA():
    global pAddress
    return pAddress

def run_with_ngrok(app, auth_token=None):
    """
    The provided Flask app will be securely exposed to the public internet via ngrok when run,
    and the its ngrok address will be printed to stdout
    :param app: a Flask application object
    :return: None
    """
    old_run = app.run

    def new_run(*args, **kwargs):
        port = kwargs.get("port", 5000)
        thread = Timer(1, start_ngrok, args=(port, auth_token))
        thread.setDaemon(True)
        thread.start()
        old_run(*args, **kwargs)

    app.run = new_run


if __name__ == "__main__":
    print(_check_ngrok_available())
