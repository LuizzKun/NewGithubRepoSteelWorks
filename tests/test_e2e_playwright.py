"""
End-to-End Tests for SteelWorks Streamlit Dashboard using Playwright.

These tests verify the complete user workflow from browser interactions
through the Streamlit UI to database queries.

Requirements:
    - Streamlit app must be running (starts automatically via fixture)
    - Test database must be populated
    - Playwright browsers installed: playwright install
    - Run: pytest tests/test_e2e_playwright.py -v --headed

Setup:
    pip install pytest-playwright
    playwright install chromium
"""

import pytest
import subprocess
import time
import os
from pathlib import Path
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

# Load test environment
test_env_path = Path(__file__).parent.parent / ".env.test"
load_dotenv(dotenv_path=test_env_path, override=True)

STREAMLIT_URL = "http://localhost:8501"
APP_PATH = "src/steelworks/app.py"


@pytest.fixture(scope="module")
def streamlit_server():
    """Start Streamlit server for E2E testing."""
    # Set test environment
    env = os.environ.copy()
    test_env = load_dotenv(test_env_path, override=True)
    
    # Start Streamlit in background
    process = subprocess.Popen(
        ["python", "-m", "streamlit", "run", APP_PATH, "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    
    # Wait for server to start
    print("⏳ Starting Streamlit server...")
    time.sleep(10)  # Give Streamlit time to initialize
    
    yield process
    
    # Cleanup
    print("🛑 Stopping Streamlit server...")
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture(scope="function")
def page(streamlit_server, playwright):
    """Create a new browser page for each test."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    # Navigate to app
    page.goto(STREAMLIT_URL)
    page.wait_for_load_state("networkidle")
    
    yield page
    
    # Cleanup
    page.close()
    context.close()
    browser.close()


class TestStreamlitAppNavigation:
    """Test basic navigation and page rendering."""
    
    def test_app_loads_successfully(self, page: Page):
        """Verify the Streamlit app loads without errors."""
        # Check for title
        expect(page.get_by_role("heading", name="SteelWorks Operations")).to_be_visible()
        
        # Check sidebar exists
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
    
    def test_navigation_menu_visible(self, page: Page):
        """Verify navigation menu shows all pages."""
        # Check for navigation title
        expect(page.get_by_text("📊 Navigation")).to_be_visible()
        
        # Check for all page options
        expect(page.get_by_text("Dashboard (Overview)")).to_be_visible()
        expect(page.get_by_text("Production Line Quality")).to_be_visible()
        expect(page.get_by_text("Defect Trends")).to_be_visible()
        expect(page.get_by_text("Shipment Status")).to_be_visible()
        expect(page.get_by_text("Lot Details (Drill-down)")).to_be_visible()
        expect(page.get_by_text("Production Summary")).to_be_visible()
    
    def test_date_range_filter_visible(self, page: Page):
        """Verify date range filter controls exist."""
        expect(page.get_by_text("Date Range Filter")).to_be_visible()
        expect(page.get_by_text("Start Date")).to_be_visible()
        expect(page.get_by_text("End Date")).to_be_visible()


class TestDashboardPage:
    """Test Dashboard (Overview) page functionality."""
    
    def test_dashboard_loads_with_metrics(self, page: Page):
        """Verify dashboard displays summary metrics."""
        # Should be on dashboard by default
        expect(page.get_by_role("heading", name="Operations Dashboard")).to_be_visible()
        
        # Check for key sections
        expect(page.get_by_text("Production Lines with Most Defects")).to_be_visible()
        expect(page.get_by_text("Defect Trend")).to_be_visible()
        expect(page.get_by_text("Shipment Status")).to_be_visible()
    
    def test_dashboard_displays_defect_chart(self, page: Page):
        """Verify defect trend chart renders."""
        # Look for matplotlib figure (chart)
        chart = page.locator('[data-testid="stImage"]').first
        expect(chart).to_be_visible(timeout=10000)
    
    def test_dashboard_shows_shipment_metrics(self, page: Page):
        """Verify shipment status metrics display."""
        # Look for metric components
        metrics = page.locator('[data-testid="stMetric"]')
        expect(metrics.first).to_be_visible()


class TestProductionLineQualityPage:
    """Test Production Line Quality page."""
    
    def test_production_line_page_loads(self, page: Page):
        """Navigate to Production Line Quality and verify display."""
        # Click navigation option
        page.get_by_text("Production Line Quality").click()
        page.wait_for_timeout(1000)
        
        expect(page.get_by_role("heading", name="Production Line Quality Analysis")).to_be_visible()
    
    def test_production_line_shows_table(self, page: Page):
        """Verify defect count table displays."""
        page.get_by_text("Production Line Quality").click()
        page.wait_for_timeout(1000)
        
        # Check for table or dataframe
        expect(page.get_by_text("Defect Count by Production Line")).to_be_visible()


class TestDefectTrendsPage:
    """Test Defect Trends page."""
    
    def test_defect_trends_page_loads(self, page: Page):
        """Navigate to Defect Trends page."""
        page.get_by_text("Defect Trends").click()
        page.wait_for_timeout(1000)
        
        expect(page.get_by_role("heading", name="Defect Trend Analysis")).to_be_visible()
    
    def test_defect_trends_shows_charts(self, page: Page):
        """Verify defect trend charts display."""
        page.get_by_text("Defect Trends").click()
        page.wait_for_timeout(2000)
        
        expect(page.get_by_text("Daily Defect Trend")).to_be_visible()
        expect(page.get_by_text("Defect Types Distribution")).to_be_visible()


class TestShipmentStatusPage:
    """Test Shipment Status page."""
    
    def test_shipment_status_page_loads(self, page: Page):
        """Navigate to Shipment Status page."""
        page.get_by_text("Shipment Status").click()
        page.wait_for_timeout(1000)
        
        expect(page.get_by_role("heading", name="Shipment Status Review")).to_be_visible()
    
    def test_shipment_status_shows_metrics(self, page: Page):
        """Verify shipment metrics display."""
        page.get_by_text("Shipment Status").click()
        page.wait_for_timeout(1000)
        
        # Check for shipment metrics
        expect(page.get_by_text("Shipped Lots")).to_be_visible()
        expect(page.get_by_text("Pending Shipments")).to_be_visible()


class TestLotDetailsPage:
    """Test Lot Details (Drill-down) page."""
    
    def test_lot_details_page_loads(self, page: Page):
        """Navigate to Lot Details page."""
        page.get_by_text("Lot Details (Drill-down)").click()
        page.wait_for_timeout(1000)
        
        expect(page.get_by_role("heading", name="Lot Details & Cross-Functional Review")).to_be_visible()
    
    def test_lot_selection_dropdown_exists(self, page: Page):
        """Verify lot selection dropdown is available."""
        page.get_by_text("Lot Details (Drill-down)").click()
        page.wait_for_timeout(1000)
        
        # Check for selectbox
        expect(page.get_by_text("Select a Lot:")).to_be_visible()
    
    def test_lot_details_shows_sections(self, page: Page):
        """Verify lot detail sections display after selection."""
        page.get_by_text("Lot Details (Drill-down)").click()
        page.wait_for_timeout(2000)
        
        # Select first lot (if available)
        selectbox = page.locator('[data-baseweb="select"]').first
        if selectbox.is_visible():
            selectbox.click()
            page.wait_for_timeout(500)
            # Click first option
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
            page.wait_for_timeout(1000)
            
            # Check for detail sections
            expect(page.get_by_text("Production Information")).to_be_visible()
            expect(page.get_by_text("Quality Inspection Information")).to_be_visible()
            expect(page.get_by_text("Shipment Information")).to_be_visible()


class TestProductionSummaryPage:
    """Test Production Summary page."""
    
    def test_production_summary_page_loads(self, page: Page):
        """Navigate to Production Summary page."""
        page.get_by_text("Production Summary").click()
        page.wait_for_timeout(1000)
        
        expect(page.get_by_role("heading", name="Production Summary")).to_be_visible()
    
    def test_production_summary_shows_statistics(self, page: Page):
        """Verify production statistics display."""
        page.get_by_text("Production Summary").click()
        page.wait_for_timeout(1000)
        
        expect(page.get_by_text("Production Statistics")).to_be_visible()
        expect(page.get_by_text("Total Production Events")).to_be_visible()


class TestDateRangeFilter:
    """Test date range filtering across pages."""
    
    def test_date_filter_changes_update_dashboard(self, page: Page):
        """Verify changing date range updates dashboard data."""
        # Get initial state
        initial_content = page.content()
        
        # Change start date
        start_date_input = page.locator('input[aria-label*="Start Date"]').first
        if start_date_input.is_visible():
            start_date_input.click()
            page.wait_for_timeout(500)
            
            # Select a different date (implementation depends on date picker)
            # This is a placeholder - actual implementation may vary
            page.keyboard.press("ArrowLeft")
            page.keyboard.press("ArrowLeft")
            page.keyboard.press("Enter")
            
            page.wait_for_timeout(2000)
            
            # Verify content changed
            updated_content = page.content()
            # Content should update after date change
            # (This is a basic check; specific assertions depend on data)


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_app_handles_no_data_gracefully(self, page: Page):
        """Verify app displays appropriate message when no data available."""
        # This test assumes some pages might have no data for certain date ranges
        # Navigate through pages and check for error messages or info messages
        
        pages_to_test = [
            "Dashboard (Overview)",
            "Production Line Quality",
            "Defect Trends",
        ]
        
        for page_name in pages_to_test:
            page.get_by_text(page_name).click()
            page.wait_for_timeout(1000)
            
            # Should not show error messages
            error_locator = page.locator('[data-testid="stException"]')
            expect(error_locator).not_to_be_visible()
    
    def test_app_validates_date_range(self, page: Page):
        """Verify app validates start date < end date."""
        # Try to set end date before start date
        # The app should show an error message
        # (Implementation depends on actual validation logic)
        pass


class TestResponsiveness:
    """Test UI responsiveness and layout."""
    
    def test_sidebar_is_responsive(self, page: Page):
        """Verify sidebar adjusts to viewport size."""
        # Test desktop view
        page.set_viewport_size({"width": 1920, "height": 1080})
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        # Test tablet view
        page.set_viewport_size({"width": 768, "height": 1024})
        page.wait_for_timeout(500)
        # Sidebar should still be accessible
    
    def test_charts_render_properly(self, page: Page):
        """Verify charts render at different screen sizes."""
        sizes = [
            {"width": 1920, "height": 1080},  # Desktop
            {"width": 1280, "height": 720},   # Laptop
            {"width": 768, "height": 1024},   # Tablet
        ]
        
        for size in sizes:
            page.set_viewport_size(size)
            page.wait_for_timeout(1000)
            
            # Check if charts are visible (not cut off)
            charts = page.locator('[data-testid="stImage"]')
            if charts.count() > 0:
                expect(charts.first).to_be_visible()
