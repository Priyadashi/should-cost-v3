"""Generate the Should-Cost Modeling Platform User Manual as PDF with screenshots."""

from fpdf import FPDF
from PIL import Image
import os

SCREENSHOTS_DIR = "screenshots"
OUTPUT = "Should-Cost_Platform_User_Manual.pdf"


class ManualPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "Should-Cost Modeling Platform  |  User Manual", align="L")
            self.cell(0, 8, f"Page {self.page_no()}", align="R")
            self.ln(12)

    def footer(self):
        pass

    def chapter_title(self, num, title):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(180, 100, 20)
        self.cell(0, 12, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(220, 160, 60)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(60, 60, 60)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(3)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(40, 40, 40)
        self.cell(0, 5.5, f"  -  {text}", new_x="LMARGIN", new_y="NEXT")

    def add_screenshot(self, path, caption=None):
        if not os.path.exists(path):
            return
        img = Image.open(path)
        w, h = img.size
        # Scale to fit page width with margins
        max_w = self.w - self.l_margin - self.r_margin
        max_h = 140  # max height for screenshot
        ratio = min(max_w / (w / 3.78), max_h / (h / 3.78))  # px to mm approx
        img_w = (w / 3.78) * ratio
        img_h = (h / 3.78) * ratio
        # If won't fit, scale further
        if img_w > max_w:
            scale = max_w / img_w
            img_w *= scale
            img_h *= scale
        if img_h > max_h:
            scale = max_h / img_h
            img_w *= scale
            img_h *= scale
        # Check if we need a new page
        if self.get_y() + img_h + 15 > self.h - 20:
            self.add_page()
        # Center the image
        x = self.l_margin + (max_w - img_w) / 2
        # Add thin border
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.rect(x - 1, self.get_y() - 1, img_w + 2, img_h + 2)
        self.image(path, x=x, y=self.get_y(), w=img_w)
        self.set_y(self.get_y() + img_h + 3)
        if caption:
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, caption, align="C", new_x="LMARGIN", new_y="NEXT")
            self.ln(4)


