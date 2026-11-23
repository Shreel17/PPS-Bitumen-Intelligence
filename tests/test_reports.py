
from backend.routers import report_archive as archive_module


def create_report_test_data(client):
    supplier_response = client.post(
        "/suppliers/",
        json={"company_name": "Report Test Supplier"}
    )
    supplier_id = supplier_response.json()["id"]

    product_response = client.post(
        "/products/",
        json={"product_name": "Report Test Bitumen"}
    )
    product_id = product_response.json()["id"]

    for effective_date, rate in [
        ("2026-11-20", 48500),
        ("2026-11-21", 50000),
        ("2026-11-22", 51000)
    ]:
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

    return product_id


def test_generate_market_report(client):
    product_id = create_report_test_data(client)

    response = client.get(
        f"/reports/market/{product_id}",
        params={
            "start_date": "2026-11-20",
            "end_date": "2026-11-22"
        }
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 500


def test_market_report_invalid_product(client):
    response = client.get(
        "/reports/market/999",
        params={
            "start_date": "2026-11-20",
            "end_date": "2026-11-22"
        }
    )

    assert response.status_code == 404


def test_market_report_invalid_date_range(client):
    product_id = create_report_test_data(client)

    response = client.get(
        f"/reports/market/{product_id}",
        params={
            "start_date": "2026-11-23",
            "end_date": "2026-11-20"
        }
    )

    assert response.status_code == 400


def test_generate_market_report_without_rate_history(client):
    product_response = client.post(
        "/products/",
        json={"product_name": "Report Without History"}
    )
    product_id = product_response.json()["id"]

    response = client.get(
        f"/reports/market/{product_id}",
        params={
            "start_date": "2026-11-20",
            "end_date": "2026-11-22"
        }
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_list_archived_reports(client, tmp_path, monkeypatch):
    monkeypatch.setattr(
        archive_module,
        "REPORTS_DIR",
        tmp_path
    )

    filename = "Daily_Market_Report_Product_1_2026-11-23.pdf"

    (tmp_path / filename).write_bytes(b"%PDF-test-report")

    response = client.get("/reports/archive/")

    assert response.status_code == 200

    data = response.json()

    assert data["total_reports"] == 1
    assert len(data["reports"]) == 1
    assert data["reports"][0]["filename"] == filename
    assert data["reports"][0]["product_id"] == 1


def test_archive_product_filter(client, tmp_path, monkeypatch):
    monkeypatch.setattr(
        archive_module,
        "REPORTS_DIR",
        tmp_path
    )

    (tmp_path / "Daily_Market_Report_Product_1_2026-11-23.pdf").write_bytes(
        b"%PDF-one"
    )

    (tmp_path / "Daily_Market_Report_Product_2_2026-11-23.pdf").write_bytes(
        b"%PDF-two"
    )

    response = client.get(
        "/reports/archive/",
        params={"product_id": 1}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_reports"] == 1
    assert data["reports"][0]["product_id"] == 1


def test_archive_date_filter(client, tmp_path, monkeypatch):
    monkeypatch.setattr(
        archive_module,
        "REPORTS_DIR",
        tmp_path
    )

    (tmp_path / "Daily_Market_Report_Product_1_2026-11-20.pdf").write_bytes(
        b"%PDF-old"
    )

    (tmp_path / "Daily_Market_Report_Product_1_2026-11-23.pdf").write_bytes(
        b"%PDF-new"
    )

    response = client.get(
        "/reports/archive/",
        params={
            "start_date": "2026-11-22",
            "end_date": "2026-11-23"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_reports"] == 1
    assert data["reports"][0]["report_date"] == "2026-11-23"


def test_archive_invalid_date_range(client, tmp_path, monkeypatch):
    monkeypatch.setattr(
        archive_module,
        "REPORTS_DIR",
        tmp_path
    )

    response = client.get(
        "/reports/archive/",
        params={
            "start_date": "2026-11-23",
            "end_date": "2026-11-20"
        }
    )

    assert response.status_code == 400


def test_download_archived_report(client, tmp_path, monkeypatch):
    monkeypatch.setattr(
        archive_module,
        "REPORTS_DIR",
        tmp_path
    )

    filename = "Daily_Market_Report_Product_1_2026-11-23.pdf"
    pdf_content = b"%PDF-1.4 test archived report"

    (tmp_path / filename).write_bytes(pdf_content)

    response = client.get(
        f"/reports/archive/download/{filename}"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content == pdf_content


def test_download_invalid_archive_filename(client, tmp_path, monkeypatch):
    monkeypatch.setattr(
        archive_module,
        "REPORTS_DIR",
        tmp_path
    )

    response = client.get(
        "/reports/archive/download/invalid.pdf"
    )

    assert response.status_code == 400


def test_download_missing_archived_report(client, tmp_path, monkeypatch):
    monkeypatch.setattr(
        archive_module,
        "REPORTS_DIR",
        tmp_path
    )

    response = client.get(
        "/reports/archive/download/Daily_Market_Report_Product_1_2026-11-23.pdf"
    )

    assert response.status_code == 404
