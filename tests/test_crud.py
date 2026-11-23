
# ==================================================
# SUPPLIER CRUD TESTS
# ==================================================

def test_create_supplier(client):
    response = client.post(
        "/suppliers/",
        json={
            "company_name": "Test Supplier",
            "contact_person": "Rahul Patel",
            "phone": "9876543210",
            "email": "supplier@example.com",
            "city": "Vadodara",
            "state": "Gujarat"
        }
    )

    assert response.status_code == 201
    assert response.json()["company_name"] == "Test Supplier"
    assert response.json()["is_active"] is True


def test_get_supplier(client):
    create_response = client.post(
        "/suppliers/",
        json={"company_name": "Test Supplier"}
    )

    supplier_id = create_response.json()["id"]

    response = client.get(f"/suppliers/{supplier_id}")

    assert response.status_code == 200
    assert response.json()["id"] == supplier_id


def test_update_supplier(client):
    create_response = client.post(
        "/suppliers/",
        json={"company_name": "Old Supplier"}
    )

    supplier_id = create_response.json()["id"]

    response = client.put(
        f"/suppliers/{supplier_id}",
        json={
            "company_name": "Updated Supplier",
            "city": "Vadodara"
        }
    )

    assert response.status_code == 200
    assert response.json()["company_name"] == "Updated Supplier"
    assert response.json()["city"] == "Vadodara"


def test_deactivate_supplier(client):
    create_response = client.post(
        "/suppliers/",
        json={"company_name": "Supplier To Deactivate"}
    )

    supplier_id = create_response.json()["id"]

    response = client.put(
        f"/suppliers/{supplier_id}",
        json={"is_active": False}
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_delete_supplier(client):
    create_response = client.post(
        "/suppliers/",
        json={"company_name": "Supplier To Delete"}
    )

    supplier_id = create_response.json()["id"]

    response = client.delete(f"/suppliers/{supplier_id}")

    assert response.status_code == 200

    get_response = client.get(f"/suppliers/{supplier_id}")
    assert get_response.status_code == 404


def test_invalid_supplier(client):
    response = client.post(
        "/suppliers/",
        json={"company_name": "A"}
    )

    assert response.status_code == 422


# ==================================================
# BUYER CRUD TESTS
# ==================================================

def test_create_buyer(client):
    response = client.post(
        "/buyers/",
        json={
            "company_name": "Test Buyer",
            "contact_person": "Amit Shah",
            "phone": "9876543210",
            "email": "buyer@example.com",
            "city": "Vadodara",
            "state": "Gujarat",
            "buyer_type": "Road Contractor"
        }
    )

    assert response.status_code == 201
    assert response.json()["company_name"] == "Test Buyer"
    assert response.json()["buyer_type"] == "Road Contractor"
    assert response.json()["is_active"] is True


def test_get_buyer(client):
    create_response = client.post(
        "/buyers/",
        json={"company_name": "Test Buyer"}
    )

    buyer_id = create_response.json()["id"]

    response = client.get(f"/buyers/{buyer_id}")

    assert response.status_code == 200
    assert response.json()["id"] == buyer_id


def test_update_buyer(client):
    create_response = client.post(
        "/buyers/",
        json={"company_name": "Old Buyer"}
    )

    buyer_id = create_response.json()["id"]

    response = client.put(
        f"/buyers/{buyer_id}",
        json={
            "company_name": "Updated Buyer",
            "buyer_type": "Distributor"
        }
    )

    assert response.status_code == 200
    assert response.json()["company_name"] == "Updated Buyer"
    assert response.json()["buyer_type"] == "Distributor"


def test_deactivate_buyer(client):
    create_response = client.post(
        "/buyers/",
        json={"company_name": "Buyer To Deactivate"}
    )

    buyer_id = create_response.json()["id"]

    response = client.put(
        f"/buyers/{buyer_id}",
        json={"is_active": False}
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_delete_buyer(client):
    create_response = client.post(
        "/buyers/",
        json={"company_name": "Buyer To Delete"}
    )

    buyer_id = create_response.json()["id"]

    response = client.delete(f"/buyers/{buyer_id}")

    assert response.status_code == 200

    get_response = client.get(f"/buyers/{buyer_id}")
    assert get_response.status_code == 404


def test_invalid_buyer(client):
    response = client.post(
        "/buyers/",
        json={"company_name": "A"}
    )

    assert response.status_code == 422


# ==================================================
# PRODUCT CRUD TESTS
# ==================================================

def test_create_product(client):
    response = client.post(
        "/products/",
        json={
            "product_name": "Bitumen",
            "grade": "VG30",
            "category": "Bitumen",
            "unit": "MT",
            "description": "VG30 grade bitumen"
        }
    )

    assert response.status_code == 201
    assert response.json()["product_name"] == "Bitumen"
    assert response.json()["grade"] == "VG30"
    assert response.json()["unit"] == "MT"
    assert response.json()["is_active"] is True


def test_get_product(client):
    create_response = client.post(
        "/products/",
        json={"product_name": "Bitumen"}
    )

    product_id = create_response.json()["id"]

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["id"] == product_id


def test_update_product(client):
    create_response = client.post(
        "/products/",
        json={"product_name": "Old Product"}
    )

    product_id = create_response.json()["id"]

    response = client.put(
        f"/products/{product_id}",
        json={
            "product_name": "Updated Bitumen",
            "grade": "VG40"
        }
    )

    assert response.status_code == 200
    assert response.json()["product_name"] == "Updated Bitumen"
    assert response.json()["grade"] == "VG40"


def test_deactivate_product(client):
    create_response = client.post(
        "/products/",
        json={"product_name": "Product To Deactivate"}
    )

    product_id = create_response.json()["id"]

    response = client.put(
        f"/products/{product_id}",
        json={"is_active": False}
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_delete_product(client):
    create_response = client.post(
        "/products/",
        json={"product_name": "Product To Delete"}
    )

    product_id = create_response.json()["id"]

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 200

    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404


def test_invalid_product(client):
    response = client.post(
        "/products/",
        json={"product_name": "A"}
    )

    assert response.status_code == 422


# ==================================================
# LIST ENDPOINT TESTS
# ==================================================

def test_list_suppliers(client):
    client.post("/suppliers/", json={"company_name": "Supplier One"})
    client.post("/suppliers/", json={"company_name": "Supplier Two"})

    response = client.get("/suppliers/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_buyers(client):
    client.post("/buyers/", json={"company_name": "Buyer One"})
    client.post("/buyers/", json={"company_name": "Buyer Two"})

    response = client.get("/buyers/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_products(client):
    client.post("/products/", json={"product_name": "Bitumen"})
    client.post("/products/", json={"product_name": "Emulsion"})

    response = client.get("/products/")

    assert response.status_code == 200
    assert len(response.json()) == 2
