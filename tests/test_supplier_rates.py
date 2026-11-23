
from datetime import date


# ==================================================
# TEST DATA HELPERS
# ==================================================

def create_supplier(client, name="Test Supplier"):
    response = client.post(
        "/suppliers/",
        json={"company_name": name}
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_product(client, name="Bitumen"):
    response = client.post(
        "/products/",
        json={
            "product_name": name,
            "grade": "VG30",
            "unit": "MT"
        }
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_rate(
    client,
    supplier_id,
    product_id,
    rate,
    effective_date="2026-11-20",
    valid_until=None
):
    return client.post(
        "/supplier-rates/",
        json={
            "supplier_id": supplier_id,
            "product_id": product_id,
            "rate": rate,
            "unit": "MT",
            "effective_date": effective_date,
            "valid_until": valid_until
        }
    )


# ==================================================
# CREATE RATE TESTS
# ==================================================

def test_create_supplier_rate(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    response = create_rate(
        client, supplier_id, product_id, 48500
    )

    assert response.status_code == 201
    assert response.json()["rate"] == 48500
    assert response.json()["unit"] == "MT"
    assert response.json()["supplier_id"] == supplier_id
    assert response.json()["product_id"] == product_id


def test_create_rate_with_validity_period(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    response = create_rate(
        client,
        supplier_id,
        product_id,
        49000,
        "2026-11-20",
        "2026-11-30"
    )

    assert response.status_code == 201
    assert response.json()["valid_until"] == "2026-11-30"


def test_create_rate_with_invalid_supplier(client):
    product_id = create_product(client)

    response = create_rate(
        client, 999, product_id, 48500
    )

    assert response.status_code == 404


def test_create_rate_with_invalid_product(client):
    supplier_id = create_supplier(client)

    response = create_rate(
        client, supplier_id, 999, 48500
    )

    assert response.status_code == 404


def test_create_rate_with_zero_value(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    response = create_rate(
        client, supplier_id, product_id, 0
    )

    assert response.status_code == 422


def test_create_rate_with_negative_value(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    response = create_rate(
        client, supplier_id, product_id, -100
    )

    assert response.status_code == 422


def test_create_rate_with_invalid_validity_dates(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    response = create_rate(
        client,
        supplier_id,
        product_id,
        48500,
        "2026-11-25",
        "2026-11-20"
    )

    assert response.status_code == 400


# ==================================================
# READ AND FILTER RATE TESTS
# ==================================================

def test_get_supplier_rate_by_id(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    create_response = create_rate(
        client, supplier_id, product_id, 48500
    )

    rate_id = create_response.json()["id"]

    response = client.get(f"/supplier-rates/{rate_id}")

    assert response.status_code == 200
    assert response.json()["id"] == rate_id
    assert response.json()["rate"] == 48500


def test_get_nonexistent_supplier_rate(client):
    response = client.get("/supplier-rates/999")

    assert response.status_code == 404


def test_get_all_supplier_rates(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    create_rate(client, supplier_id, product_id, 48500)
    create_rate(
        client, supplier_id, product_id, 49000,
        "2026-11-22"
    )

    response = client.get("/supplier-rates/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_rates_by_supplier(client):
    supplier_a = create_supplier(client, "Supplier A")
    supplier_b = create_supplier(client, "Supplier B")
    product_id = create_product(client)

    create_rate(client, supplier_a, product_id, 48500)
    create_rate(client, supplier_b, product_id, 49000)

    response = client.get(
        "/supplier-rates/",
        params={"supplier_id": supplier_a}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["supplier_id"] == supplier_a


def test_filter_rates_by_product(client):
    supplier_id = create_supplier(client)
    product_a = create_product(client, "Bitumen")
    product_b = create_product(client, "Emulsion")

    create_rate(client, supplier_id, product_a, 48500)
    create_rate(client, supplier_id, product_b, 49000)

    response = client.get(
        "/supplier-rates/",
        params={"product_id": product_b}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["product_id"] == product_b


def test_filter_rates_by_effective_date(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    create_rate(
        client, supplier_id, product_id, 48500,
        "2026-11-20"
    )
    create_rate(
        client, supplier_id, product_id, 49000,
        "2026-11-25"
    )

    response = client.get(
        "/supplier-rates/",
        params={"effective_on": "2026-11-22"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["rate"] == 48500


def test_filter_rates_respects_valid_until(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    create_rate(
        client,
        supplier_id,
        product_id,
        48500,
        "2026-11-20",
        "2026-11-22"
    )

    response = client.get(
        "/supplier-rates/",
        params={"effective_on": "2026-11-23"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_rate_history_is_preserved(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    create_rate(
        client, supplier_id, product_id, 48500,
        "2026-11-20"
    )
    create_rate(
        client, supplier_id, product_id, 50000,
        "2026-11-24"
    )

    response = client.get(
        "/supplier-rates/",
        params={
            "supplier_id": supplier_id,
            "product_id": product_id
        }
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


# ==================================================
# SUPPLIER RATE COMPARISON TESTS
# ==================================================

def test_compare_supplier_rates(client):
    supplier_a = create_supplier(client, "Supplier A")
    supplier_b = create_supplier(client, "Supplier B")
    product_id = create_product(client)

    create_rate(
        client, supplier_a, product_id, 50000,
        "2026-11-20"
    )
    create_rate(
        client, supplier_b, product_id, 48750,
        "2026-11-20"
    )

    response = client.get(
        f"/supplier-rates/compare/{product_id}",
        params={"effective_on": "2026-11-24"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_suppliers"] == 2
    assert data["lowest_rate"] == 48750
    assert data["highest_rate"] == 50000
    assert data["rates"][0]["is_lowest"] is True
    assert data["rates"][0]["rate"] == 48750
    assert data["rates"][1]["difference_from_lowest"] == 1250


def test_comparison_uses_latest_rate_per_supplier(client):
    supplier_id = create_supplier(client)
    product_id = create_product(client)

    create_rate(
        client, supplier_id, product_id, 48500,
        "2026-11-20"
    )
    create_rate(
        client, supplier_id, product_id, 50000,
        "2026-11-24"
    )

    response = client.get(
        f"/supplier-rates/compare/{product_id}",
        params={"effective_on": "2026-11-25"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_suppliers"] == 1
    assert data["rates"][0]["rate"] == 50000


def test_comparison_excludes_inactive_suppliers(client):
    supplier_a = create_supplier(client, "Active Supplier")
    supplier_b = create_supplier(client, "Inactive Supplier")
    product_id = create_product(client)

    create_rate(client, supplier_a, product_id, 50000)
    create_rate(client, supplier_b, product_id, 48000)

    client.put(
        f"/suppliers/{supplier_b}",
        json={"is_active": False}
    )

    response = client.get(
        f"/supplier-rates/compare/{product_id}",
        params={"effective_on": "2026-11-25"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_suppliers"] == 1
    assert data["rates"][0]["supplier_id"] == supplier_a


def test_compare_nonexistent_product(client):
    response = client.get(
        "/supplier-rates/compare/999",
        params={"effective_on": "2026-11-25"}
    )

    assert response.status_code == 404


def test_comparison_with_no_applicable_rates(client):
    product_id = create_product(client)

    response = client.get(
        f"/supplier-rates/compare/{product_id}",
        params={"effective_on": "2026-11-25"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_suppliers"] == 0
    assert data["lowest_rate"] is None
    assert data["highest_rate"] is None
    assert data["rates"] == []
