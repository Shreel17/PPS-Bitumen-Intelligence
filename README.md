# PPS Bitumen Intelligence

A Bitumen Supplier, Buyer, Rate Management and Market Intelligence Dashboard built using Python, FastAPI, SQLAlchemy, SQLite and Streamlit.

> **Project status:** Independent local prototype developed for demonstration and learning purposes. This is not an official PPS Anantams application. All sample supplier, buyer and rate records are illustrative and must not be treated as verified live market quotations.

## 1. Project Overview

PPS Bitumen Intelligence is a business-focused application designed to organize bitumen supplier and buyer information, maintain historical supplier rates, compare current supplier quotations, analyze market movements and generate automated PDF reports.

The application provides a centralized interface for managing business records and understanding historical rate trends.

## 2. Key Features

### Supplier Management
- Add and view suppliers.
- Edit supplier information.
- Activate or deactivate supplier records.
- Search and track supplier information.

### Buyer Management
- Add and manage buyer records.
- Update contact and company details.
- Activate or deactivate buyers.
- Maintain buyer information for business tracking.

### Product Management
- Maintain bitumen product records.
- Add and update product information.
- Activate or deactivate products.

### Supplier Rate Management
- Record supplier-specific product rates.
- Maintain effective dates and optional validity periods.
- Store rate sources and notes.
- Filter rates by supplier, product and effective date.
- Preserve historical rate records instead of overwriting previous quotations.

### Dashboard and Market Analytics
- View active supplier, buyer and product counts.
- Monitor recent rate updates.
- Compare current supplier rates.
- Identify the lowest and highest applicable supplier rates.
- Analyze historical market movements.
- Filter analytics by product, date range and supplier.
- Visualize supplier-wise rate trends.

### Market Intelligence Reports
- Generate downloadable PDF market reports.
- Include market movement summaries and supplier comparisons.
- Display supplier-wise rate movements and business observations.
- Generate daily reports automatically at 6:00 PM IST while the backend is running.

### Report Archive
- View previously generated daily reports.
- Filter reports by product and date.
- Download archived PDF reports.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| Data Processing | Pandas |
| Data Visualization | Altair |
| PDF Generation | ReportLab |
| Task Scheduling | APScheduler |
| API Communication | Requests |
| Automated Testing | Pytest |
| API Testing | FastAPI TestClient |

## 4. Project Architecture

The application follows a modular backend architecture.

```text
PPS-Bitumen-Intelligence/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── supplier.py
│   │   ├── buyer.py
│   │   ├── product.py
│   │   └── supplier_rate.py
│   │
│   ├── schemas/
│   │   ├── supplier.py
│   │   ├── buyer.py
│   │   ├── product.py
│   │   └── supplier_rate.py
│   │
│   ├── routers/
│   │   ├── supplier.py
│   │   ├── buyer.py
│   │   ├── product.py
│   │   ├── supplier_rate.py
│   │   ├── dashboard.py
│   │   ├── reports.py
│   │   └── report_archive.py
│   │
│   └── services/
│       ├── report_service.py
│       └── scheduler_service.py
│
├── frontend/
│   └── app.py
│
├── data/
│   └── pps_bitumen.db
│
├── reports/
│   └── Generated PDF reports
│
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_crud.py
│   ├── test_supplier_rates.py
│   ├── test_dashboard.py
│   └── test_reports.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## 5. Database Design

The application uses SQLite with SQLAlchemy ORM.

### Main entities

**Supplier**
- Supplier ID
- Company name
- Contact details
- Address
- Active status

**Buyer**
- Buyer ID
- Company name
- Contact details
- Address
- Buyer type
- Active status

**Product**
- Product ID
- Product name
- Description
- Active status

**SupplierRate**
- Rate ID
- Supplier ID
- Product ID
- Rate
- Unit
- Effective date
- Valid-until date
- Source
- Notes
- Creation timestamp

### Relationships

- One supplier can have multiple rate records.
- One product can have multiple supplier rate records.
- Each rate record references one supplier and one product.
- Previous rate records are preserved to support historical analytics.

## 6. Backend API Endpoints

The backend exposes REST APIs through FastAPI.

| Module | Endpoint | Method |
|---|---|---|
| Health | `/` | GET |
| Health | `/health` | GET |
| Database | `/database-status` | GET |
| Suppliers | `/suppliers/` | GET, POST |
| Buyers | `/buyers/` | GET, POST |
| Products | `/products/` | GET, POST |
| Supplier Rates | `/supplier-rates/` | GET, POST |
| Rate Comparison | `/supplier-rates/compare/{product_id}` | GET |
| Rate Details | `/supplier-rates/{rate_id}` | GET |
| Dashboard | `/dashboard/summary` | GET |
| Dashboard | `/dashboard/recent-rates` | GET |
| Rate History | `/dashboard/rate-history/{product_id}` | GET |
| Market Trend | `/dashboard/market-trend/{product_id}` | GET |
| Market Reports | `/reports/market/{product_id}` | GET |
| Report Archive | `/reports/archive/` | GET |
| Archive Download | `/reports/archive/download/{filename}` | GET |

Additional update and deactivation operations are available through the corresponding supplier, buyer and product routes.

## 7. Installation and Setup

### Prerequisites

- Python 3.10 or higher
- pip
- Git (optional)

### Step 1: Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd PPS-Bitumen-Intelligence
```

