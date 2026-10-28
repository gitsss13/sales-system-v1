
from app import app


def test_home_page():
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200


def test_add_sale():
    with app.test_client() as client:
        response = client.post("/api/sales", json={
            "product": "Notebook",
            "price": 50,
            "quantity": 2
        })

        assert response.status_code == 201
        assert response.json["sale"]["total"] == 100


def test_view_sales():
    with app.test_client() as client:
        response = client.get("/api/sales")
        assert response.status_code == 200


def test_revenue():
    with app.test_client() as client:
        response = client.get("/api/summary")
        assert response.status_code == 200
        assert "total_revenue" in response.json
