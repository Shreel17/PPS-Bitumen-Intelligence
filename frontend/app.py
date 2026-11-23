
import requests
import pandas as pd
import streamlit as st
import altair as alt

from datetime import date, timedelta


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="PPS Bitumen Intelligence",
    page_icon="🏗️",
    layout="wide"
)

API_BASE_URL = "http://127.0.0.1:8000"


# ==================================================
# 2. API HELPER FUNCTIONS
# ==================================================

def api_get(endpoint, params=None):
    """Send GET requests to FastAPI."""

    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            params=params,
            timeout=10
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text

        st.error(f"API Error: {detail}")
        return None

    except requests.exceptions.RequestException as error:
        st.error(f"Backend connection error: {error}")
        return None


def api_write(endpoint, method="POST", data=None):
    """Send POST or PUT requests to FastAPI."""

    try:
        url = f"{API_BASE_URL}{endpoint}"

        if method == "POST":
            response = requests.post(
                url,
                json=data,
                timeout=10
            )

        elif method == "PUT":
            response = requests.put(
                url,
                json=data,
                timeout=10
            )

        else:
            st.error("Unsupported API method.")
            return None

        response.raise_for_status()

        if response.content:
            return response.json()

        return {}

    except requests.exceptions.HTTPError:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text

        st.error(f"API Error: {detail}")
        return None

    except requests.exceptions.RequestException as error:
        st.error(f"Backend connection error: {error}")
        return None

    
def api_download(endpoint, params=None):
    """Download a PDF report from FastAPI."""

    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            params=params,
            timeout=60
        )

        response.raise_for_status()

        return response.content

    except requests.exceptions.HTTPError:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text

        st.error(f"Report generation failed: {detail}")
        return None

    except requests.exceptions.RequestException as error:
        st.error(f"Backend connection error: {error}")
        return None



# ==================================================
# 3. CUSTOM STYLING
# ==================================================

