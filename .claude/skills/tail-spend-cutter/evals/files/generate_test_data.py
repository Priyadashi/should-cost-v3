"""Generate 3 test CSV files for tail-spend-cutter evals."""
import csv
import random
import os

random.seed(42)
OUT = os.path.dirname(__file__)

# ============================================================
# EVAL 1: Rich dataset - 50 suppliers, all columns present
# Tests: full pipeline, fuzzy matching, multi-category clustering
# ============================================================
suppliers_rich = [
    ("Acme Corp", "IT Hardware", 155000, "Operations"),
    ("Global Services Inc", "Professional Services", 118000, "Finance"),
    ("TechPro Solutions", "IT Software", 92000, "IT"),
    ("Premier Facilities Mgmt", "Facilities", 83000, "Operations"),
    ("National Staffing Group", "Temporary Staffing", 71000, "HR"),
    ("Office Depot", "Office Supplies", 36000, "Operations"),
    ("CleanCorp Services", "Facilities", 29000, "Operations"),
    ("DataLink Systems", "IT Hardware", 23000, "IT"),
    ("Metro Catering Co", "Catering/Food", 17500, "Operations"),
    ("SafeGuard Supply", "Uniforms/Safety", 14800, "Operations"),
    ("Quick Print Shop", "Printing/Shipping", 8600, "Marketing"),
    ("Joe's IT Repair", "MRO", 7300, "IT"),
    ("City Telecom", "Telecom", 6900, "IT"),
    ("ABC Training Center", "Training", 5600, "HR"),
    ("Smith Legal LLP", "Professional Services", 4900, "Legal"),
    ("Travel Express", "Travel & Entertainment", 4300, "Sales"),
    ("Paper Plus", "Office Supplies", 3900, "Operations"),
    ("Bob's Cleaning", "Facilities", 3600, "Operations"),
    ("Digital Media Co", "Marketing", 3300, "Marketing"),
    ("Local Staffing LLC", "Temporary Staffing", 2950, "HR"),
    ("Flash Couriers", "Printing/Shipping", 2650, "Operations"),
    ("Green Catering", "Catering/Food", 2450, "Operations"),
    ("Tech Parts Direct", "MRO", 2250, "IT"),
    ("Uniforms R Us", "Uniforms/Safety", 2050, "Operations"),
    ("Cloud Nine Software", "IT Software", 1850, "IT"),
    ("MegaOffice Supply", "Office Supplies", 1650, "Operations"),
    # Fuzzy duplicates
    ("QuikPrint Shop", "Printing/Shipping", 1550, "Marketing"),
    ("Joes IT Repair", "MRO", 1450, "IT"),
    ("City Telcom", "Telecom", 1250, "IT"),
    # More tail
    ("Express Training", "Training", 1150, "HR"),
    ("Legal Eagle LLP", "Professional Services", 980, "Legal"),
    ("Budget Travel", "Travel & Entertainment", 850, "Sales"),
    ("PaperPlus Inc", "Office Supplies", 720, "Operations"),
    ("Bobs Cleaning Svc", "Facilities", 680, "Operations"),
    ("Digital Media Company", "Marketing", 620, "Marketing"),
    ("Local Staff LLC", "Temporary Staffing", 580, "HR"),
    ("Courier Fast", "Printing/Shipping", 520, "Operations"),
    ("Green Cat Catering", "Catering/Food", 470, "Operations"),
    ("Spare Parts Inc", "MRO", 420, "IT"),
    ("Uniform Supply Co", "Uniforms/Safety", 380, "Operations"),
    ("Tiny Software Shop", "IT Software", 320, "IT"),
    ("Office Things", "Office Supplies", 290, "Operations"),
    ("Clean It Up", "Facilities", 260, "Operations"),
    ("Web Design Pro", "Marketing", 230, "Marketing"),
    ("Temp Staff Express", "Temporary Staffing", 210, "HR"),
    ("Print It Now", "Printing/Shipping", 190, "Marketing"),
    ("Snack Attack Catering", "Catering/Food", 160, "Operations"),
    ("Fix It Hardware", "MRO", 130, "IT"),
    ("Safety First Inc", "Uniforms/Safety", 110, "Operations"),
    ("Mini Telecom", "Telecom", 90, "IT"),
]

rows = []
for supplier, category, annual, dept in suppliers_rich:
    n_txn = random.randint(1, 5)
    for t in range(n_txn):
        txn_amount = round(annual / n_txn * random.uniform(0.7, 1.3), 2)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        rows.append({
            "Vendor Name": supplier,
            "Invoice Amount": txn_amount,
            "Spend Category": category,
            "Invoice Date": f"2025-{month:02d}-{day:02d}",
            "Department": dept,
            "PO Number": f"PO-{random.randint(10000, 99999)}",
        })
random.shuffle(rows)

