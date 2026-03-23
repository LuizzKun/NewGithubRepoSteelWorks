"""
Streamlit User Interface for SteelWorks Operations Reporting.

This module provides an interactive web interface for operations team to:
1. View production line quality metrics
2. Analyze defect trends over time
3. Review shipment status by lot
4. Drill down into specific lots for detailed cross-departmental data

Architecture:
    - Streamlit framework for reactive UI
    - Session service for business logic
    - Multi-page/section layout with sidebar navigation

Time Complexity: O(n) queries with caching
Space Complexity: O(m) result rendering

Author: SteelWorks Operations Team
Date: 2024-02-16
"""

import streamlit as st
from datetime import date, timedelta
import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from dotenv import load_dotenv
import sentry_sdk
import logging
import sys

from src.steelworks.models import create_session
from src.steelworks.service import OperationsReportingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("steelworks_app.log"),
    ],
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    send_default_pii=False,
    traces_sample_rate=0.0,
    enable_logs=False,
)
logger.info("Application starting - SteelWorks Operations Reporting Tool")
logger.info(f"Environment loaded from: {env_path}")

# ===== Page Configuration =====

st.set_page_config(
    page_title="SteelWorks Operations Reporting",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏭 SteelWorks Operations Reporting Tool")
st.markdown("Review production, quality (QE), and shipment information by lot and date")

# ===== Initialize Session Service =====


def get_service() -> OperationsReportingService:
    """
    Create a fresh service instance with new database session for each page render.

    This ensures failed transactions don't persist across page interactions.

    Time Complexity: O(1) DB connection
    Space Complexity: O(1) service instance
    """
    try:
        logger.info("Initializing database service for page render")
        session = create_session()
        return OperationsReportingService(session)
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        st.error(f"Failed to connect to database: {e}")
        st.stop()


service = get_service()

# ===== Sidebar Navigation =====

st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Select Report:",
    [
        "Dashboard (Overview)",
        "Production Line Quality",
        "Defect Trends",
        "Shipment Status",
        "Lot Details (Drill-down)",
        "Production Summary",
    ],
)
logger.info(f"User navigated to page: {page}")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**About**: This tool aggregates production, inspection (QE), "
    "and shipment data to answer operations questions without manual Excel work."
)

# ===== Common Date Range Selection =====

st.sidebar.markdown("### Date Range Filter")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=date.today() - timedelta(days=30),
        key="start_date",
    )
with col2:
    end_date = st.date_input(
        "End Date",
        value=date.today(),
        key="end_date",
    )

if start_date > end_date:
    st.error("Start date must be before end date!")
    st.stop()

# ===== Page 1: Dashboard (Overview) =====

if page == "Dashboard (Overview)":
    st.header("📈 Operations Dashboard")

    st.write(f"Summary view of operations metrics for {start_date} to {end_date}")

    try:
        # AC 1: Top production lines with defects
        st.subheader("🚨 Production Lines with Most Defects")
        lines_data = service.get_lines_with_most_defects(start_date, end_date)

        if lines_data:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write("**Line Quality Issues Summary**")
                for line_code, defect_count in lines_data:
                    st.metric(f"Line: {line_code}", f"{int(defect_count)} defects")
            with col2:
                st.write("")
                st.write("Lines sorted by defect count (descending)")
        else:
            st.info("No defect data available for selected date range.")

        st.markdown("---")

        # AC 2: Defect trend
        st.subheader("📉 Defect Trend (Last 30 Days)")

        trend_data = service.get_defect_trend_over_time(start_date, end_date)

        if trend_data:
            dates = [d["date"] for d in trend_data]
            counts = [d["total_defects"] for d in trend_data]

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(
                dates, counts, marker="o", linewidth=2, markersize=6, color="#FF6B6B"
            )
            ax.fill_between(dates, counts, alpha=0.3, color="#FF6B6B")
            ax.set_xlabel("Date")
            ax.set_ylabel("Total Defects")
            ax.set_title("Daily Defect Count")
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        else:
            st.info("No trend data available.")

        st.markdown("---")

        # Shipment Status
        st.subheader("📦 Shipment Status")
        shipped = service.get_shipped_lots()
        pending = service.get_pending_shipments()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Lots Shipped", len(shipped))
        with col2:
            st.metric("Lots Pending", len(pending))

    except Exception as e:
        service.session.rollback()
        st.error(f"Error loading dashboard: {str(e)}")