def build_manual():
    pdf = ManualPDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Cover Page ──
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(180, 100, 20)
    pdf.cell(0, 18, "Should-Cost", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 28)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 14, "Modeling Platform", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_draw_color(220, 160, 60)
    pdf.set_line_width(1.2)
    pdf.line(60, pdf.get_y(), pdf.w - 60, pdf.get_y())
    pdf.ln(12)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 12, "End User Manual", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Version 3.0", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "April 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, "A comprehensive guide for procurement and supply chain professionals", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "to build bottom-up should-cost models for manufactured components.", align="C", new_x="LMARGIN", new_y="NEXT")

    # ── Table of Contents ──
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(180, 100, 20)
    pdf.cell(0, 14, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    toc = [
        ("1", "Introduction", "3"),
        ("2", "Getting Started", "4"),
        ("3", "Dashboard", "5"),
        ("4", "Cost Sheets", "6"),
        ("5", "Cost Sheet Builder", "7"),
        ("6", "Master Data Management", "10"),
        ("7", "Excel Import", "13"),
        ("8", "Settings", "14"),
        ("9", "Tips & Best Practices", "15"),
    ]
    for num, title, page in toc:
        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(10, 8, num + ".")
        pdf.cell(140, 8, title)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 8, page, align="R", new_x="LMARGIN", new_y="NEXT")

    # ── Chapter 1: Introduction ──
    pdf.add_page()
    pdf.chapter_title("1", "Introduction")
    pdf.body_text(
        "The Should-Cost Modeling Platform is a web-based application designed for "
        "procurement professionals, cost engineers, and supply chain teams. It enables "
        "you to build bottom-up cost models for manufactured components and compare them "
        "against supplier-quoted prices to identify savings opportunities."
    )
    pdf.section_title("What is Should-Cost Analysis?")
    pdf.body_text(
        "Should-cost analysis (also called cleansheet costing) estimates what a manufactured "
        "part should cost based on its raw materials, manufacturing processes, labor, overheads, "
        "and profit margins. By building a fact-based cost model, you gain negotiation leverage "
        "and can identify where a supplier's price may include excessive margins or inefficiencies."
    )
    pdf.section_title("Key Capabilities")
    pdf.bullet("Build cost sheets with Bill of Materials (BOM), process routing, and overhead allocation")
    pdf.bullet("Calculate should-cost vs. quoted price to identify cost gaps")
    pdf.bullet("Perform sensitivity analysis on key cost drivers")
    pdf.bullet("Get AI-powered cost reduction recommendations")
    pdf.bullet("Compare multiple cost scenarios side-by-side")
    pdf.bullet("Manage master data: materials, machines, vendors, process templates, overhead profiles")
    pdf.bullet("Bulk import data via Excel upload")
    pdf.ln(3)
    pdf.section_title("Navigation Overview")
    pdf.body_text(
        "The platform uses a left sidebar for navigation, organized into three sections:"
    )
    pdf.bullet("Overview: Dashboard and Cost Sheets list")
    pdf.bullet("Master Data: Materials, Machines, Process Templates, Vendors, Overhead Profiles")
    pdf.bullet("Tools: Excel Import and Settings")

    # ── Chapter 2: Getting Started ──
    pdf.add_page()
    pdf.chapter_title("2", "Getting Started")
    pdf.section_title("System Requirements")
    pdf.bullet("Modern web browser (Chrome, Firefox, Edge, or Safari)")
    pdf.bullet("Screen resolution of 1280x720 or higher recommended")
    pdf.bullet("Active network connection to the application server")
    pdf.ln(3)
    pdf.section_title("Logging In")
    pdf.body_text(
        "Open your web browser and navigate to the application URL provided by your administrator. "
        "The platform will load directly to the Dashboard. User authentication is managed by your "
        "organization's identity provider."
    )
    pdf.section_title("First-Time Setup Checklist")
    pdf.body_text("Before creating your first cost sheet, ensure the following master data is configured:")
    pdf.bullet("Materials: At least one raw material with grade, type, and price per kg")
    pdf.bullet("Machines: Manufacturing machines with hourly rates and power consumption")
    pdf.bullet("Overhead Profiles: Cost allocation percentages for factory overhead, profit margin, etc.")
    pdf.bullet("(Optional) Process Templates: Reusable manufacturing operation definitions")
    pdf.bullet("(Optional) Vendors: Supplier records with capabilities and certifications")

    # ── Chapter 3: Dashboard ──
    pdf.add_page()
    pdf.chapter_title("3", "Dashboard")
    pdf.body_text(
        "The Dashboard is your landing page and provides an at-a-glance overview of the platform's status."
    )
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/01-dashboard.png", "Figure 3.1 - Dashboard overview")
    pdf.section_title("KPI Cards")
    pdf.body_text("Four summary cards are displayed at the top:")
    pdf.bullet("Cost Sheets: Total number of cost sheets, with calculated and draft counts")
    pdf.bullet("Parts: Total number of parts registered in the system")
    pdf.bullet("Materials: Total number of raw materials in the master data")
    pdf.bullet("Annual Opportunity: Sum of identified cost savings across all calculated cost sheets")
    pdf.ln(3)
    pdf.section_title("Quick Actions")
    pdf.body_text("Three action buttons provide shortcuts to common tasks:")
    pdf.bullet("+ New Cost Sheet: Opens the Cost Sheet Builder to create a new analysis")
    pdf.bullet("Import Excel: Navigates to the Excel Import page for bulk data upload")
    pdf.bullet("View All Sheets: Opens the Cost Sheets list page")
    pdf.ln(3)
    pdf.section_title("Recent Activity")
    pdf.body_text(
        "A chronological feed shows the latest actions performed in the system, such as "
        "cost sheets created, calculated, or updated. Click 'View all' to see the full activity history."
    )

    # ── Chapter 4: Cost Sheets ──
    pdf.add_page()
    pdf.chapter_title("4", "Cost Sheets")
    pdf.body_text(
        "The Cost Sheets page displays all cost analyses in a searchable, sortable table."
    )
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/02-cost-sheets-list.png", "Figure 4.1 - Cost Sheets list view")
    pdf.section_title("Table Columns")
    pdf.bullet("Scenario: The name of the cost scenario (e.g., 'Base Scenario', 'Optimized')")
    pdf.bullet("Part Name / Part No.: The component being analyzed")
    pdf.bullet("Status: Draft (not yet calculated), Calculated, or Approved")
    pdf.bullet("Should Cost: The calculated should-cost value per unit")
    pdf.bullet("Gap %: Percentage difference between should-cost and the supplier's quoted price")
    pdf.bullet("Calculated: Date when the cost sheet was last calculated")
    pdf.bullet("Actions: Edit or delete the cost sheet")
    pdf.ln(3)
    pdf.section_title("Creating a New Cost Sheet")
    pdf.body_text(
        "Click the '+ New Cost Sheet' button in the top right corner to open the Cost Sheet Builder. "
        "This takes you to a guided form where you define the part, materials, processes, and overheads."
    )

    # ── Chapter 5: Cost Sheet Builder ──
    pdf.add_page()
    pdf.chapter_title("5", "Cost Sheet Builder")
    pdf.body_text(
        "The Cost Sheet Builder is the core of the platform. It guides you through defining a "
        "bottom-up cost model for a manufactured component in three tabs: Raw Material, "
        "Process Routing, and Overheads."
    )
    pdf.section_title("Part Information Header")
    pdf.body_text("At the top, enter the part details:")
    pdf.bullet("Part Name: Descriptive name of the component (e.g., 'Connecting Rod')")
    pdf.bullet("Part Number: Unique identifier (e.g., 'CR-2024-001')")
    pdf.bullet("Annual Volume: Expected annual production quantity")
    pdf.bullet("Commodity: Type of manufacturing (Forging, Casting, or Fabrication)")
    pdf.bullet("Quoted Price: The supplier's quoted price per unit for comparison")
    pdf.ln(3)

    pdf.section_title("Tab 1: Raw Material (BOM)")
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/03-cost-sheet-builder.png", "Figure 5.1 - Raw Material tab")
    pdf.body_text("Define the bill of materials for the part:")
    pdf.bullet("Material Grade: Select from the materials master data (shows grade and price/kg)")
    pdf.bullet("Gross Weight (kg): Total weight of raw material input (before machining/scrap)")
    pdf.bullet("Net Weight (kg): Finished part weight (gross weight minus scrap)")
    pdf.body_text(
        "Click '+ Add Material' to add additional material lines if the part uses multiple materials. "
        "The system automatically calculates material cost including scrap credit recovery."
    )

    pdf.add_page()
    pdf.section_title("Tab 2: Process Routing")
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/04-process-routing-tab.png", "Figure 5.2 - Process Routing tab")
    pdf.body_text("Define the manufacturing steps required to produce the part:")
    pdf.bullet("Click '+ Add Process Step' to add each manufacturing operation")
    pdf.bullet("For each step, specify: operation name, machine, cycle time, setup time, labor rate, batch size, number of operators, and any tooling cost")
    pdf.body_text(
        "The system calculates machine cost and labor cost per piece for each process step. "
        "You can reorder steps and use process templates to quickly populate standard operations."
    )

    pdf.section_title("Tab 3: Overheads")
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/05-overheads-tab.png", "Figure 5.3 - Overheads tab")
    pdf.body_text("Select an overhead profile to apply cost allocation percentages:")
    pdf.bullet("Factory Overhead: Indirect manufacturing costs (maintenance, utilities, supervision)")
    pdf.bullet("Admin Overhead: General & administrative costs")
    pdf.bullet("Depreciation: Equipment depreciation allocation")
    pdf.bullet("Quality Cost: Inspection, testing, and quality assurance")
    pdf.bullet("Profit Margin: Supplier's expected profit percentage")
    pdf.bullet("Taxes & Duties: Applicable taxes and import duties")
    pdf.bullet("SGA: Selling, general, and administrative expenses")
    pdf.bullet("Packaging/Unit: Fixed packaging cost per unit")
    pdf.bullet("Freight/Unit: Fixed freight/logistics cost per unit")
    pdf.body_text(
        "Enter a Scenario Name (e.g., 'Base Scenario') to label this particular cost analysis."
    )

    pdf.section_title("Live Cost Preview")
    pdf.body_text(
        "On the right side of the builder, a Live Cost Preview panel shows real-time totals as you "
        "enter data. It breaks down: Raw Material cost, Process Cost, Overhead, and Estimated Total. "
        "This helps you validate inputs before running the full calculation."
    )

    pdf.section_title("Calculating Results")
    pdf.body_text(
        "Click the 'Calculate' button (top right) or 'Calculate & View Results' to run the "
        "cost engine. The system will compute the full should-cost breakdown including:\n"
        "- Summary KPI cards (should-cost, quoted price, gap, annual opportunity)\n"
        "- Waterfall chart showing cost buildup from material to final price\n"
        "- Donut chart showing cost category split percentages\n"
        "- Detailed line item table with confidence scores\n"
        "- Sensitivity analysis (tornado chart) showing impact of +/-10% changes\n"
        "- Volume-price curve analysis\n"
        "- AI-powered cost reduction recommendations"
    )

    # ── Chapter 6: Master Data ──
    pdf.add_page()
    pdf.chapter_title("6", "Master Data Management")
    pdf.body_text(
        "Master data forms the foundation of accurate cost modeling. The platform provides "
        "dedicated management pages for each data type, all accessible from the sidebar "
        "under 'Master Data'."
    )

    pdf.section_title("6.1 Materials")
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/06-materials.png", "Figure 6.1 - Materials master data")
    pdf.body_text("The Materials page manages raw material definitions used in cost sheets:")
    pdf.bullet("Grade: Material grade designation (e.g., EN8, SS304, ADC12)")
    pdf.bullet("Type: Material category (Steel, Aluminum, Cast Iron, etc.)")
    pdf.bullet("Rate/kg: Current market price per kilogram in the selected currency")
    pdf.bullet("Currency: Pricing currency (e.g., INR)")
    pdf.bullet("Scrap Recovery: Percentage of scrap value that can be recovered/resold")
    pdf.bullet("Region: Geographic region for the pricing data")
    pdf.body_text(
        "Click '+ Add Material' to create a new entry. Use the edit (pencil) icon to modify "
        "existing records or the delete (trash) icon to remove them. A search bar at the top "
        "allows quick filtering."
    )

    pdf.add_page()
    pdf.section_title("6.2 Machines")
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/07-machines.png", "Figure 6.2 - Machines master data")
    pdf.body_text("The Machines page defines manufacturing equipment and their cost rates:")
    pdf.bullet("Name: Descriptive machine name (e.g., 'CNC Machining Center')")
    pdf.bullet("Type: Machine category (CNC, Press, Welding, Lathe, Furnace, etc.)")
    pdf.bullet("Hourly Rate: Machine operating cost per hour (includes depreciation, power, maintenance)")
    pdf.bullet("Power (kW): Electrical power consumption in kilowatts")
    pdf.bullet("Commodities: Which commodity types this machine is applicable to (Forging, Casting, Fabrication)")

    pdf.section_title("6.3 Process Templates")
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/08-process-templates.png", "Figure 6.3 - Process Templates")
    pdf.body_text(
        "Process Templates are reusable manufacturing operation definitions that speed up "
        "cost sheet creation. Instead of entering process details manually each time, select "
        "a template to auto-fill the operation parameters."
    )
    pdf.bullet("Name: Operation name (e.g., 'Billet Cutting', 'Forging Press', 'Heat Treatment')")
    pdf.bullet("Commodity: The commodity type this template applies to")
    pdf.bullet("Sequence: Suggested order in the manufacturing routing")
    pdf.bullet("Cycle Time: Time per piece for the operation")
    pdf.bullet("Setup Time: One-time setup time per batch")
    pdf.bullet("Labor Rate/Hr: Operator labor cost for this operation")
    pdf.body_text("Use the Commodity Filter dropdown to view templates for a specific commodity type.")

    pdf.add_page()
    pdf.section_title("6.4 Vendors")
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/09-vendors.png", "Figure 6.4 - Vendors master data")
    pdf.body_text("The Vendors page stores supplier information for reference and tracking:")
    pdf.bullet("Name: Company name")
    pdf.bullet("Code: Short identifier code")
    pdf.bullet("Location: Manufacturing location (city, country)")
    pdf.bullet("Capabilities: Manufacturing processes the vendor can perform (tags)")
    pdf.bullet("Certifications: Quality certifications held (ISO 9001, IATF 16949, AS9100, etc.)")
    pdf.bullet("Email: Primary contact email")

    pdf.section_title("6.5 Overhead Profiles")
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/10-overhead-profiles.png", "Figure 6.5 - Overhead Profiles")
    pdf.body_text(
        "Overhead Profiles define reusable sets of cost allocation percentages. One profile "
        "is marked as 'Default' and is automatically selected when creating new cost sheets."
    )
    pdf.bullet("Factory OH: Factory overhead percentage applied to conversion cost")
    pdf.bullet("Admin OH: Administrative overhead percentage")
    pdf.bullet("Profit: Supplier profit margin percentage")
    pdf.bullet("SGA: Selling, general & administrative percentage")
    pdf.bullet("Packaging/Unit: Fixed packaging cost per unit (in currency)")
    pdf.bullet("Freight/Unit: Fixed freight/logistics cost per unit (in currency)")
    pdf.body_text(
        "Create multiple profiles to model different scenarios (e.g., 'India - Standard Forging' vs. "
        "'India - Premium / Automotive') and quickly switch between them in the Cost Sheet Builder."
    )

    # ── Chapter 7: Excel Import ──
    pdf.add_page()
    pdf.chapter_title("7", "Excel Import")
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/11-excel-import.png", "Figure 7.1 - Excel Import page")
    pdf.body_text(
        "The Excel Import feature allows you to bulk-upload cost data from spreadsheets. "
        "This is useful for migrating existing cost data or importing multiple parts at once."
    )
    pdf.section_title("How to Import")
    pdf.bullet("Drag and drop an .xlsx or .xls file onto the upload area, or click to browse")
    pdf.bullet("The system validates the file structure and data against expected columns")
    pdf.bullet("Valid records are imported; errors are reported with row-level details")
    pdf.ln(2)
    pdf.section_title("Download Template")
    pdf.body_text(
        "Click 'Download .xlsx' to get a pre-formatted Excel template with the correct column "
        "headers and sample data. Use this template to structure your data before uploading."
    )
    pdf.section_title("Supported Data")
    pdf.body_text("The Excel import supports uploading:")
    pdf.bullet("Parts with BOM lines (materials, weights, scrap rates)")
    pdf.bullet("Routing steps (operations, machines, cycle/setup times, labor rates)")
    pdf.bullet("The system performs upsert: existing records are updated, new ones are created")

    # ── Chapter 8: Settings ──
    pdf.add_page()
    pdf.chapter_title("8", "Settings")
    pdf.add_screenshot(f"{SCREENSHOTS_DIR}/12-settings.png", "Figure 8.1 - Settings page")
    pdf.section_title("AI Analysis (OpenAI)")
    pdf.body_text(
        "The platform integrates with OpenAI to provide AI-powered cost reduction recommendations. "
        "The API key is configured server-side via the OPENAI_API_KEY environment variable in the "
        "backend .env file. Contact your system administrator to configure this."
    )
    pdf.section_title("SAP S/4HANA Integration")
    pdf.body_text(
        "A future integration with SAP S/4HANA will enable automatic synchronization of materials, "
        "BOMs, and pricing data. This feature is marked 'Coming Soon'. Configuration fields include "
        "the S/4HANA Base URL, Client ID, and Client Secret."
    )

    # ── Chapter 9: Tips & Best Practices ──
    pdf.add_page()
    pdf.chapter_title("9", "Tips & Best Practices")

    pdf.section_title("Accurate Material Pricing")
    pdf.bullet("Update material rates regularly to reflect current market prices")
    pdf.bullet("Use the correct scrap recovery percentage for each material grade")
    pdf.bullet("Account for both gross and net weight to properly capture material utilization")

    pdf.section_title("Process Routing Accuracy")
    pdf.bullet("Validate cycle times against actual shop floor measurements when possible")
    pdf.bullet("Include all manufacturing steps, even minor ones like deburring or inspection")
    pdf.bullet("Use realistic batch sizes to get accurate setup cost amortization")

    pdf.section_title("Overhead Profiles")
    pdf.bullet("Create separate profiles for different manufacturing regions or quality tiers")
    pdf.bullet("Review and update overhead percentages annually based on actual factory data")
    pdf.bullet("Benchmark your overhead assumptions against industry standards")

    pdf.section_title("Scenario Comparison")
    pdf.bullet("Create multiple scenarios for the same part (e.g., different materials or processes)")
    pdf.bullet("Use the Scenario Comparison feature to identify the most cost-effective approach")
    pdf.bullet("Name scenarios descriptively for easy identification later")

    pdf.section_title("Supplier Negotiations")
    pdf.bullet("Use the should-cost model as a fact-based starting point for price discussions")
    pdf.bullet("Focus on the cost gap percentage to identify areas of potential savings")
    pdf.bullet("Review the AI recommendations for specific, actionable cost reduction ideas")
    pdf.bullet("Share the cost breakdown transparently with strategic suppliers for collaborative improvement")

    pdf.ln(10)
    pdf.set_draw_color(220, 160, 60)
    pdf.set_line_width(0.6)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Should-Cost Modeling Platform v3.0  |  End User Manual  |  April 2026", align="C")

    pdf.output(OUTPUT)
    print(f"Manual generated: {OUTPUT}")


if __name__ == "__main__":
    build_manual()