with open(os.path.join(OUT, "eval1_rich_spend.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Vendor Name", "Invoice Amount", "Spend Category",
                                       "Invoice Date", "Department", "PO Number"])
    w.writeheader()
    w.writerows(rows)
print(f"Eval 1: {len(rows)} transactions, {len(suppliers_rich)} suppliers")

# ============================================================
# EVAL 2: Minimal dataset - only 3 columns (supplier, amount, description)
# Tests: column auto-detection with non-standard headers, missing category
# ============================================================
minimal_suppliers = [
    ("ACME INDUSTRIAL SUPPLY", 45000, "Bulk fasteners and hardware"),
    ("Johnson & Johnson Med", 38000, "Medical supplies for clinic"),
    ("Staples Business", 22000, "Office paper and toner cartridges"),
    ("FedEx Shipping", 18000, "Overnight and ground shipping"),
    ("Aramark Food Svc", 15000, "Cafeteria catering services"),
    ("Dell Technologies", 12000, "Laptop computers replacement"),
    ("Cintas Uniforms", 8500, "Employee uniform rental"),
    ("Waste Mgmt Inc", 7200, "Waste disposal and recycling"),
    ("Grainger Industrial", 5500, "MRO parts and tools"),
    ("Cintas Uniform Svc", 4200, "Safety gear and uniform cleaning"),  # fuzzy dup
    ("Staples Inc", 3800, "Printer ink and supplies"),  # fuzzy dup
    ("Local Plumber Joe", 2500, "Emergency plumbing repair"),
    ("Quick Signs LLC", 1800, "Signage and banners"),
    ("Pizza Palace", 1200, "Team lunch catering"),
    ("Random Consulting", 950, "Ad hoc advisory work"),
    ("Uber Business", 750, "Ride share for employees"),
    ("Amazon Business", 600, "Misc office purchases"),
    ("Costco Wholesale", 450, "Break room supplies"),
    ("Home Depot Pro", 300, "Maintenance supplies"),
    ("Corner Deli", 150, "Meeting refreshments"),
]

rows2 = []
for supplier, annual, desc in minimal_suppliers:
    n_txn = random.randint(1, 3)
    for t in range(n_txn):
        txn_amount = round(annual / n_txn * random.uniform(0.8, 1.2), 2)
        rows2.append({
            "Payee": supplier,
            "Total Paid": txn_amount,
            "Memo": desc,
        })
random.shuffle(rows2)

with open(os.path.join(OUT, "eval2_minimal_spend.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Payee", "Total Paid", "Memo"])
    w.writeheader()
    w.writerows(rows2)
print(f"Eval 2: {len(rows2)} transactions, {len(minimal_suppliers)} suppliers")

# ============================================================
# EVAL 3: Messy dataset - dirty data, missing values, negative amounts
# Tests: data quality handling, robustness, error recovery
# ============================================================
messy_suppliers = [
    ("  Acme Corp  ", "IT", 50000),
    ("acme corp", "IT", 25000),  # case dup
    ("ACME CORP.", "IT", 15000),  # punctuation dup
    ("Beta Services", "Consulting", 35000),
    ("Beta Srvcs", "Consulting", 12000),  # abbreviation dup
    ("Gamma Supply", "Office", 28000),
    ("Delta Tech", "Software", 22000),
    ("Epsilon Logistics", "Shipping", 18000),
    ("", "IT", 5000),  # missing supplier
    ("Zeta Corp", "", 8000),  # missing category
    ("Eta Systems", "IT", -3500),  # credit/reversal
    ("Theta Inc", "MRO", 0),  # zero amount
    ("Iota Catering", "Food", 4500),
    ("Kappa Legal", "Legal", 3200),
    ("Lambda Training", "Training", 2800),
    ("Mu Staffing", "Temp", 2100),
    ("Nu Electric", "Utilities", 1700),
    ("Xi Printing", "Print", 1200),
    ("Omicron Safety", "Safety", 800),
    ("Pi Telecom", "Telecom", None),  # missing amount
]

rows3 = []
for supplier, category, annual in messy_suppliers:
    n_txn = random.randint(1, 3)
    for t in range(n_txn):
        if annual is None:
            txn_amount = ""
        elif annual <= 0:
            txn_amount = annual
        else:
            txn_amount = round(annual / n_txn * random.uniform(0.7, 1.3), 2)
        month = random.randint(1, 12)
        rows3.append({
            "supplier_name": supplier,
            "spend_amount": txn_amount,
            "commodity": category,
            "txn_date": f"2025-{month:02d}-{random.randint(1,28):02d}",
        })
random.shuffle(rows3)

with open(os.path.join(OUT, "eval3_messy_spend.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["supplier_name", "spend_amount", "commodity", "txn_date"])
    w.writeheader()
    w.writerows(rows3)
print(f"Eval 3: {len(rows3)} transactions, {len(messy_suppliers)} suppliers")