# ===== Page 2: Production Line Quality =====

elif page == "Production Line Quality":
    st.header("📊 Production Line Quality Analysis")

    st.write(
        "AC 1: Identify which production lines had the most defects in the selected period."
    )

    try:
        lines_data = service.get_lines_with_most_defects(start_date, end_date)

        if lines_data:
            # Display as table
            st.subheader("Defect Count by Production Line")

            table_data = []
            for line_code, defect_count in lines_data:
                table_data.append(
                    {"Production Line": line_code, "Total Defects": int(defect_count)}
                )

            st.dataframe(table_data, use_container_width=True, hide_index=True)

            # Bar chart
            st.subheader("Visual Comparison")
            df = pd.DataFrame(table_data)
            st.bar_chart(df.set_index("Production Line"))
        else:
            st.info("No data available for the selected date range.")

    except Exception as e:
        st.error(f"Error loading production line quality: {str(e)}")

# ===== Page 3: Defect Trends =====

elif page == "Defect Trends":
    st.header("📉 Defect Trend Analysis")

    st.write(
        "AC 2: Identify defect trends over time and AC 3: Aggregate by defect type."
    )

    try:
        # Trend over time
        st.subheader("Daily Defect Trend")
        trend_data = service.get_defect_trend_over_time(start_date, end_date)

        if trend_data:
            df_trend = pd.DataFrame(trend_data)

            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(
                df_trend["date"],
                df_trend["total_defects"],
                marker="o",
                linewidth=2,
                markersize=8,
                color="#FF6B6B",
            )
            ax.fill_between(
                df_trend["date"], df_trend["total_defects"], alpha=0.3, color="#FF6B6B"
            )
            ax.set_xlabel("Date")
            ax.set_ylabel("Defects")
            ax.set_title(f"Daily Defect Count ({start_date} to {end_date})")
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            st.subheader("Detailed Trend Data")
            st.dataframe(df_trend, use_container_width=True, hide_index=True)
        else:
            st.info("No trend data available.")

        st.markdown("---")

        # Defect types
        st.subheader("Defect Types Distribution (AC 3)")
        defect_data = service.get_defects_by_type(start_date, end_date)

        if defect_data:
            df_defects = pd.DataFrame(defect_data)

            # Pie chart
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(df_defects, use_container_width=True, hide_index=True)

            with col2:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.pie(
                    df_defects["total_qty"],
                    labels=df_defects["defect_code"],
                    autopct="%1.1f%%",
                    startangle=90,
                )
                ax.set_title("Defect Distribution")
                st.pyplot(fig)
        else:
            st.info("No defect type data available.")

    except Exception as e:
        st.error(f"Error loading defect trends: {str(e)}")

# ===== Page 4: Shipment Status =====

elif page == "Shipment Status":
    st.header("📦 Shipment Status Review")

    st.write("AC 4: Determine which lots have been shipped and track their status.")

    try:
        shipment_data = service.get_shipped_lots_summary()

        if shipment_data:
            df_shipments = pd.DataFrame(shipment_data)

            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                shipped_count = len(
                    [s for s in shipment_data if s["ship_status"] == "Shipped"]
                )
                st.metric("Shipped Lots", shipped_count)
            with col2:
                pending_count = len(
                    [s for s in shipment_data if s["ship_status"] != "Shipped"]
                )
                st.metric("Pending Shipments", pending_count)
            with col3:
                total_defects = sum(s["total_defects"] for s in shipment_data)
                st.metric("Total Defects", int(total_defects))

            st.markdown("---")

            st.subheader("Shipment Details")
            st.dataframe(df_shipments, use_container_width=True, hide_index=True)
        else:
            st.info("No shipment data available.")

    except Exception as e:
        st.error(f"Error loading shipment status: {str(e)}")