st.markdown("""
<style>
    .main-title {
        font-size: 30px;
        font-weight: 700;
        color: #1F4E79;
    }

    .sub-title {
        color: #64748b;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)


# ==================================================
# 4. APPLICATION HEADER
# ==================================================

st.markdown(
    '<div class="main-title">PPS Bitumen Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Supplier, Buyer and Market Rate Management'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==================================================
# 5. SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("PPS Intelligence")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Supplier Management",
        "Buyer Management",
        "Product Management",
        "Supplier Rate Management",
        "Report Archive"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "Prototype | Local Development"
)


# ==================================================
# 6. DASHBOARD PAGE
# ==================================================

if page == "Dashboard":

    st.subheader("Business Overview")

    # ----------------------------------------------
    # DASHBOARD SUMMARY
    # ----------------------------------------------

    summary = api_get("/dashboard/summary")

    if summary is None:
        st.stop()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Active Suppliers",
        summary["total_active_suppliers"]
    )

    col2.metric(
        "Active Buyers",
        summary["total_active_buyers"]
    )

    col3.metric(
        "Active Products",
        summary["total_active_products"]
    )

    col4.metric(
        "Total Rate Records",
        summary["total_rate_records"]
    )

    st.divider()

    # ----------------------------------------------
    # CURRENT MARKET RATE OVERVIEW
    # ----------------------------------------------

    st.subheader("Current Market Rate Overview")

    col1, col2, col3 = st.columns(3)

    lowest = summary["lowest_current_rate"]
    highest = summary["highest_current_rate"]

    col1.metric(
        "Current Supplier-Product Rates",
        summary["current_supplier_product_rates"]
    )

    col2.metric(
        "Lowest Current Rate",
        f"₹{lowest:,.2f}" if lowest is not None else "N/A",
        "Per MT"
    )

    col3.metric(
        "Highest Current Rate",
        f"₹{highest:,.2f}" if highest is not None else "N/A",
        "Per MT"
    )

    st.caption(
        f"Rate overview as of {summary['as_of_date']}. "
        "Prices are illustrative prototype data."
    )

    st.divider()

    # ----------------------------------------------
    # RECENT RATE UPDATES
    # ----------------------------------------------

    st.subheader("Recent Supplier Rate Updates")

    recent_rates = api_get(
        "/dashboard/recent-rates",
        params={"limit": 10}
    )

    if recent_rates is not None:

        if recent_rates:

            recent_df = pd.DataFrame(recent_rates)

            st.dataframe(
                recent_df,
                width="stretch",
                hide_index=True
            )

        else:
            st.info("No rate updates available yet.")

    st.divider()

    # ----------------------------------------------
    # PRODUCT RATE ANALYSIS
    # ----------------------------------------------

    st.subheader("Product Rate Analysis")

    products = api_get("/products/")

    if products is None:
        st.stop()

    if products:

        product_options = {
            f"{product['product_name']} (ID: {product['id']})":
            product["id"]
            for product in products
        }

        selected_product = st.selectbox(
            "Select Product",
            list(product_options.keys())
        )

        product_id = product_options[selected_product]

        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Start Date",
                value=date.today() - timedelta(days=30),
                key="history_start_date"
            )

        with col2:
            end_date = st.date_input(
                "End Date",
                value=date.today(),
                key="history_end_date"
            )

        if start_date > end_date:

            st.warning(
                "Start date cannot be later than end date."
            )

        else:

            history = api_get(
                f"/dashboard/rate-history/{product_id}",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )

            if history is not None:

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Rate Updates",
                    history["total_rate_updates"]
                )

                col2.metric(
                    "Lowest Recorded",
                    (
                        f"₹{history['lowest_recorded_rate']:,.2f}"
                        if history["lowest_recorded_rate"] is not None
                        else "N/A"
                    )
                )

                col3.metric(
                    "Highest Recorded",
                    (
                        f"₹{history['highest_recorded_rate']:,.2f}"
                        if history["highest_recorded_rate"] is not None
                        else "N/A"
                    )
                )

                col4.metric(
                    "Average Recorded",
                    (
                        f"₹{history['average_recorded_rate']:,.2f}"
                        if history["average_recorded_rate"] is not None
                        else "N/A"
                    )
                )

                history_df = pd.DataFrame(
                    history["rate_history"]
                )

                if not history_df.empty:

                    # ----------------------------------
                    # RATE TREND CHART
                    # ----------------------------------

                    st.markdown("#### Recorded Rate Trend")

                    history_df["effective_date"] = pd.to_datetime(
                        history_df["effective_date"]
                    )

                    chart_df = history_df.sort_values(
                        "effective_date"
                    )

                    trend_chart = (
                        alt.Chart(chart_df)
                        .mark_line(
                            point=alt.OverlayMarkDef(
                                filled=True,
                                size=80
                            )
                        )
                        .encode(
                            x=alt.X(
                                "effective_date:T",
                                title="Effective Date",
                                axis=alt.Axis(
                                    format="%d %b",
                                    labelAngle=0,
                                    tickCount=alt.TimeIntervalStep(
                                        interval="day",
                                        step=1
                                    )
                                )
                            ),
                            y=alt.Y(
                                "rate:Q",
                                title="Rate (₹/MT)",
                                scale=alt.Scale(zero=False)
                            ),
                            color=alt.Color(
                                "supplier_name:N",
                                title="Supplier"
                            ),
                            tooltip=[
                                alt.Tooltip(
                                    "supplier_name:N",
                                    title="Supplier"
                                ),
                                alt.Tooltip(
                                    "rate:Q",
                                    title="Rate",
                                    format=",.2f"
                                ),
                                alt.Tooltip(
                                    "effective_date:T",
                                    title="Effective Date",
                                    format="%d %b %Y"
                                )
                            ]
                        )
                        .properties(height=350)
                        .interactive()
                    )

                    st.altair_chart(
                        trend_chart,
                        width="stretch"
                    )

                    # ----------------------------------
                    # RATE HISTORY TABLE
                    # ----------------------------------

                    st.markdown("#### Rate History Details")

                    st.dataframe(
                        history_df,
                        width="stretch",
                        hide_index=True
                    )

                else:

                    st.info(
                        "No rate records found for this date range."
                    )

        st.divider()

        # ----------------------------------------------
        # HISTORICAL MARKET TREND ANALYTICS
        # ----------------------------------------------

        st.subheader("Historical Market Trend Analytics")

        trend_col1, trend_col2 = st.columns(2)

        with trend_col1:
            trend_start_date = st.date_input(
                "Trend Start Date",
                value=date.today() - timedelta(days=30),
                key="market_trend_start"
            )

        with trend_col2:
            trend_end_date = st.date_input(
                "Trend End Date",
                value=date.today(),
                key="market_trend_end"
            )

        # Fetch supplier options for the selected product
        trend_suppliers = api_get("/suppliers/")

        if trend_suppliers is not None:

            trend_supplier_options = {
                "All Suppliers": None
            }

            trend_supplier_options.update({
                f"{supplier['company_name']} "
                f"(ID: {supplier['id']})": supplier["id"]
                for supplier in trend_suppliers
                if supplier.get("is_active", False)
            })

            selected_trend_supplier = st.selectbox(
                "Analyze Supplier",
                list(trend_supplier_options.keys()),
                key="market_trend_supplier"
            )

            selected_trend_supplier_id = (
                trend_supplier_options[selected_trend_supplier]
            )

            if trend_start_date > trend_end_date:

                st.warning(
                    "Trend start date cannot be later than end date."
                )

            else:

                trend_params = {
                    "start_date": trend_start_date.isoformat(),
                    "end_date": trend_end_date.isoformat()
                }

                if selected_trend_supplier_id is not None:
                    trend_params["supplier_id"] = (
                        selected_trend_supplier_id
                    )

                market_trend = api_get(
                    f"/dashboard/market-trend/{product_id}",
                    params=trend_params
                )

                if market_trend is not None:

                    if market_trend["total_rate_updates"] > 0:

                        st.markdown("#### Market Movement Summary")

                        metric1, metric2, metric3, metric4 = st.columns(4)

                        metric1.metric(
                            "Rate Updates",
                            market_trend["total_rate_updates"]
                        )

                        metric2.metric(
                            "Opening Rate",
                            f"₹{market_trend['opening_rate']:,.2f}"
                        )

                        metric3.metric(
                            "Latest Rate",
                            f"₹{market_trend['latest_rate']:,.2f}"
                        )

                        metric4.metric(
                            "Average Rate",
                            f"₹{market_trend['average_rate']:,.2f}"
                        )

                        metric5, metric6, metric7 = st.columns(3)

                        metric5.metric(
                            "Minimum Rate",
                            f"₹{market_trend['minimum_rate']:,.2f}"
                        )

                        metric6.metric(
                            "Maximum Rate",
                            f"₹{market_trend['maximum_rate']:,.2f}"
                        )

                        change = market_trend["absolute_change"]
                        percentage = market_trend["percentage_change"]

                        metric7.metric(
                            "Price Movement",
                            f"₹{change:,.2f}",
                            (
                                f"{percentage:+.2f}%"
                                if percentage is not None
                                else None
                            )
                        )

                        trend = market_trend["trend"]

                        if trend == "Increasing":
                            st.warning(
                                "Overall recorded movement: Increasing"
                            )
                        elif trend == "Decreasing":
                            st.success(
                                "Overall recorded movement: Decreasing"
                            )
                        else:
                            st.info(
                                f"Overall recorded movement: {trend}"
                            )

                        # ----------------------------------
                        # SUPPLIER-WISE TREND CHART
                        # ----------------------------------

                        st.markdown("#### Supplier-wise Price Movement")

                        supplier_chart_records = []

                        for movement in market_trend["supplier_movements"]:

                            for point in movement["rate_history"]:

                                supplier_chart_records.append({
                                    "Supplier": movement["supplier_name"],
                                    "Effective Date": point["effective_date"],
                                    "Rate": point["rate"]
                                })

                        supplier_chart_df = pd.DataFrame(
                            supplier_chart_records
                        )

                        if not supplier_chart_df.empty:

                            supplier_chart_df["Effective Date"] = (
                                pd.to_datetime(
                                    supplier_chart_df["Effective Date"]
                                )
                            )

                            supplier_trend_chart = (
                                alt.Chart(supplier_chart_df)
                                .mark_line(
                                    point=alt.OverlayMarkDef(
                                        filled=True,
                                        size=80
                                    )
                                )
                                .encode(
                                    x=alt.X(
                                        "Effective Date:T",
                                        title="Effective Date",
                                        axis=alt.Axis(
                                            format="%d %b",
                                            labelAngle=0
                                        )
                                    ),
                                    y=alt.Y(
                                        "Rate:Q",
                                        title="Rate (₹/MT)",
                                        scale=alt.Scale(zero=False)
                                    ),
                                    color=alt.Color(
                                        "Supplier:N",
                                        title="Supplier"
                                    ),
                                    tooltip=[
                                        alt.Tooltip(
                                            "Supplier:N",
                                            title="Supplier"
                                        ),
                                        alt.Tooltip(
                                            "Rate:Q",
                                            title="Rate",
                                            format=",.2f"
                                        ),
                                        alt.Tooltip(
                                            "Effective Date:T",
                                            title="Effective Date",
                                            format="%d %b %Y"
                                        )
                                    ]
                                )
                                .properties(height=350)
                                .interactive()
                            )

                            st.altair_chart(
                                supplier_trend_chart,
                                width="stretch"
                            )

                        # ----------------------------------
                        # SUPPLIER MOVEMENT TABLE
                        # ----------------------------------

                        st.markdown("#### Supplier-wise Movement Details")

                        movement_records = []

                        for movement in market_trend["supplier_movements"]:

                            movement_records.append({
                                "Supplier": movement["supplier_name"],
                                "Rate Updates": movement["total_rate_updates"],
                                "Opening Rate (₹)": movement["opening_rate"],
                                "Latest Rate (₹)": movement["latest_rate"],
                                "Change (₹)": movement["absolute_change"],
                                "Change (%)": movement["percentage_change"],
                                "Trend": movement["trend"]
                            })

                        movement_df = pd.DataFrame(
                            movement_records
                        )

                        st.dataframe(
                            movement_df,
                            width="stretch",
                            hide_index=True
                        )

                    else:

                        st.info(
                            "No historical rate updates found "
                            "for the selected product, supplier and date range."
                        )


        # ----------------------------------------------
        # SUPPLIER RATE COMPARISON
        # ----------------------------------------------

        st.subheader("Supplier Rate Comparison")

        comparison_date = st.date_input(
            "Compare rates as of",
            value=date.today(),
            key="comparison_date"
        )

        comparison = api_get(
            f"/supplier-rates/compare/{product_id}",
            params={
                "effective_on": comparison_date.isoformat()
            }
        )

        if comparison is not None:

            comparison_rates = comparison.get("rates", [])

            if comparison_rates:

                comparison_df = pd.DataFrame(
                    comparison_rates
                )

                st.dataframe(
                    comparison_df,
                    width="stretch",
                    hide_index=True
                )

                best_rate = comparison_rates[0]

                st.success(
                    f"Lowest available recorded rate: "
                    f"{best_rate['supplier_name']} — "
                    f"₹{best_rate['rate']:,.2f}/{best_rate['unit']}"
                )

            else:

                st.info(
                    "No applicable supplier rates found for this date."
                )

        st.divider()

        # ----------------------------------------------
        # MARKET INTELLIGENCE REPORT
        # ----------------------------------------------

        st.subheader("Market Intelligence Report")

        st.write(
            "Generate a downloadable PDF containing historical "
            "market movement, supplier rate comparison, "
            "supplier-wise trends and business observations."
        )

        st.caption(
            f"Report period: {trend_start_date} to {trend_end_date}"
        )

        report_signature = (
            product_id,
            trend_start_date.isoformat(),
            trend_end_date.isoformat()
        )

        if st.button(
            "Generate Market Intelligence Report",
            type="primary",
            width="stretch",
            key="generate_market_report"
        ):

            if trend_start_date > trend_end_date:

                st.error(
                    "Please select a valid reporting date range."
                )

            else:

                with st.spinner(
                    "Generating your PDF market intelligence report..."
                ):

                    pdf_data = api_download(
                        f"/reports/market/{product_id}",
                        params={
                            "start_date": trend_start_date.isoformat(),
                            "end_date": trend_end_date.isoformat()
                        }
                    )

                if pdf_data:

                    st.session_state["market_report_pdf"] = pdf_data

                    st.session_state["market_report_signature"] = (
                        report_signature
                    )

                    st.success(
                        "Market Intelligence Report generated successfully!"
                    )

        # Show download button only for the currently selected
        # product and reporting date range.

        if (
            st.session_state.get("market_report_signature")
            == report_signature
            and st.session_state.get("market_report_pdf")
        ):

            filename = (
                f"Bitumen_Market_Report_{product_id}_"
                f"{trend_start_date}_{trend_end_date}.pdf"
            )

            st.download_button(
                label="Download PDF Report",
                data=st.session_state["market_report_pdf"],
                file_name=filename,
                mime="application/pdf",
                width="stretch",
                key="download_market_report"
            )


    else:

        st.info(
            "Add a product to begin product rate analysis."
        )

    st.divider()

    st.caption(
        "PPS Bitumen Intelligence | Demonstration Prototype | "
        "Data stored locally in SQLite"
    )


# ==================================================
# 7. SUPPLIER MANAGEMENT PAGE
# ==================================================

elif page == "Supplier Management":

    st.subheader("Supplier Management")

    st.write(
        "Add, view, edit and deactivate suppliers. "
        "Supplier records are retained for historical rate tracking."
    )

    # ----------------------------------------------
    # SUCCESS MESSAGE
    # ----------------------------------------------

    flash = st.session_state.pop(
        "supplier_flash",
        None
    )

    if flash:
        st.success(flash)

    # ----------------------------------------------
    # FETCH SUPPLIERS
    # ----------------------------------------------

    suppliers = api_get("/suppliers/")

    if suppliers is None:
        st.stop()

    # ----------------------------------------------
    # ADD NEW SUPPLIER
    # ----------------------------------------------

    st.markdown("### Add New Supplier")

    with st.form(
        "add_supplier_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            company_name = st.text_input(
                "Company Name *"
            )

            contact_person = st.text_input(
                "Contact Person"
            )

            phone = st.text_input(
                "Phone Number"
            )

            email = st.text_input(
                "Email Address"
            )

        with col2:

            city = st.text_input("City")

            state = st.text_input("State")

            address = st.text_area(
                "Full Address"
            )

        add_submitted = st.form_submit_button(
            "Add Supplier",
            width="stretch"
        )

    if add_submitted:

        if len(company_name.strip()) < 2:

            st.error(
                "Company name must contain at least 2 characters."
            )

        else:

            supplier_data = {
                "company_name": company_name.strip(),
                "contact_person": contact_person.strip() or None,
                "phone": phone.strip() or None,
                "email": email.strip() or None,
                "city": city.strip() or None,
                "state": state.strip() or None,
                "address": address.strip() or None
            }

            result = api_write(
                "/suppliers/",
                method="POST",
                data=supplier_data
            )

            if result is not None:

                st.session_state["supplier_flash"] = (
                    f"Supplier '{result['company_name']}' "
                    "added successfully."
                )

                st.rerun()

    st.divider()

    # ----------------------------------------------
    # SUPPLIER DATABASE
    # ----------------------------------------------

    st.markdown("### Supplier Database")

    if suppliers:

        supplier_df = pd.DataFrame(suppliers)

        st.dataframe(
            supplier_df,
            width="stretch",
            hide_index=True
        )

        active_count = sum(
            1 for supplier in suppliers
            if supplier["is_active"]
        )

        inactive_count = len(suppliers) - active_count

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Suppliers", len(suppliers))
        col2.metric("Active Suppliers", active_count)
        col3.metric("Inactive Suppliers", inactive_count)

    else:

        st.info("No suppliers registered yet.")

    st.divider()

    # ----------------------------------------------
    # EDIT / ACTIVATE / DEACTIVATE SUPPLIER
    # ----------------------------------------------

    st.markdown("### Update Supplier Information")

    if suppliers:

        supplier_options = {
            f"{supplier['company_name']} "
            f"(ID: {supplier['id']})": supplier
            for supplier in suppliers
        }

        selected_label = st.selectbox(
            "Select Supplier",
            list(supplier_options.keys())
        )

        selected_supplier = supplier_options[selected_label]

        supplier_id = selected_supplier["id"]

        with st.form(
            f"update_supplier_form_{supplier_id}"
        ):

            st.markdown(
                f"**Editing Supplier ID: {supplier_id}**"
            )

            col1, col2 = st.columns(2)

            with col1:

                edit_company_name = st.text_input(
                    "Company Name",
                    value=selected_supplier["company_name"] or "",
                    key=f"edit_company_{supplier_id}"
                )

                edit_contact_person = st.text_input(
                    "Contact Person",
                    value=selected_supplier["contact_person"] or "",
                    key=f"edit_contact_{supplier_id}"
                )

                edit_phone = st.text_input(
                    "Phone Number",
                    value=selected_supplier["phone"] or "",
                    key=f"edit_phone_{supplier_id}"
                )

                edit_email = st.text_input(
                    "Email Address",
                    value=selected_supplier["email"] or "",
                    key=f"edit_email_{supplier_id}"
                )

            with col2:

                edit_city = st.text_input(
                    "City",
                    value=selected_supplier["city"] or "",
                    key=f"edit_city_{supplier_id}"
                )

                edit_state = st.text_input(
                    "State",
                    value=selected_supplier["state"] or "",
                    key=f"edit_state_{supplier_id}"
                )

                edit_address = st.text_area(
                    "Address",
                    value=selected_supplier["address"] or "",
                    key=f"edit_address_{supplier_id}"
                )

                edit_active = st.checkbox(
                    "Supplier is active",
                    value=bool(selected_supplier["is_active"]),
                    key=f"edit_active_{supplier_id}"
                )

            update_submitted = st.form_submit_button(
                "Save Changes",
                width="stretch"
            )

        if update_submitted:

            if len(edit_company_name.strip()) < 2:

                st.error(
                    "Company name must contain at least 2 characters."
                )

            else:

                updated_data = {
                    "company_name": edit_company_name.strip(),
                    "contact_person": edit_contact_person.strip() or None,
                    "phone": edit_phone.strip() or None,
                    "email": edit_email.strip() or None,
                    "city": edit_city.strip() or None,
                    "state": edit_state.strip() or None,
                    "address": edit_address.strip() or None,
                    "is_active": edit_active
                }

                result = api_write(
                    f"/suppliers/{supplier_id}",
                    method="PUT",
                    data=updated_data
                )

                if result is not None:

                    st.session_state["supplier_flash"] = (
                        f"Supplier '{edit_company_name}' "
                        "updated successfully."
                    )

                    st.rerun()

    else:

        st.info(
            "Add a supplier first to enable supplier editing."
        )

    st.divider()

    st.caption(
        "PPS Bitumen Intelligence | Demonstration Prototype | "
        "Data stored locally in SQLite"
    )


# ==================================================
# 8. BUYER MANAGEMENT PAGE
# ==================================================

elif page == "Buyer Management":

    st.subheader("Buyer Management")

    st.write(
        "Add, view, edit and deactivate buyers. "
        "Buyer records are retained for business tracking."
    )

    # ----------------------------------------------
    # SUCCESS MESSAGE
    # ----------------------------------------------

    flash = st.session_state.pop(
        "buyer_flash",
        None
    )

    if flash:
        st.success(flash)

    # ----------------------------------------------
    # FETCH BUYERS
    # ----------------------------------------------

    buyers = api_get("/buyers/")

    if buyers is None:
        st.stop()

    # ----------------------------------------------
    # ADD NEW BUYER
    # ----------------------------------------------

    st.markdown("### Add New Buyer")

    with st.form(
        "add_buyer_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            company_name = st.text_input(
                "Company Name *",
                key="new_buyer_company"
            )

            contact_person = st.text_input(
                "Contact Person",
                key="new_buyer_contact"
            )

            phone = st.text_input(
                "Phone Number",
                key="new_buyer_phone"
            )

            email = st.text_input(
                "Email Address",
                key="new_buyer_email"
            )

        with col2:

            city = st.text_input(
                "City",
                key="new_buyer_city"
            )

            state = st.text_input(
                "State",
                key="new_buyer_state"
            )

            buyer_type = st.selectbox(
                "Buyer Type",
                [
                    "Road Contractor",
                    "Infrastructure Company",
                    "Government Department",
                    "Distributor",
                    "Dealer",
                    "Other"
                ],
                key="new_buyer_type"
            )

            address = st.text_area(
                "Full Address",
                key="new_buyer_address"
            )

        add_submitted = st.form_submit_button(
            "Add Buyer",
            width="stretch"
        )

    if add_submitted:

        if len(company_name.strip()) < 2:

            st.error(
                "Company name must contain at least 2 characters."
            )

        else:

            buyer_data = {
                "company_name": company_name.strip(),
                "contact_person": contact_person.strip() or None,
                "phone": phone.strip() or None,
                "email": email.strip() or None,
                "city": city.strip() or None,
                "state": state.strip() or None,
                "buyer_type": buyer_type,
                "address": address.strip() or None
            }

            result = api_write(
                "/buyers/",
                method="POST",
                data=buyer_data
            )

            if result is not None:

                st.session_state["buyer_flash"] = (
                    f"Buyer '{result.get('company_name', company_name)}' "
                    "added successfully."
                )

                st.rerun()

    st.divider()

    # ----------------------------------------------
    # BUYER DATABASE
    # ----------------------------------------------

    st.markdown("### Buyer Database")

    if buyers:

        buyer_df = pd.DataFrame(buyers)

        search_term = st.text_input(
            "Search by company, contact person, phone or city",
            key="buyer_search"
        )

        if search_term.strip():

            searchable_columns = [
                "company_name",
                "contact_person",
                "phone",
                "city"
            ]

            mask = pd.Series(
                False,
                index=buyer_df.index
            )

            for column in searchable_columns:

                if column in buyer_df.columns:

                    mask |= (
                        buyer_df[column]
                        .fillna("")
                        .astype(str)
                        .str.contains(
                            search_term.strip(),
                            case=False,
                            regex=False
                        )
                    )

            filtered_df = buyer_df[mask]

        else:

            filtered_df = buyer_df

        st.dataframe(
            filtered_df,
            width="stretch",
            hide_index=True
        )

        active_count = sum(
            1 for buyer in buyers
            if buyer["is_active"]
        )

        inactive_count = len(buyers) - active_count

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Buyers", len(buyers))
        col2.metric("Active Buyers", active_count)
        col3.metric("Inactive Buyers", inactive_count)

        st.caption(
            f"Showing {len(filtered_df)} of {len(buyers)} buyers."
        )

    else:

        st.info(
            "No buyers registered yet. Add your first buyer above."
        )

    st.divider()

    # ----------------------------------------------
    # EDIT / ACTIVATE / DEACTIVATE BUYER
    # ----------------------------------------------

    st.markdown("### Update Buyer Information")

    if buyers:

        buyer_options = {
            f"{buyer['company_name']} (ID: {buyer['id']})": buyer
            for buyer in buyers
        }

        selected_label = st.selectbox(
            "Select Buyer",
            list(buyer_options.keys()),
            key="selected_buyer"
        )

        selected_buyer = buyer_options[selected_label]

        buyer_id = selected_buyer["id"]

        with st.form(
            f"update_buyer_form_{buyer_id}"
        ):

            st.markdown(
                f"**Editing Buyer ID: {buyer_id}**"
            )

            col1, col2 = st.columns(2)

            with col1:

                edit_company_name = st.text_input(
                    "Company Name",
                    value=selected_buyer["company_name"] or "",
                    key=f"buyer_company_{buyer_id}"
                )

                edit_contact_person = st.text_input(
                    "Contact Person",
                    value=selected_buyer.get("contact_person") or "",
                    key=f"buyer_contact_{buyer_id}"
                )

                edit_phone = st.text_input(
                    "Phone Number",
                    value=selected_buyer.get("phone") or "",
                    key=f"buyer_phone_{buyer_id}"
                )

                edit_email = st.text_input(
                    "Email Address",
                    value=selected_buyer.get("email") or "",
                    key=f"buyer_email_{buyer_id}"
                )

            with col2:

                edit_city = st.text_input(
                    "City",
                    value=selected_buyer.get("city") or "",
                    key=f"buyer_city_{buyer_id}"
                )

                edit_state = st.text_input(
                    "State",
                    value=selected_buyer.get("state") or "",
                    key=f"buyer_state_{buyer_id}"
                )

                buyer_types = [
                    "Road Contractor",
                    "Infrastructure Company",
                    "Government Department",
                    "Distributor",
                    "Dealer",
                    "Other"
                ]

                existing_type = (
                    selected_buyer.get("buyer_type") or "Other"
                )

                if existing_type not in buyer_types:
                    buyer_types.append(existing_type)

                edit_buyer_type = st.selectbox(
                    "Buyer Type",
                    buyer_types,
                    index=buyer_types.index(existing_type),
                    key=f"buyer_type_{buyer_id}"
                )

                edit_address = st.text_area(
                    "Address",
                    value=selected_buyer.get("address") or "",
                    key=f"buyer_address_{buyer_id}"
                )

                edit_active = st.checkbox(
                    "Buyer is active",
                    value=bool(selected_buyer["is_active"]),
                    key=f"buyer_active_{buyer_id}"
                )

            update_submitted = st.form_submit_button(
                "Save Changes",
                width="stretch"
            )

        if update_submitted:

            if len(edit_company_name.strip()) < 2:

                st.error(
                    "Company name must contain at least 2 characters."
                )

            else:

                updated_data = {
                    "company_name": edit_company_name.strip(),
                    "contact_person": edit_contact_person.strip() or None,
                    "phone": edit_phone.strip() or None,
                    "email": edit_email.strip() or None,
                    "city": edit_city.strip() or None,
                    "state": edit_state.strip() or None,
                    "buyer_type": edit_buyer_type,
                    "address": edit_address.strip() or None,
                    "is_active": edit_active
                }

                result = api_write(
                    f"/buyers/{buyer_id}",
                    method="PUT",
                    data=updated_data
                )

                if result is not None:

                    st.session_state["buyer_flash"] = (
                        f"Buyer '{edit_company_name}' "
                        "updated successfully."
                    )

                    st.rerun()

    else:

        st.info(
            "Add a buyer first to enable buyer editing."
        )

    st.divider()

    st.caption(
        "PPS Bitumen Intelligence | Demonstration Prototype | "
        "Data stored locally in SQLite"
    )


# ==================================================
# 9. PRODUCT MANAGEMENT PAGE
# ==================================================

elif page == "Product Management":

    st.subheader("Product Management")

    st.write(
        "Add, view, edit and deactivate products. "
        "Product records are retained for historical rate tracking."
    )

    # ----------------------------------------------
    # SUCCESS MESSAGE
    # ----------------------------------------------

    flash = st.session_state.pop(
        "product_flash",
        None
    )

    if flash:
        st.success(flash)

    # ----------------------------------------------
    # FETCH PRODUCTS
    # ----------------------------------------------

    products = api_get("/products/")

    if products is None:
        st.stop()

    # ----------------------------------------------
    # ADD NEW PRODUCT
    # ----------------------------------------------

    st.markdown("### Add New Product")

    with st.form(
        "add_product_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            product_name = st.text_input(
                "Product Name *"
            )

            grade = st.text_input(
                "Grade",
                placeholder="Example: VG-30"
            )

            category = st.selectbox(
                "Product Category",
                [
                    "Bitumen",
                    "Modified Bitumen",
                    "Emulsion",
                    "Other"
                ]
            )

        with col2:

            unit = st.selectbox(
                "Unit",
                [
                    "MT",
                    "KG",
                    "Litre",
                    "Drum",
                    "Other"
                ]
            )

            description = st.text_area(
                "Product Description"
            )

        add_submitted = st.form_submit_button(
            "Add Product",
            width="stretch"
        )

    if add_submitted:

        if len(product_name.strip()) < 2:

            st.error(
                "Product name must contain at least 2 characters."
            )

        else:

            product_data = {
                "product_name": product_name.strip(),
                "grade": grade.strip() or None,
                "category": category,
                "unit": unit,
                "description": description.strip() or None
            }

            result = api_write(
                "/products/",
                method="POST",
                data=product_data
            )

            if result is not None:

                st.session_state["product_flash"] = (
                    f"Product '{result.get('product_name', product_name)}' "
                    "added successfully."
                )

                st.rerun()

    st.divider()

    # ----------------------------------------------
    # PRODUCT DATABASE
    # ----------------------------------------------

    st.markdown("### Product Database")

    if products:

        product_df = pd.DataFrame(products)

        # Search products
        search_term = st.text_input(
            "Search by product name, grade or category",
            key="product_search"
        )

        if search_term.strip():

            searchable_columns = [
                "product_name",
                "grade",
                "category"
            ]

            mask = pd.Series(
                False,
                index=product_df.index
            )

            for column in searchable_columns:

                if column in product_df.columns:

                    mask |= (
                        product_df[column]
                        .fillna("")
                        .astype(str)
                        .str.contains(
                            search_term.strip(),
                            case=False,
                            regex=False
                        )
                    )

            filtered_df = product_df[mask]

        else:

            filtered_df = product_df

        st.dataframe(
            filtered_df,
            width="stretch",
            hide_index=True
        )

        active_count = sum(
            1 for product in products
            if product["is_active"]
        )

        inactive_count = len(products) - active_count

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Products",
            len(products)
        )

        col2.metric(
            "Active Products",
            active_count
        )

        col3.metric(
            "Inactive Products",
            inactive_count
        )

        st.caption(
            f"Showing {len(filtered_df)} of {len(products)} products."
        )

    else:

        st.info(
            "No products registered yet. Add your first product above."
        )

    st.divider()

    # ----------------------------------------------
    # EDIT / ACTIVATE / DEACTIVATE PRODUCT
    # ----------------------------------------------

    st.markdown("### Update Product Information")

    if products:

        product_options = {
            f"{product['product_name']} (ID: {product['id']})":
            product
            for product in products
        }

        selected_label = st.selectbox(
            "Select Product",
            list(product_options.keys()),
            key="selected_product_management"
        )

        selected_product = product_options[selected_label]

        product_id = selected_product["id"]

        with st.form(
            f"update_product_form_{product_id}"
        ):

            st.markdown(
                f"**Editing Product ID: {product_id}**"
            )

            col1, col2 = st.columns(2)

            with col1:

                edit_product_name = st.text_input(
                    "Product Name",
                    value=selected_product["product_name"] or "",
                    key=f"product_name_{product_id}"
                )

                edit_grade = st.text_input(
                    "Grade",
                    value=selected_product.get("grade") or "",
                    key=f"product_grade_{product_id}"
                )

                categories = [
                    "Bitumen",
                    "Modified Bitumen",
                    "Emulsion",
                    "Other"
                ]

                existing_category = (
                    selected_product.get("category") or "Other"
                )

                if existing_category not in categories:
                    categories.append(existing_category)

                edit_category = st.selectbox(
                    "Product Category",
                    categories,
                    index=categories.index(existing_category),
                    key=f"product_category_{product_id}"
                )

            with col2:

                units = [
                    "MT",
                    "KG",
                    "Litre",
                    "Drum",
                    "Other"
                ]

                existing_unit = (
                    selected_product.get("unit") or "MT"
                )

                if existing_unit not in units:
                    units.append(existing_unit)

                edit_unit = st.selectbox(
                    "Unit",
                    units,
                    index=units.index(existing_unit),
                    key=f"product_unit_{product_id}"
                )

                edit_description = st.text_area(
                    "Product Description",
                    value=selected_product.get("description") or "",
                    key=f"product_description_{product_id}"
                )

                edit_active = st.checkbox(
                    "Product is active",
                    value=bool(selected_product["is_active"]),
                    key=f"product_active_{product_id}"
                )

            update_submitted = st.form_submit_button(
                "Save Changes",
                width="stretch"
            )

        if update_submitted:

            if len(edit_product_name.strip()) < 2:

                st.error(
                    "Product name must contain at least 2 characters."
                )

            else:

                updated_data = {
                    "product_name": edit_product_name.strip(),
                    "grade": edit_grade.strip() or None,
                    "category": edit_category,
                    "unit": edit_unit,
                    "description": edit_description.strip() or None,
                    "is_active": edit_active
                }

                result = api_write(
                    f"/products/{product_id}",
                    method="PUT",
                    data=updated_data
                )

                if result is not None:

                    st.session_state["product_flash"] = (
                        f"Product '{edit_product_name}' "
                        "updated successfully."
                    )

                    st.rerun()

    else:

        st.info(
            "Add a product first to enable product editing."
        )

    st.divider()

    st.caption(
        "PPS Bitumen Intelligence | Demonstration Prototype | "
        "Data stored locally in SQLite"
    )


# ==================================================
# 10. SUPPLIER RATE MANAGEMENT PAGE
# ==================================================

elif page == "Supplier Rate Management":

    st.subheader("Supplier Rate Management")

    st.write(
        "Record supplier-wise bitumen rates, view historical "
        "prices and filter rates by supplier, product and date."
    )

    # ----------------------------------------------
    # SUCCESS MESSAGE
    # ----------------------------------------------

    flash = st.session_state.pop(
        "rate_flash",
        None
    )

    if flash:
        st.success(flash)

    # ----------------------------------------------
    # FETCH SUPPLIERS AND PRODUCTS
    # ----------------------------------------------

    suppliers = api_get("/suppliers/")
    products = api_get("/products/")

    if suppliers is None or products is None:
        st.stop()

    active_suppliers = [
        supplier for supplier in suppliers
        if supplier.get("is_active", False)
    ]

    active_products = [
        product for product in products
        if product.get("is_active", False)
    ]

    # ----------------------------------------------
    # ADD NEW SUPPLIER RATE
    # ----------------------------------------------

    st.markdown("### Add New Supplier Rate")

    if not active_suppliers:
        st.warning(
            "No active suppliers available. "
            "Add or activate a supplier first."
        )

    elif not active_products:
        st.warning(
            "No active products available. "
            "Add or activate a product first."
        )

    else:

        supplier_options = {
            f"{supplier['company_name']} (ID: {supplier['id']})":
            supplier
            for supplier in active_suppliers
        }

        product_options = {
            (
                f"{product['product_name']} "
                f"{' - ' + product['grade'] if product.get('grade') else ''} "
                f"(ID: {product['id']})"
            ): product
            for product in active_products
        }

        with st.form(
            "add_supplier_rate_form",
            clear_on_submit=True
        ):

            col1, col2 = st.columns(2)

            with col1:

                selected_supplier_label = st.selectbox(
                    "Select Supplier *",
                    list(supplier_options.keys())
                )

                selected_product_label = st.selectbox(
                    "Select Product *",
                    list(product_options.keys())
                )

                rate = st.number_input(
                    "Rate (₹) *",
                    min_value=0.01,
                    value=48500.0,
                    step=100.0,
                    format="%.2f"
                )

                unit_options = [
                    "MT",
                    "KG",
                    "Litre",
                    "Drum",
                    "Other"
                ]

                selected_product = product_options[
                    selected_product_label
                ]

                product_unit = selected_product.get("unit") or "MT"

                if product_unit not in unit_options:
                    unit_options.append(product_unit)

                unit = st.selectbox(
                    "Rate Unit",
                    unit_options,
                    index=unit_options.index(product_unit)
                )

            with col2:

                effective_date = st.date_input(
                    "Effective Date *",
                    value=date.today(),
                    key="new_rate_effective_date"
                )

                valid_until = st.date_input(
                    "Valid Until (Optional)",
                    value=None,
                    min_value=effective_date,
                    key="new_rate_valid_until"
                )

                source = st.text_input(
                    "Rate Source",
                    placeholder="Example: Supplier quotation"
                )

                notes = st.text_area(
                    "Additional Notes",
                    placeholder="Enter any relevant rate details..."
                )

            submitted = st.form_submit_button(
                "Save Supplier Rate",
                width="stretch"
            )

        if submitted:

            if rate <= 0:

                st.error("Rate must be greater than zero.")

            elif valid_until and valid_until < effective_date:

                st.error(
                    "Valid-until date cannot be earlier "
                    "than the effective date."
                )

            else:

                selected_supplier = supplier_options[
                    selected_supplier_label
                ]

                selected_product = product_options[
                    selected_product_label
                ]

                rate_data = {
                    "supplier_id": selected_supplier["id"],
                    "product_id": selected_product["id"],
                    "rate": rate,
                    "unit": unit,
                    "effective_date": effective_date.isoformat(),
                    "valid_until": (
                        valid_until.isoformat()
                        if valid_until else None
                    ),
                    "source": source.strip() or None,
                    "notes": notes.strip() or None
                }

                result = api_write(
                    "/supplier-rates/",
                    method="POST",
                    data=rate_data
                )

                if result is not None:

                    st.session_state["rate_flash"] = (
                        f"Rate ₹{rate:,.2f}/{unit} recorded successfully "
                        f"for {selected_supplier['company_name']}."
                    )

                    st.rerun()

    st.divider()

    # ----------------------------------------------
    # RATE DATABASE
    # ----------------------------------------------

    st.markdown("### Supplier Rate Database")

    col1, col2 = st.columns(2)

    with col1:

        filter_supplier_options = {
            "All Suppliers": None
        }

        filter_supplier_options.update({
            f"{supplier['company_name']} (ID: {supplier['id']})":
            supplier["id"]
            for supplier in suppliers
        })

        selected_supplier_filter = st.selectbox(
            "Filter by Supplier",
            list(filter_supplier_options.keys()),
            key="rate_supplier_filter"
        )

    with col2:

        filter_product_options = {
            "All Products": None
        }

        filter_product_options.update({
            f"{product['product_name']} "
            f"(ID: {product['id']})":
            product["id"]
            for product in products
        })

        selected_product_filter = st.selectbox(
            "Filter by Product",
            list(filter_product_options.keys()),
            key="rate_product_filter"
        )

    use_date_filter = st.checkbox(
        "Show rates valid on a specific date",
        key="use_rate_date_filter"
    )

    params = {}

    supplier_filter_id = filter_supplier_options[
        selected_supplier_filter
    ]

    product_filter_id = filter_product_options[
        selected_product_filter
    ]

    if supplier_filter_id is not None:
        params["supplier_id"] = supplier_filter_id

    if product_filter_id is not None:
        params["product_id"] = product_filter_id

    if use_date_filter:

        filter_date = st.date_input(
            "Select Date",
            value=date.today(),
            key="rate_filter_date"
        )

        params["effective_on"] = filter_date.isoformat()

    rate_records = api_get(
        "/supplier-rates/",
        params=params
    )

    if rate_records is None:
        st.stop()

    # ----------------------------------------------
    # RATE HISTORY TABLE
    # ----------------------------------------------

    if rate_records:

        supplier_lookup = {
            supplier["id"]: supplier["company_name"]
            for supplier in suppliers
        }

        product_lookup = {
            product["id"]: (
                product["product_name"]
                + (
                    f" ({product['grade']})"
                    if product.get("grade") else ""
                )
            )
            for product in products
        }

        display_records = []

        for record in rate_records:

            display_records.append({
                "Rate ID": record["id"],
                "Supplier": supplier_lookup.get(
                    record["supplier_id"],
                    f"Supplier ID {record['supplier_id']}"
                ),
                "Product": product_lookup.get(
                    record["product_id"],
                    f"Product ID {record['product_id']}"
                ),
                "Rate (₹)": record["rate"],
                "Unit": record["unit"],
                "Effective Date": record["effective_date"],
                "Valid Until": record["valid_until"] or "No expiry",
                "Source": record["source"] or "-",
                "Notes": record["notes"] or "-"
            })

        rate_df = pd.DataFrame(display_records)

        # ------------------------------------------
        # SUMMARY METRICS
        # ------------------------------------------

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Rate Records",
            len(rate_records)
        )

        col2.metric(
            "Lowest Listed Rate",
            f"₹{rate_df['Rate (₹)'].min():,.2f}"
        )

        col3.metric(
            "Highest Listed Rate",
            f"₹{rate_df['Rate (₹)'].max():,.2f}"
        )

        st.dataframe(
            rate_df,
            width="stretch",
            hide_index=True
        )

        st.caption(
            f"Showing {len(rate_records)} supplier rate records. "
            "Historical records are retained."
        )

    else:

        st.info(
            "No supplier rate records found for the selected filters."
        )

    st.divider()

    st.caption(
        "PPS Bitumen Intelligence | Demonstration Prototype | "
        "Rate history stored locally in SQLite"
    )


# ==================================================
# 11. REPORT ARCHIVE PAGE
# ==================================================

elif page == "Report Archive":

    st.subheader("Market Intelligence Report Archive")

    st.write(
        "View, filter and download previously generated "
        "daily market intelligence PDF reports."
    )

    st.divider()

    # ----------------------------------------------
    # FETCH PRODUCTS
    # ----------------------------------------------

    products = api_get("/products/")

    if products is None:
        st.stop()

    # ----------------------------------------------
    # REPORT FILTERS
    # ----------------------------------------------

    st.markdown("### Filter Archived Reports")

    product_options = {
        "All Products": None
    }

    product_options.update({
        (
            f"{product['product_name']} "
            f"(ID: {product['id']})"
        ): product["id"]
        for product in products
    })

    col1, col2 = st.columns(2)

    with col1:

        selected_product = st.selectbox(
            "Filter by Product",
            list(product_options.keys()),
            key="archive_product_filter"
        )

    with col2:

        enable_date_filter = st.checkbox(
            "Filter by report date",
            key="archive_enable_date_filter"
        )

    archive_params = {}

    selected_product_id = product_options[
        selected_product
    ]

    if selected_product_id is not None:

        archive_params["product_id"] = selected_product_id

    if enable_date_filter:

        date_col1, date_col2 = st.columns(2)

        with date_col1:

            archive_start_date = st.date_input(
                "Start Date",
                value=date.today() - timedelta(days=30),
                key="archive_start_date"
            )

        with date_col2:

            archive_end_date = st.date_input(
                "End Date",
                value=date.today(),
                key="archive_end_date"
            )

        if archive_start_date > archive_end_date:

            st.warning(
                "Start date cannot be later than end date."
            )

            st.stop()

        archive_params["start_date"] = (
            archive_start_date.isoformat()
        )

        archive_params["end_date"] = (
            archive_end_date.isoformat()
        )

    # ----------------------------------------------
    # FETCH ARCHIVED REPORTS
    # ----------------------------------------------

    st.divider()

    st.markdown("### Archived Reports")

    archive_data = api_get(
        "/reports/archive/",
        params=archive_params
    )

    if archive_data is None:
        st.stop()

    archived_reports = archive_data.get(
        "reports",
        []
    )

    total_reports = archive_data.get(
        "total_reports",
        len(archived_reports)
    )

    # ----------------------------------------------
    # SUMMARY
    # ----------------------------------------------

    col1, col2 = st.columns(2)

    col1.metric(
        "Total Archived Reports",
        total_reports
    )

    col2.metric(
        "Products Covered",
        len({
            report["product_id"]
            for report in archived_reports
        })
    )

    st.divider()

    # ----------------------------------------------
    # REPORT LIST
    # ----------------------------------------------

    if archived_reports:

        product_lookup = {
            product["id"]: product["product_name"]
            for product in products
        }

        archive_df = pd.DataFrame([
            {
                "Report Date": report["report_date"],
                "Product": product_lookup.get(
                    report["product_id"],
                    f"Product {report['product_id']}"
                ),
                "Product ID": report["product_id"],
                "File Size (KB)": report["file_size_kb"],
                "Filename": report["filename"]
            }
            for report in archived_reports
        ])

        st.dataframe(
            archive_df.drop(columns=["Filename"]),
            width="stretch",
            hide_index=True
        )

        st.markdown("### Download Reports")

        for index, report in enumerate(archived_reports):

            product_name = product_lookup.get(
                report["product_id"],
                f"Product {report['product_id']}"
            )

            with st.container(border=True):

                col1, col2 = st.columns(
                    [3, 1],
                    vertical_alignment="center"
                )

                with col1:

                    st.markdown(
                        f"**{product_name} – "
                        f"{report['report_date']}**"
                    )

                    st.caption(
                        f"{report['filename']} | "
                        f"{report['file_size_kb']} KB"
                    )

                with col2:

                    if st.button(
                        "Download PDF",
                        key=f"archive_download_{index}",
                        width="stretch"
                    ):

                        with st.spinner(
                            "Downloading report..."
                        ):

                            pdf_data = api_download(
                                "/reports/archive/download/"
                                + report["filename"]
                            )

                        if pdf_data:

                            st.download_button(
                                label="Save PDF",
                                data=pdf_data,
                                file_name=report["filename"],
                                mime="application/pdf",
                                key=f"archive_save_{index}",
                                width="stretch"
                            )

    else:

        st.info(
            "No archived reports found for the selected filters."
        )

    st.divider()

    st.caption(
        "PPS Bitumen Intelligence | Report Archive | "
        "PDF reports stored locally"
    )