Replace `YOUR_REPOSITORY_URL` with the actual repository URL if the project is published.

Alternatively, open the existing project directory directly.

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

### Step 3: Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Start the backend

```bash
uvicorn backend.main:app --reload
```

Backend URL:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

### Step 6: Start the frontend

Open a second terminal, activate the virtual environment and run:

```bash
streamlit run frontend/app.py
```

Frontend URL:

http://localhost:8501

## 8. Automated Report Scheduling

The application uses APScheduler to register a daily report-generation job.

- Schedule: Every day at 6:00 PM.
- Time zone: Asia/Kolkata.
- Reports are generated for active products.
- The report period covers the preceding 30 days through the current date.
- Generated PDF files are saved in the `reports/` directory.

**Important:** The scheduler runs only while the backend application is running. This local prototype is not configured as an independent production scheduling service.

## 9. Running Automated Tests

The project uses Pytest and FastAPI TestClient.

Run the complete test suite:

```bash
python -m pytest -v
```

Run individual test modules:

```bash
python -m pytest tests/test_crud.py -v
python -m pytest tests/test_supplier_rates.py -v
python -m pytest tests/test_dashboard.py -v
python -m pytest tests/test_reports.py -v
python -m pytest tests/test_health.py -v
```

### Current Test Results

| Test Module | Passed |
|---|---:|
| CRUD operations | 21 |
| Supplier rate management | 20 |
| Dashboard analytics | 10 |
| Health endpoints | 2 |
| Reports and archive | 11 |
| **Total** | **64** |

All 64 automated tests passed in the latest local test run.

## 10. Business Value

The prototype demonstrates how a bitumen trading or supply business could:

- Centralize supplier and buyer records.
- Maintain historical supplier quotations.
- Compare applicable supplier rates.
- Monitor rate movements over time.
- Generate structured market intelligence reports.
- Reduce manual reporting through scheduled PDF generation.

## 11. Future Enhancements

Potential improvements include:

- PostgreSQL migration for multi-user deployment.
- Role-based authentication and access control.
- WhatsApp notifications for rate changes.
- Integration with verified market-rate data sources.
- Email delivery of scheduled reports.
- Advanced price forecasting and anomaly detection.
- Cloud deployment and production monitoring.
- Improved audit logs and reporting permissions.

## 12. Disclaimer

This project is an independent demonstration prototype. It is not an official PPS Anantams product or deployment. The sample records and prices are illustrative. The application does not currently connect to verified live bitumen market data.
