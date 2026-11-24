import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request


def needed(url, method="GET"):
    r = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {}


proj = f"hw3_check_{int(time.time())}"
port = os.environ.get("TEST_PORT", "18080")
base = f"http://127.0.0.1:{port}"
backup_file = os.path.abspath(f"{proj}.tar.gz")
vol = f"{proj}_redis_data"
doc = ["docker", "compose", "-p", proj]

env = os.environ.copy()
env["APP_PORT"] = port
stage = "start"

try:
    stage = "up"
    subprocess.run(doc + ["up", "-d", "--build", "--wait"], env=env, check=True, timeout=60)

    stage = "increment"
    code, data = needed(f"{base}/")
    assert code == 200
    assert data["count"] == 0

    for _ in range(3):
        code, _ = needed(f"{base}/increment", "POST")
        assert code == 200

    code, data = needed(f"{base}/")
    assert code == 200
    assert data["count"] == 3
    host1 = data["hostname"]

    stage = "recreate app"
    subprocess.run(doc + ["up", "-d", "--force-recreate", "--no-deps", "--wait", "app"], env=env, check=True, timeout=60)
    code, data = needed(f"{base}/")
    host2 = data["hostname"]
    assert code == 200
    assert data["count"] == 3
    assert host1 != host2

    stage = "stop/start redis"
    subprocess.run(doc + ["stop", "redis"], check=True, timeout=30)
    assert needed(f"{base}/healthz")[0] == 200
    assert needed(f"{base}/readyz")[0] == 503
    assert needed(f"{base}/increment", "POST")[0] == 503

    subprocess.run(doc + ["start", "redis"], check=True, timeout=30)
    ok = False
    for _ in range(20):
        try:
            if needed(f"{base}/readyz")[0] == 200:
                ok = True
                break
        except Exception:
            pass
        time.sleep(1)
    if not ok:
        raise RuntimeError("redis did not become ready")

    code, data = needed(f"{base}/")
    assert code == 200
    assert data["count"] == 3
    assert data["hostname"] == host2

    code, data = needed(f"{base}/increment", "POST")
    assert code == 200
    assert data["count"] == 4

    stage = "backup"
    subprocess.run(doc + ["stop", "app", "redis"], check=True, timeout=30)
    subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{vol}:/data:ro",
            "-v", f"{os.getcwd()}:/backup",
            "redis:7.4-alpine",
            "tar", "-czf", f"/backup/{proj}.tar.gz", "-C", "/data", ".",
        ],
        check=True,
        timeout=30,
    )
    assert os.path.getsize(backup_file) > 0

    stage = "cleanup"
    subprocess.run(doc + ["down", "-v"], check=True, timeout=30)
    check_vol = subprocess.run(["docker", "volume", "inspect", vol], capture_output=True, timeout=15)
    assert check_vol.returncode != 0

    print("OK:", backup_file)

except Exception as e:
    print(f"Error on stage '{stage}': {e}")
    sys.exit(1)

finally:
    subprocess.run(doc + ["down", "-v"], capture_output=True, timeout=30)
