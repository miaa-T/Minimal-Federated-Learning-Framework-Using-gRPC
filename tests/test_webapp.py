from src.webapp import app


def test_web_interface_page():
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
        assert b"Federated Arithmetic Demonstration" in response.data


def test_web_interface_runs_expression():
    with app.test_client() as client:
        response = client.post(
            "/run",
            data={"expression": "(12 * 5) + (30 / 6) - (8 * 4) + (15 + 7)"},
        )
        assert response.status_code == 200
        assert b"Experiment status: COMPLETED" in response.data
        assert b"Global result" in response.data
        assert b"55.0" in response.data


def test_web_interface_rejects_empty_expression():
    with app.test_client() as client:
        response = client.post("/run", data={"expression": " "})
        assert response.status_code == 200
        assert b"Please enter an arithmetic expression." in response.data