# ===== Page 5: Lot Details (Drill-down) =====

elif page == "Lot Details (Drill-down)":
    st.header("🔍 Lot Details & Cross-Functional Review")

    st.write(
        "AC 5: Drill down into a specific lot to see production, quality, "
        "and shipment data side-by-side."
    )

    try:
        # Get list of all lots for selection
        all_lots_data = service.get_shipped_lots_summary()
        lot_codes = [lot["lot_code"] for lot in all_lots_data]

        selected_lot = st.selectbox(
            "Select a Lot:",
            lot_codes,
            help="Choose a lot to view its full operational history",
        )

        if selected_lot:
            lot_report = service.get_lot_report(selected_lot)

            if lot_report:
                # Production Info
                st.subheader("📦 Production Information")
                if lot_report["production_info"]:
                    prod_df = pd.DataFrame(lot_report["production_info"])
                    st.dataframe(prod_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No production records found.")

                st.markdown("---")

                # Quality Info
                st.subheader("🔬 Quality Inspection Information")
                quality = lot_report["quality_info"]

                col1, col2 = st.columns([2, 1])
                with col1:
                    if quality["defects"]:
                        defects_df = pd.DataFrame(quality["defects"])
                        st.dataframe(
                            defects_df, use_container_width=True, hide_index=True
                        )
                    else:
                        st.info("No defects found (clean lot).")
                with col2:
                    st.metric("Total Defects", quality["total_defects"])

                st.markdown("---")

                # Shipment Info
                st.subheader("📬 Shipment Information")
                shipment = lot_report["shipment_info"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    status_display = {
                        "Shipped": "✅ Shipped",
                        "On Hold": "⏸️ On Hold",
                        "Partial": "📦 Partial",
                        "Backordered": "⏳ Backordered",
                        "Pending": "⏳ Pending",
                    }
                    status = status_display.get(
                        shipment["ship_status"], shipment["ship_status"]
                    )
                    st.metric("Status", status)
                with col2:
                    st.metric(
                        "Ship Date",
                        str(shipment["ship_date"]) if shipment["ship_date"] else "N/A",
                    )
                with col3:
                    st.metric("Days to Ship", shipment["days_to_ship"] or "Pending")
            else:
                st.error(f"Lot {selected_lot} not found in database.")

    except Exception as e:
        st.error(f"Error loading lot details: {str(e)}")

# ===== Page 6: Production Summary =====

elif page == "Production Summary":
    st.header("🏭 Production Summary")

    st.write("AC 6: Aggregate production records by date and line.")

    try:
        production_data = service.get_production_summary(start_date, end_date)

        if production_data:
            df_prod = pd.DataFrame(production_data)

            st.subheader("Production Events")
            st.dataframe(df_prod, use_container_width=True, hide_index=True)

            # Summary stats
            st.subheader("Production Statistics")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Production Events", len(production_data))

            with col2:
                unique_dates = df_prod["date"].nunique()
                st.metric("Production Days", unique_dates)

            with col3:
                unique_lines = df_prod["line_code"].nunique()
                st.metric("Active Lines", unique_lines)

            # Line utilization
            st.subheader("Production by Line")
            line_counts = df_prod["line_code"].value_counts().reset_index()
            line_counts.columns = ["Line", "Count"]
            st.bar_chart(line_counts.set_index("Line"))
        else:
            st.info("No production data available for selected date range.")

    except Exception as e:
        st.error(f"Error loading production summary: {str(e)}")

# ===== Footer =====

st.markdown("---")
st.markdown(
    "**SteelWorks Operations Reporting Tool** | "
    "Data from Production, Quality (QE), and Shipment Departments"
)
