"""Real HTTP boundary checks without starting an emulator."""
import base64
from http.server import ThreadingHTTPServer
import http.client
from pathlib import Path
import sys
import threading

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/autosd_dashboard"))
from board_server import Handler


@pytest.fixture(params=[False, True], ids=["no-login", "password"])
def http_board(request):
    class App:
        token = "test-csrf"
        def state(self):
            return {"run_id": "test-run", "lifecycle": "STOPPED"}
        def start_job(self, payload):
            return {"id": "test-job", "action": payload["action"]}
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.authorization = "Basic " + base64.b64encode(b"autosd:test-password").decode() if request.param else None
    server.app = App()
    worker = threading.Thread(target=server.serve_forever)
    worker.start()
    def request(path="/api/board", headers=None, body=None, authenticated=True):
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=2)
        values = {"Authorization": server.authorization} if authenticated and server.authorization else {}
        values.update(headers or {})
        connection.request("POST" if body is not None else "GET", path, body, values)
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result
    request.login_required = server.authorization is not None
    yield request
    server.shutdown()
    worker.join()
    server.server_close()


def test_authentication_and_same_origin(http_board):
    assert http_board()[0] == 200
    status, headers, _ = http_board(authenticated=False)
    assert status == (401 if http_board.login_required else 200)
    assert ("WWW-Authenticate" in headers) == http_board.login_required
    assert http_board(headers={"Authorization": "Basic wrong"})[0] == (401 if http_board.login_required else 200)
    assert http_board(headers={"Host": "external.invalid"})[0] == 403
    assert http_board(headers={"Origin": "http://external.invalid"})[0] == 403
    assert http_board(headers={"Sec-Fetch-Site": "cross-site"})[0] == 403


def test_mutation_csrf_and_payload_limit(http_board):
    assert http_board("/api/jobs", body=b"{}")[0] == 403
    headers = {"X-CSRF-Token": "test-csrf", "Content-Type": "application/json"}
    assert http_board("/api/jobs", headers, b'{"action":"vmcu.status"}')[0] == 202
    assert http_board("/api/jobs", headers, b" " * 4097)[0] == 400
    assert http_board("/api/jobs", headers, b"bad json")[0] == 400
    assert http_board("/api/shell", headers, b"{}")[0] == 404


def test_static_csp_and_path_allowlist(http_board):
    status, headers, body = http_board("/")
    assert status == 200 and b"board.js" in body
    assert "script-src 'self'" in headers["Content-Security-Policy"]
    assert http_board("/../board_server.py")[0] == 404
    assert http_board("/board.js")[0] == 200
