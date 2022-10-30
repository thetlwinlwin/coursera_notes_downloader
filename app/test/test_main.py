from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path

client = TestClient(app)
TEST_FOLDER_PATH = Path.cwd().joinpath(__file__).parent

TEST_INPUT_TEXT_NAME = "test.txt"
TEST_OUTPUT_TEXT_NAME = "result.txt"


def test_index():
    response = client.get("/")
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.status_code == 200


def test_with_one_input_left():
    payloads = [{"note_source": "random"}, {"output_name": "hi.txt"}]
    for payload in payloads:
        response = client.request("POST", "/get_form", data=payload)
        assert response.status_code == 406
        assert response.headers["content-type"] == "text/html; charset=utf-8"


def test_with_invalid_source():
    payload = {"note_source": "random", "output_name": "hi.txt"}
    response = client.post("/get_form", data=payload)
    assert response.status_code == 406
    assert response.headers["content-type"] == "text/html; charset=utf-8"


def test_with_vaild():
    file = open(TEST_FOLDER_PATH.joinpath(TEST_INPUT_TEXT_NAME))
    payload = {
        "note_source": file.read(),
        "output_name": TEST_OUTPUT_TEXT_NAME,
    }
    file.close()

    response = client.post("/get_form", data=payload, allow_redirects=True)

    to_delete = Path.cwd().joinpath(TEST_OUTPUT_TEXT_NAME)
    if to_delete.exists:
        to_delete.unlink()

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.url == "http://testserver/result/result.txt"
