
from datetime import date


def create_test_data(client):
    supplier_response = client.post(
        "/suppliers/",
        json={"company_name": "Dashboard Test Supplier"}
    )
    assert supplier_response.status_code == 201
    supplier_id = supplier_response.json()["id"]

    buyer_response = client.post(
        "/buyers/",
        json={"company_name": "Dashboard Test Buyer"}
    )
    assert buyer_response.status_code == 201

    product_response = client.post(
        "/products/",
        json={"product_name": "Dashboard Test Bitumen"}
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    rates = [
        ("2026-11-20", 48500),
        ("2026-11-21", 50000),
        ("2026-11-22", 51000),
    ]

    for effective_date, rate in rates:
        response = client.post(
            "/supplier-rates/",
            json={
                "supplier_id": supplier_id,
                "product_id": product_id,
                "rate": rate,
                "unit": "MT",
                "effective_date": effective_date
            }
        )
        assert response.status_code == 201

    return supplier_id, product_id


def test_dashboard_summary(client):
    create_test_data(client)

    response = client.get("/dashboard/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_active_suppliers"] == 1
    assert data["total_active_buyers"] == 1
    assert data["total_active_products"] == 1
    assert data["total_rate_records"] == 3
    assert data["current_supplier_product_rates"] == 1
    assert data["lowest_current_rate"] == 51000
    assert data["highest_current_rate"] == 51000
    assert data["currency"] == "INR"
    assert data["unit"] == "MT"


def test_recent_rate_updates(client):
    create_test_data(client)

    response = client.get("/dashboard/recent-rates")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert data[0]["rate"] == 51000
    assert data[0]["supplier_name"] == "Dashboard Test Supplier"


def test_recent_rate_limit(client):
    create_test_data(client)

    response = client.get(
        "/dashboard/recent-rates",
        params={"limit": 2}
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_rate_history(client):
    supplier_id, product_id = create_test_data(client)

    response = client.get(
        f"/dashboard/rate-history/{product_id}",
        params={
            "start_date": "2026-11-20",
            "end_date": "2026-11-22"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product_id
    assert data["total_rate_updates"] == 3
    assert data["lowest_recorded_rate"] == 48500
    assert data["highest_recorded_rate"] == 51000
    assert data["average_recorded_rate"] == 49833.33
    assert len(data["rate_history"]) == 3


def test_rate_history_invalid_product(client):
    response = client.get("/dashboard/rate-history/999")

    assert response.status_code == 404


def test_rate_history_invalid_date_range(client):
    _, product_id = create_test_data(client)

    response = client.get(
        f"/dashboard/rate-history/{product_id}",
        params={
            "start_date": "2026-11-23",
            "end_date": "2026-11-20"
        }
    )

    assert response.status_code == 400


def test_market_trend_calculations(client):
    supplier_id, product_id = create_test_data(client)

    response = client.get(
        f"/dashboard/market-trend/{product_id}",
        params={
            "start_date": "2026-11-20",
            "end_date": "2026-11-22"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_rate_updates"] == 3
    assert data["opening_rate"] == 48500
    assert data["latest_rate"] == 51000
    assert data["average_rate"] == 49833.33
    assert data["minimum_rate"] == 48500
    assert data["maximum_rate"] == 51000
    assert data["absolute_change"] == 2500
    assert data["percentage_change"] == 5.15
    assert data["trend"] == "Increasing"

    assert len(data["supplier_movements"]) == 1

    movement = data["supplier_movements"][0]

    assert movement["supplier_id"] == supplier_id
    assert movement["total_rate_updates"] == 3
    assert movement["opening_rate"] == 48500
    assert movement["latest_rate"] == 51000
    assert movement["trend"] == "Increasing"


def test_market_trend_supplier_filter(client):
    supplier_id, product_id = create_test_data(client)

    response = client.get(
        f"/dashboard/market-trend/{product_id}",
        params={
            "start_date": "2026-11-20",
            "end_date": "2026-11-22",
            "supplier_id": supplier_id
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["supplier_id"] == supplier_id
    assert data["total_rate_updates"] == 3
    assert len(data["supplier_movements"]) == 1


def test_market_trend_no_records(client):
    product_response = client.post(
        "/products/",
        json={"product_name": "Empty Trend Product"}
    )

    product_id = product_response.json()["id"]

    response = client.get(
        f"/dashboard/market-trend/{product_id}",
        params={
            "start_date": "2026-11-20",
            "end_date": "2026-11-22"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_rate_updates"] == 0
    assert data["opening_rate"] is None
    assert data["latest_rate"] is None
    assert data["trend"] == "Insufficient Data"
    assert data["supplier_movements"] == []


def test_market_trend_invalid_product(client):
    response = client.get("/dashboard/market-trend/999")

    assert response.status_code == 404
