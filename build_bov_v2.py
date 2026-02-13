#!/usr/bin/env python3
"""
Build script V2 for Stocker Gardens BOV — 420-428 W Stocker St, Glendale, CA 91202
Major content expansion: Investment Overview, Location Overview, expanded Development/ADU/Comp sections.
"""
import base64, json, os, sys, time, urllib.request, urllib.parse, io, statistics

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
BOV_BASE_URL = "https://420428stocker.laaa.com"
PDF_WORKER_URL = "https://laaa-pdf-worker.laaa-team.workers.dev"
PDF_FILENAME = "BOV - 420-428 W Stocker St, Glendale.pdf"
PDF_LINK = PDF_WORKER_URL + "/?url=" + urllib.parse.quote(BOV_BASE_URL + "/", safe="") + "&filename=" + urllib.parse.quote(PDF_FILENAME, safe="")

# ============================================================
# IMAGE LOADING (same as V1)
# ============================================================
def load_image_b64(filename):
    path = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(path):
        print(f"WARNING: Image not found: {path}")
        return ""
    ext = filename.rsplit(".", 1)[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    print(f"  Loaded image: {filename} ({len(data)//1024}KB b64)")
    return f"data:{mime};base64,{data}"

print("Loading images...")
IMG = {
    "logo": load_image_b64("LAAA_Team_White.png"),
    "glen": load_image_b64("Glen_Scher.png"),
    "filip": load_image_b64("Filip_Niculete.png"),
    "hero": load_image_b64("aeiral shot of subject property.png"),
    "grid1": load_image_b64("420 stocker image.png"),
    "grid2": load_image_b64("428 stocker image.png"),
    "grid3": load_image_b64("Screenshot 2026-02-11 135326.png"),
    "grid4": load_image_b64("Screenshot 2026-02-11 135431.png"),
    "adu_aerial": load_image_b64("Gemini_Generated_Image_w3ubtuw3ubtuw3ub.jpeg"),
    "adu_parking": load_image_b64("back parking (potentail spot for ADUs).png"),
    "aerial_outline": load_image_b64("Screenshot 2026-02-11 135520.png"),
    "loc_map": load_image_b64("location-map.png"),
    "closings_map": load_image_b64("closings-map.png"),
}

# ============================================================
# SUBJECT COORDINATES (used for Leaflet comp maps)
# ============================================================
import math
SUBJECT_LAT, SUBJECT_LNG = 34.162911, -118.26303

# ============================================================
# GEOCODING — Use cached coords from V1 to avoid re-hitting API
# ============================================================

# Cached from V1 build (all successfully geocoded)
ADDRESSES = {
    "437 W Glenoaks Blvd, Glendale, CA 91202": (34.159222, -118.262076),
    "559 Glenwood Rd, Glendale, CA 91202": (34.164680, -118.266842),
    "704 Palm Dr, Glendale, CA 91202": (34.161729, -118.270823),
    "336 E Dryden St, Glendale, CA 91207": (34.161332, -118.252078),
    "125 E Fairview Ave, Glendale, CA 91207": (34.160333, -118.254605),
    "1244 N Columbus Ave, Glendale, CA 91202": (34.164934, -118.262001),
    "617 W Stocker St, Glendale, CA 91202": (34.163993, -118.268555),
    "950 N Louise St, Glendale, CA 91207": (34.159607, -118.252585),
    "1151 N Columbus Ave, Glendale, CA 91202": (34.162837, -118.262066),
    "719 N Jackson St, Glendale, CA 91206": (34.156811, -118.250368),
    "1207 N Columbus Ave, Glendale, CA 91202": (34.163843, -118.262272),
    "550 W Stocker St, Glendale, CA 91202": (34.163481, -118.266883),
    "439 W Stocker St, Glendale, CA 91202": (34.163346, -118.263795),
    "432 W Stocker St, Glendale, CA 91202": (34.163208, -118.263624),
    "618 W Dryden St, Glendale, CA 91202": (34.160706, -118.268463),
    "409 W Dryden St, Glendale, CA 91202": (34.161223, -118.262072),
    "245 W Loraine St, Glendale, CA 91204": (34.164637, -118.258906),
    "404 W Stocker St, Glendale, CA 91202": (34.163427, -118.262369),
}
print("Using cached geocode data (18 addresses)")

# ============================================================
# FINANCIAL DATA (from PDF pricing model - source of truth)
# ============================================================
LIST_PRICE = 9_350_000
APT_VALUE = 9_000_000
TAX_RATE = 0.0113
UNITS = 27
SF = 22_674
GSR = 740_748
PF_GSR = 878_280
VACANCY_PCT = 0.05
OTHER_INCOME = 5_820
NON_TAX_CUR_EXP = 158_040
NON_TAX_PF_EXP = 163_266

def calc_metrics(price):
    taxes = price * TAX_RATE
    cur_egi = GSR * (1 - VACANCY_PCT) + OTHER_INCOME
    pf_egi = PF_GSR * (1 - VACANCY_PCT) + OTHER_INCOME
    cur_exp = NON_TAX_CUR_EXP + taxes
    pf_exp = NON_TAX_PF_EXP + taxes
    cur_noi = cur_egi - cur_exp
    pf_noi = pf_egi - pf_exp
    return {"price": price, "taxes": taxes, "cur_noi": cur_noi, "pf_noi": pf_noi,
            "per_unit": price / UNITS, "per_sf": price / SF,
            "cur_cap": cur_noi / price * 100, "pf_cap": pf_noi / price * 100, "grm": price / GSR}

# Descending, $100K increments, matching PDF model range ($9.5M to $8.5M)
MATRIX_PRICES = list(range(9_500_000, 8_400_000, -100_000))
MATRIX = [calc_metrics(p) for p in MATRIX_PRICES]
AT_LIST = calc_metrics(LIST_PRICE)
AT_APT = calc_metrics(APT_VALUE)

print(f"Financials at list ${LIST_PRICE:,.0f}: Cap {AT_LIST['cur_cap']:.2f}%")

# ============================================================
# UNIT MIX DATA
# ============================================================
RENT_ROLL = [
    ("420-House", "4BR/3BA", 2500, 5000, 5000), ("420-A", "2BR/1BA", 750, 2040, 2650),
    ("420-B", "2BR/1BA", 750, 2205, 2650), ("420-C", "2BR/1BA", 750, 2299, 2650),
    ("420-D", "1BR/1BA", 650, 1895, 2295), ("420-E", "2BR/1BA", 750, 2650, 2650),
    ("420-F", "2BR/1BA", 750, 2050, 2650), ("420-G", "2BR/1BA", 750, 2050, 2650),
    ("420-H", "1BR/1BA", 650, 1950, 2295), ("428-1", "2BR/1BA", 750, 2040, 2650),
    ("428-2", "2BR/1BA", 750, 2395, 2650), ("428-3", "2BR/1BA", 750, 2475, 2650),
    ("428-4", "2BR/1BA", 750, 2195, 2650), ("428-5", "2BR/1BA", 750, 2150, 2650),
    ("428-6", "2BR/1BA", 750, 2630, 2650), ("428-7", "2BR/1BA", 750, 2100, 2650),
    ("428-8", "2BR/1BA", 750, 2310, 2650), ("428-9", "2BR/1BA", 750, 900, 2650),
    ("428-10", "2BR/1BA", 750, 2380, 2650), ("428-11", "2BR/1BA", 750, 2650, 2650),
    ("428-12", "2BR/1BA", 750, 2365, 2650), ("428-14", "2BR/1BA", 750, 2040, 2650),
    ("428-15", "2BR/1BA", 750, 2150, 2650), ("428-16", "2BR/1BA", 750, 2025, 2650),
    ("428-17", "2BR/1BA", 750, 2365, 2650), ("428-18", "2BR/1BA", 750, 1970, 2650),
    ("428-19", "2BR/1BA", 750, 2450, 2650),
]

SALE_COMPS = [
    {"num": 1, "addr": "437 W Glenoaks Blvd", "submarket": "Verdugo Viejo", "units": 9, "sf": 6580, "yr": 1962, "price": 2800000, "ppu": 311111, "psf": 425.53, "cap": 4.93, "grm": 13.37, "date": "12/31/2025", "notes": "Trust sale, sold above ask. Updated/remodeled.", "tier": "Value-Add"},
    {"num": 2, "addr": "559 Glenwood Rd", "submarket": "Glenwood", "units": 7, "sf": 6642, "yr": 1952, "price": 2565000, "ppu": 366429, "psf": 386.18, "cap": None, "grm": None, "date": "12/8/2025", "notes": "Off-market. No financials.", "tier": "Value-Add"},
    {"num": 3, "addr": "704 Palm Dr", "submarket": "Glenwood", "units": 14, "sf": 18373, "yr": 1987, "price": 6350000, "ppu": 453571, "psf": 345.62, "cap": None, "grm": None, "date": "10/31/2025", "notes": "Off-market. 1987 build.", "tier": "Stabilized"},
    {"num": 4, "addr": "336 E Dryden St", "submarket": "Rossmoyne", "units": 8, "sf": 7866, "yr": 1960, "price": 3240000, "ppu": 405000, "psf": 411.90, "cap": 4.84, "grm": 13.43, "date": "9/9/2025", "notes": "New roof, copper plumbing, dual-pane.", "tier": "Stabilized"},
    {"num": 5, "addr": "125 E Fairview Ave", "submarket": "Rossmoyne", "units": 9, "sf": 10295, "yr": 1986, "price": 4240000, "ppu": 471111, "psf": 411.85, "cap": 4.83, "grm": 13.72, "date": "6/17/2025", "notes": "1986 build, central AC, subterranean pkg. 1 DOM.", "tier": "Stabilized"},
    {"num": 6, "addr": "1244 N Columbus Ave", "submarket": "Verdugo Viejo", "units": 12, "sf": 7424, "yr": 1953, "price": 3650000, "ppu": 304167, "psf": 491.65, "cap": 4.38, "grm": 16.11, "date": "5/30/2025", "notes": "Same yr built. 95 DOM, $73K concessions.", "tier": "Value-Add"},
    {"num": 7, "addr": "617 W Stocker St", "submarket": "Glendale", "units": 9, "sf": 8816, "yr": 1962, "price": 3546000, "ppu": 394000, "psf": 402.22, "cap": 4.77, "grm": 14.84, "date": "2/20/2025", "notes": "SAME STREET. All 2BR/1BA. Updated.", "tier": "Stabilized"},
    {"num": 8, "addr": "950 N Louise St", "submarket": "Rossmoyne", "units": 25, "sf": 34700, "yr": 1967, "price": 9250000, "ppu": 370000, "psf": 266.57, "cap": 5.17, "grm": 11.60, "date": "1/24/2025", "notes": "Best size match. M&M listing. $1M+ capex.", "tier": "Value-Add"},
]

# ============================================================
# OPERATING STATEMENT — uses PDF model figures at $9.0M apartment value (source of truth)
# ============================================================
TAXES_AT_APT_VALUE = APT_VALUE * TAX_RATE  # $101,700 per PDF model at $9.0M
CUR_EGI = GSR * (1 - VACANCY_PCT) + OTHER_INCOME
PF_EGI = PF_GSR * (1 - VACANCY_PCT) + OTHER_INCOME
CUR_MGMT = CUR_EGI * 0.04
PF_MGMT = PF_EGI * 0.04
CUR_TOTAL_EXP = TAXES_AT_APT_VALUE + 28074 + 24945 + 2979 + 17700 + 20250 + 4800 + 700 + 24000 + 2160 + 4050 + CUR_MGMT
PF_TOTAL_EXP = TAXES_AT_APT_VALUE + 28074 + 24945 + 2979 + 17700 + 20250 + 4800 + 700 + 24000 + 2160 + 4050 + PF_MGMT
CUR_NOI_AT_LIST = CUR_EGI - CUR_TOTAL_EXP
PF_NOI_AT_LIST = PF_EGI - PF_TOTAL_EXP

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def fc(n):
    if n is None: return "n/a"
    return f"${n:,.0f}"
def fp(n):
    if n is None: return "n/a"
    return f"{n:.2f}%"

def build_map_js(map_id, comps, comp_color, subject_lat, subject_lng):
    js = f"var {map_id} = L.map('{map_id}').setView([{subject_lat}, {subject_lng}], 14);\n"
    js += f"L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{attribution: '&copy; OpenStreetMap'}}).addTo({map_id});\n"
    js += f"""L.marker([{subject_lat}, {subject_lng}], {{icon: L.divIcon({{className: 'custom-marker', html: '<div style="background:#C5A258;color:#fff;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);">&#9733;</div>', iconSize: [32, 32], iconAnchor: [16, 16]}})}})\n.addTo({map_id}).bindPopup('<b>420-428 W Stocker St</b><br>Subject Property<br>27 Units | 22,674 SF');\n"""
    for i, c in enumerate(comps):
        lat, lng = None, None
        for a, coords in ADDRESSES.items():
            if c["addr"].lower() in a.lower() and coords:
                lat, lng = coords
                break
        if lat is None: continue
        label = str(i + 1)
        popup = f"<b>#{label}: {c['addr']}</b><br>{c.get('units', '')} Units | {fc(c.get('price', 0))}"
        js += f"""L.marker([{lat}, {lng}], {{icon: L.divIcon({{className: 'custom-marker', html: '<div style="background:{comp_color};color:#fff;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;border:2px solid #fff;box-shadow:0 2px 4px rgba(0,0,0,0.3);">{label}</div>', iconSize: [26, 26], iconAnchor: [13, 13]}})}})\n.addTo({map_id}).bindPopup('{popup}');\n"""
    return js

sale_map_js = build_map_js("saleMap", SALE_COMPS, "#1B3A5C", SUBJECT_LAT, SUBJECT_LNG)
active_comps_for_map = [
    {"addr": "1151 N Columbus Ave", "units": 5, "price": 1699000},
    {"addr": "719 N Jackson St", "units": 6, "price": 1950000},
    {"addr": "1207 N Columbus Ave", "units": 10, "price": 4695000},
]
active_map_js = build_map_js("activeMap", active_comps_for_map, "#2E7D32", SUBJECT_LAT, SUBJECT_LNG)
rent_comps_for_map = [{"addr": a, "price": 0, "units": ""} for a in ["550 W Stocker St","439 W Stocker St","432 W Stocker St","618 W Dryden St","409 W Dryden St","245 W Loraine St","404 W Stocker St"]]
rent_map_js = build_map_js("rentMap", rent_comps_for_map, "#1B3A5C", SUBJECT_LAT, SUBJECT_LNG)

# ============================================================
# GENERATE DYNAMIC TABLE HTML
# ============================================================

# Pricing matrix
matrix_html = ""
for m in MATRIX:
    cls = ' class="highlight"' if m["price"] == LIST_PRICE else ""
    matrix_html += f'<tr{cls}><td class="num">{fc(m["price"])}</td><td class="num">{fp(m["cur_cap"])}</td><td class="num">{fc(m["per_unit"])}</td><td class="num">${m["per_sf"]:.0f}</td><td class="num">{m["grm"]:.2f}x</td></tr>\n'

# Rent roll
rent_roll_html = ""
total_sf = total_cur = total_mkt = 0
for unit, utype, sqft, cur, mkt in RENT_ROLL:
    rent_roll_html += f"<tr><td>{unit}</td><td>{utype}</td><td>{sqft:,}</td><td>${cur:,}</td><td>${cur/sqft:.2f}</td><td>${mkt:,}</td><td>${mkt/sqft:.2f}</td></tr>\n"
    total_sf += sqft; total_cur += cur; total_mkt += mkt
rent_roll_html += f'<tr style="font-weight:700;background:#1B3A5C;color:#fff;"><td>TOTAL</td><td>27 Units</td><td>{total_sf:,}</td><td>${total_cur:,}</td><td>${total_cur/total_sf:.2f}</td><td>${total_mkt:,}</td><td>${total_mkt/total_sf:.2f}</td></tr>'

# Sale comps table
sale_comps_html = ""
# Subject row first (bold, highlighted)
sale_comps_html += f'<tr class="highlight" style="font-weight:700;"><td>S</td><td>420-428 W Stocker St</td><td>Glenwood</td><td>{UNITS}</td><td>Proposed</td><td>{fc(APT_VALUE)}</td><td>{fc(APT_VALUE // UNITS)}</td><td>${APT_VALUE / SF:.0f}</td><td>{AT_APT["cur_cap"]:.2f}%</td><td>{AT_APT["grm"]:.2f}</td><td>1953</td><td style="font-size:11px;">Subject Property</td></tr>\n'
for c in SALE_COMPS:
    cap_str = fp(c["cap"]) if c["cap"] else "n/a"
    grm_str = f'{c["grm"]:.2f}' if c["grm"] else "n/a"
    tier_tag = f' <em style="color:#C5A258;">[{c["tier"]}]</em>' if c.get("tier") else ""
    hl = ' class="highlight"' if "SAME STREET" in (c.get("notes") or "") else ""
    sale_comps_html += f'<tr{hl}><td>{c["num"]}</td><td>{c["addr"]}</td><td>{c["submarket"]}</td><td>{c["units"]}</td><td>{c["date"]}</td><td>{fc(c["price"])}</td><td>{fc(c["ppu"])}</td><td>${c["psf"]:.0f}</td><td>{cap_str}</td><td>{grm_str}</td><td>{c["yr"]}</td><td style="font-size:11px;">{c["notes"]}{tier_tag}</td></tr>\n'
caps = [c["cap"] for c in SALE_COMPS if c["cap"]]
grms = [c["grm"] for c in SALE_COMPS if c["grm"]]
ppus = [c["ppu"] for c in SALE_COMPS]
psfs = [c["psf"] for c in SALE_COMPS]
prices = [c["price"] for c in SALE_COMPS]
units_list = [c["units"] for c in SALE_COMPS]
sale_comps_html += f'<tr style="font-weight:600;background:#f0f4f8;"><td></td><td>Averages</td><td></td><td>{sum(units_list)//len(units_list)}</td><td></td><td>{fc(sum(prices)//len(prices))}</td><td>{fc(sum(ppus)//len(ppus))}</td><td>${sum(psfs)/len(psfs):.0f}</td><td>{fp(sum(caps)/len(caps))}</td><td>{sum(grms)/len(grms):.2f}</td><td></td><td></td></tr>'
med_units = int(statistics.median(units_list))
med_price = int(statistics.median(prices))
med_ppu = int(statistics.median(ppus))
med_psf = statistics.median(psfs)
med_cap = statistics.median(caps)
med_grm = statistics.median(grms)
sale_comps_html += f'<tr style="font-weight:600;background:#f0f4f8;"><td></td><td>Medians</td><td></td><td>{med_units}</td><td></td><td>{fc(med_price)}</td><td>{fc(med_ppu)}</td><td>${med_psf:.0f}</td><td>{med_cap:.2f}%</td><td>{med_grm:.2f}</td><td></td><td></td></tr>'

# Operating statement
# Operating statement — single-column format: Annual, Per Unit, % EGI
# Income section (% EGI = "—" for income lines)
income_lines = [
    ("Gross Scheduled Rent", GSR, False),
    ("Less: Vacancy (5%)", -(GSR * VACANCY_PCT), False),
    ("Other Income (Parking)", OTHER_INCOME, False),
]
# Expense section
expense_lines = [
    ("Real Estate Taxes", TAXES_AT_APT_VALUE),
    ("Insurance", 28074),
    ("Water & Power", 24945),
    ("Gas", 2979),
    ("Trash Removal", 17700),
    ("Repairs & Maintenance", 20250),
    ("Landscaping", 4800),
    ("Pest Control", 700),
    ("On-site Manager", 24000),
    ("General & Administrative", 2160),
    ("Operating Reserves", 4050),
    ("Management Fee (4%)", CUR_MGMT),
]

op_income_html = ""
for label, val, _ in income_lines:
    v_str = f"${val:,.0f}" if val >= 0 else f"(${abs(val):,.0f})"
    pu = f"${val/UNITS:,.0f}" if val >= 0 else f"(${abs(val)/UNITS:,.0f})"
    op_income_html += f"<tr><td>{label}</td><td class='num'>{v_str}</td><td class='num'>{pu}</td><td class='num'> - </td></tr>\n"
op_income_html += f'<tr class="summary"><td><strong>Effective Gross Income</strong></td><td class="num"><strong>${CUR_EGI:,.0f}</strong></td><td class="num"><strong>${CUR_EGI/UNITS:,.0f}</strong></td><td class="num"><strong>100.0%</strong></td></tr>'

op_expense_html = ""
for label, val in expense_lines:
    pct = f"{val/CUR_EGI*100:.1f}%"
    op_expense_html += f"<tr><td>{label}</td><td class='num'>${val:,.0f}</td><td class='num'>${val/UNITS:,.0f}</td><td class='num'>{pct}</td></tr>\n"
op_expense_html += f'<tr class="summary"><td><strong>Total Expenses</strong></td><td class="num"><strong>${CUR_TOTAL_EXP:,.0f}</strong></td><td class="num"><strong>${CUR_TOTAL_EXP/UNITS:,.0f}</strong></td><td class="num"><strong>{CUR_TOTAL_EXP/CUR_EGI*100:.1f}%</strong></td></tr>'
op_expense_html += f'\n<tr class="summary"><td><strong>Net Operating Income</strong></td><td class="num"><strong>${CUR_NOI_AT_LIST:,.0f}</strong></td><td class="num"><strong>${CUR_NOI_AT_LIST/UNITS:,.0f}</strong></td><td class="num"><strong>{CUR_NOI_AT_LIST/CUR_EGI*100:.1f}%</strong></td></tr>'

# ============================================================
# COMP NARRATIVES (from SALE_COMP_ANALYSIS.md)
# ============================================================
COMP_NARRATIVES = [
    # Comp 1
    """<p><strong>437 W Glenoaks Blvd (9 units, $2.8M, 12/31/2025):</strong> "Santa Barbara Apartments" - a trust sale featuring 4 two-bedroom and 5 one-bedroom units. Recently updated with new electric subpanels in every unit, new main service panel, updated asphalt, fresh exterior paint, upgraded railings, and new irrigation. Three apartments recently remodeled. Sold <em>above</em> asking ($2.75M list to $2.8M sale, 101.82% SP/LP) in just 30 DOM, signaling strong buyer demand in the 91202 submarket. Tenants pay all utilities. At $311K/unit, this is the lowest $/unit among non-distressed comps but reflects only 9 units. The nearly identical cap rate to the subject (4.93% vs. 5.00%) validates income-based pricing. The subject's higher $/unit ($333K) is justified by 3x scale and 1.1-acre lot with ADU potential.</p>""",
    # Comp 2
    """<p><strong>559 Glenwood Rd (7 units, $2.565M, 12/8/2025):</strong> Off-market MLS Entry Only transaction with zero financial data, no condition information, and no unit details. Its primary value is as a $/unit reference point: at $366K/unit for a 7-unit building in 91202 with unknown condition, it demonstrates that even small, unmarketed Glendale properties trade above the subject's $333K/unit. The 1952 vintage is nearly identical to the subject's 1953.</p>""",
    # Comp 3
    """<p><strong>704 Palm Dr (14 units, $6.35M, 10/31/2025):</strong> Another off-market MLS Entry Only sale with no financial data. Built in 1987 (34 years newer than subject), this property represents a fundamentally different product class. At $454K/unit, it establishes the ceiling for mid-size buildings in 91202. The subject's $333K/unit (27% below) appropriately reflects the vintage gap. Notably, this comp's $/SF ($346) is actually <em>lower</em> than the subject's ($397), because the comp's 18,373 SF building on a 13,011 SF lot has a tighter building-to-land ratio.</p>""",
    # Comp 4
    """<p><strong>336 E Dryden St (8 units, $3.24M, 9/9/2025):</strong> Premium comp in Rossmoyne (91207) with extensive capital improvements: new roof, copper plumbing, dual-pane windows, new sewer line, and select unit remodels. This pride-of-ownership property (first time on market) sold quickly at 98.18% of ask in just 11 DOM with cash financing. Unit mix of 7x 2BR/1BA + 1x 1BR/1BA closely mirrors the subject. At $405K/unit and 4.84% cap, it reflects the value of completed capex in a premium location. The subject's $333K/unit (18% below) is the appropriate discount for 91202 vs. 91207 location, less-updated condition, and 3.4x larger scale.</p>""",
    # Comp 5
    """<p><strong>125 E Fairview Ave (9 units, $4.24M, 6/17/2025):</strong> The absolute ceiling for Glendale multifamily. Built in 1986 with central AC, gated access, subterranean parking, private balconies, and spacious 2BR/2BA units. Sold in <em>1 day</em> at 99.18% of ask, reflecting extreme buyer demand. Located in Rossmoyne at the corner of Brand Blvd, the most prestigious Glendale submarket. At $471K/unit (41% above subject), this comp demonstrates the premium for newer, institutional-quality product. The cap rate (4.83%) is nearly identical to the subject (5.00%), confirming that the Glendale market prices consistently around 5% regardless of vintage. The premium for newer/better product flows through $/unit and $/SF, not cap rate.</p>""",
    # Comp 6
    """<p><strong>1244 N Columbus Ave (12 units, $3.65M, 5/30/2025):</strong> The only comp with an identical year built (1953) to the subject. However, the unit mix is fundamentally different: 10 one-bedroom and 2 two-bedroom units (83% 1BR vs. subject's 89% 2BR). The sale was slow: 95 DOM, two price reductions (from $3.995M to $3.795M), and $73,000 in concessions bringing the net effective price to ~$3.577M ($298K/unit). Updated with copper plumbing, new asphalt, sewer clean-outs, and a 2017 roof. The very low 4.38% cap and high 16.11 GRM reflect deep value-add pricing. The subject's stronger income metrics (5.00% cap, 12.15 GRM) mean a buyer gets significantly more income per dollar, and the subject's 2BR-dominant mix commands a premium. This comp establishes the floor for same-vintage, same-zip product.</p>""",
    # Comp 7
    """<p><strong>617 W Stocker St (9 units, $3.546M, 2/20/2025) - PRIMARY ANCHOR:</strong> The single most relevant comparable. Located on the <em>same street</em> with an identical unit type (all 2BR/1BA), same 91202 zip code, and same GLR4YY zoning. MLS remarks describe the location as "arguably the best location in Glendale... north of Glenoaks in the 91202 zip code, nestled just below multimillion-dollar homes, 3 schools within 1 block walking distance." The property was updated with a pitched roof, all new windows/sliders, and several remodeled unit interiors. Listed at $3.65M, contracted in 15 DOM, closed at $3.546M (97.15% SP/LP) after a long escrow. Same agent represented both buyer and seller (Levon Alexanian). At $394K/unit and $402/SF, the subject's pricing at $333K/unit is a 15% discount and $397/SF is nearly identical. This discount is the correct magnitude for a property that is 3x larger, 9 years older, and less updated. The near-identical $/SF ($402 vs. $397) is the strongest single validation of the $9.0M apartment value.</p>""",
    # Comp 8
    """<p><strong>950 N Louise St (25 units, $9.25M, 1/24/2025) - BEST SIZE MATCH:</strong> The closest unit-count comparison (25 vs. 27 units) and the only comp in a similar price tier. A Marcus &amp; Millichap listing (Andy Kawatra) that was listed at $9.95M and ultimately sold at $9.25M (93% of ask, 129 DOM). This is a fundamentally premium product: 3-story elevator building in 91207 Rossmoyne, 1,388 SF average units (vs. subject's 840 SF), common AC system, and $1M+ in owner capex invested (17 of 25 units upgraded with hardwood floors and granite countertops). The MLS confirms R1250 zoning, validating our zoning assumption for the subject. Despite all premiums, it traded at $370K/unit, only 11% above the subject's $333K/unit. The subject offers a comparable 5.00% cap (vs. 5.17%) with significantly more upside ($138K rent + $127K ADU NOI) on a property that has not yet captured its value-add potential.</p>""",
]

print("Building HTML...")

# ============================================================
# ASSEMBLE FULL HTML — V2 with expanded content
# ============================================================
# NOTE: Due to file size, the CSS is identical to V1. Only the HTML body content changes.

# Read the V1 CSS from the existing build (it's the same)
# For efficiency, we'll inline it directly

html_parts = []

# HEAD + CSS (same as V1)
html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BOV - 420-428 W Stocker St, Glendale | LAAA Team</title>
<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');</style>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;color:#333;line-height:1.6;background:#fff;}}
html{{scroll-padding-top:50px;}}
.cover{{position:relative;min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;color:#fff;overflow:hidden;}}
.cover-bg{{position:absolute;inset:0;background-size:cover;background-position:center;filter:brightness(0.45);z-index:0;}}
.cover-content{{position:relative;z-index:2;padding:60px 40px;max-width:860px;}}
.cover-logo{{width:320px;margin:0 auto 30px;display:block;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.3));}}
.cover-label{{font-size:13px;font-weight:500;letter-spacing:3px;text-transform:uppercase;color:#C5A258;margin-bottom:18px;}}
.cover-title{{font-size:46px;font-weight:700;letter-spacing:1px;margin-bottom:8px;text-shadow:0 2px 12px rgba(0,0,0,0.3);}}
.cover-subtitle{{font-size:20px;font-weight:300;color:rgba(255,255,255,0.8);margin-bottom:28px;}}
.cover-price{{font-size:48px;font-weight:700;color:#C5A258;margin-bottom:28px;text-shadow:0 2px 8px rgba(0,0,0,0.2);}}
.cover-stats{{display:flex;gap:32px;justify-content:center;flex-wrap:wrap;margin-bottom:32px;}}
.cover-stat{{text-align:center;}}.cover-stat-value{{display:block;font-size:26px;font-weight:600;color:#fff;}}.cover-stat-label{{display:block;font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:1.5px;color:#C5A258;margin-top:4px;}}
.client-greeting{{font-size:16px;font-weight:400;letter-spacing:2px;text-transform:uppercase;color:#C5A258;margin-top:16px;}}
.cover-headshots{{display:flex;justify-content:center;gap:40px;margin-top:24px;margin-bottom:16px;}}
.cover-headshot-wrap{{text-align:center;}}
.cover-headshot{{width:80px;height:80px;border-radius:50%;border:3px solid #C5A258;object-fit:cover;box-shadow:0 4px 16px rgba(0,0,0,0.4);}}
.cover-headshot-name{{font-size:12px;font-weight:600;margin-top:6px;color:#fff;}}
.cover-headshot-title{{font-size:10px;color:#C5A258;}}
.gold-line{{height:3px;background:#C5A258;margin:20px 0;}}
.pdf-float-btn{{position:fixed;bottom:24px;right:24px;z-index:9999;padding:14px 28px;background:#C5A258;color:#1B3A5C;font-size:14px;font-weight:700;text-decoration:none;border-radius:8px;letter-spacing:0.5px;box-shadow:0 4px 16px rgba(0,0,0,0.35);transition:background 0.2s,transform 0.2s;display:flex;align-items:center;gap:8px;}}.pdf-float-btn:hover{{background:#fff;transform:translateY(-2px);}}.pdf-float-btn svg{{width:18px;height:18px;fill:currentColor;}}
.toc-nav{{background:#1B3A5C;padding:0 12px;display:flex;flex-wrap:nowrap;gap:0;justify-content:center;align-items:stretch;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,0.15);overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;-ms-overflow-style:none;}}
.toc-nav::-webkit-scrollbar{{display:none;}}
.toc-nav a{{color:rgba(255,255,255,0.85);text-decoration:none;font-size:11px;font-weight:500;letter-spacing:0.3px;text-transform:uppercase;padding:12px 8px;border-bottom:2px solid transparent;transition:all 0.2s ease;white-space:nowrap;display:flex;align-items:center;}}
.toc-nav a:hover{{color:#fff;background:rgba(197,162,88,0.12);border-bottom-color:rgba(197,162,88,0.4);}}.toc-nav a.toc-active{{color:#C5A258;font-weight:600;border-bottom-color:#C5A258;}}
.section{{padding:50px 40px;max-width:1100px;margin:0 auto;}}.section-alt{{background:#f8f9fa;}}
.section-title{{font-size:26px;font-weight:700;color:#1B3A5C;margin-bottom:6px;}}.section-subtitle{{font-size:13px;color:#C5A258;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:16px;font-weight:500;}}
.section-divider{{width:60px;height:3px;background:#C5A258;margin-bottom:30px;}}.sub-heading{{font-size:18px;font-weight:600;color:#1B3A5C;margin:30px 0 16px;}}
.metrics-grid,.metrics-grid-4{{display:grid;gap:16px;margin-bottom:30px;}}.metrics-grid{{grid-template-columns:repeat(3,1fr);}}.metrics-grid-4{{grid-template-columns:repeat(4,1fr);}}
.metric-card{{background:#1B3A5C;border-radius:12px;padding:24px;text-align:center;color:#fff;}}
.metric-value{{display:block;font-size:28px;font-weight:700;color:#fff;margin-bottom:4px;}}.metric-label{{display:block;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,0.6);margin-top:6px;}}.metric-sub{{display:block;font-size:12px;color:#C5A258;margin-top:4px;}}
table{{width:100%;border-collapse:collapse;margin-bottom:24px;font-size:13px;}}th{{background:#1B3A5C;color:#fff;padding:10px 12px;text-align:left;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;}}td{{padding:8px 12px;border-bottom:1px solid #eee;}}tr:nth-child(even){{background:#f5f5f5;}}tr.highlight{{background:#FFF8E7 !important;border-left:3px solid #C5A258;}}
.table-scroll{{overflow-x:auto;-webkit-overflow-scrolling:touch;margin-bottom:24px;}}.table-scroll table{{min-width:700px;margin-bottom:0;}}
.info-table{{width:100%;}}.info-table td{{padding:8px 12px;border-bottom:1px solid #eee;font-size:13px;}}.info-table td:first-child{{font-weight:600;color:#1B3A5C;width:40%;}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-bottom:30px;}}
.photo-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:30px;border-radius:8px;overflow:hidden;}}.photo-grid img{{width:100%;height:180px;object-fit:cover;border-radius:4px;}}
.condition-note{{background:#FFF8E7;border-left:4px solid #C5A258;padding:16px 20px;margin:24px 0;border-radius:0 4px 4px 0;font-size:13px;line-height:1.6;}}
.buyer-profile{{background:#f0f4f8;border-left:4px solid #1B3A5C;padding:20px 24px;margin:24px 0;border-radius:0 4px 4px 0;}}.buyer-profile-label{{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#1B3A5C;margin-bottom:12px;}}.buyer-profile ul{{list-style:none;padding:0;margin:0;}}.buyer-profile li{{padding:8px 0;border-bottom:1px solid #dce3eb;font-size:14px;line-height:1.6;color:#333;}}.buyer-profile li:last-child{{border-bottom:none;}}.buyer-profile li strong{{color:#1B3A5C;}}.buyer-profile .bp-closing{{font-size:13px;color:#555;margin-top:12px;font-style:italic;}}
.leaflet-map{{height:400px;border-radius:4px;border:1px solid #ddd;margin-bottom:30px;z-index:1;}}.map-fallback{{display:none;font-size:12px;color:#666;font-style:italic;margin-bottom:30px;}}
.embed-map-wrap{{position:relative;width:100%;margin-bottom:20px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);}}.embed-map-wrap iframe{{display:block;width:100%;height:350px;border:0;}}.embed-map-caption{{font-size:12px;color:#888;text-align:center;margin-top:8px;font-style:italic;}}.embed-map-fallback{{display:none;font-size:12px;color:#666;font-style:italic;margin-bottom:30px;}}
.adu-img-wrap{{margin-bottom:20px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);}}.adu-img-wrap img{{width:100%;display:block;}}
.footer{{background:#1B3A5C;color:#fff;padding:50px 40px;text-align:center;}}.footer-logo{{width:180px;margin-bottom:30px;filter:drop-shadow(0 2px 6px rgba(0,0,0,0.3));}}.footer-team{{display:flex;justify-content:center;gap:40px;margin-bottom:30px;flex-wrap:wrap;}}.footer-person{{text-align:center;flex:1;min-width:280px;}}.footer-headshot{{width:70px;height:70px;border-radius:50%;border:2px solid #C5A258;margin-bottom:10px;object-fit:cover;}}.footer-name{{font-size:16px;font-weight:600;}}.footer-title{{font-size:12px;color:#C5A258;margin-bottom:8px;}}.footer-contact{{font-size:12px;color:rgba(255,255,255,0.7);line-height:1.8;}}.footer-contact a{{color:rgba(255,255,255,0.7);text-decoration:none;}}.footer-office{{font-size:12px;color:rgba(255,255,255,0.5);margin-top:20px;}}.footer-disclaimer{{font-size:10px;color:rgba(255,255,255,0.35);margin-top:20px;max-width:800px;margin-left:auto;margin-right:auto;line-height:1.6;}}
p{{margin-bottom:16px;font-size:14px;line-height:1.7;}}
.highlight-box{{background:#f0f4f8;border:1px solid #dce3eb;border-radius:8px;padding:20px 24px;margin:24px 0;}}
.highlight-box h4{{color:#1B3A5C;font-size:14px;margin-bottom:10px;}}
.highlight-box ul{{margin:0;padding-left:20px;}}.highlight-box li{{font-size:13px;margin-bottom:6px;line-height:1.5;}}
td.num,th.num{{text-align:right;}}
.broker-insight{{background:#f8f4eb;border-left:4px solid #C5A258;padding:16px 20px;margin:24px 0;border-radius:0 4px 4px 0;font-size:13px;line-height:1.7;color:#444;}}
.broker-insight-label{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#C5A258;margin-bottom:8px;display:block;}}
.costar-badge{{text-align:center;background:#FFF8E7;border:2px solid #C5A258;border-radius:8px;padding:20px 24px;margin:30px auto 24px;max-width:600px;}}
.costar-badge-title{{font-size:22px;font-weight:700;color:#1B3A5C;line-height:1.2;}}
.costar-badge-sub{{font-size:12px;color:#C5A258;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;margin-top:6px;}}
.bio-grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:24px 0;}}
.bio-card{{display:flex;gap:16px;align-items:flex-start;}}
.bio-headshot{{width:80px;height:80px;border-radius:50%;border:3px solid #C5A258;object-fit:cover;flex-shrink:0;}}
.bio-name{{font-size:16px;font-weight:700;color:#1B3A5C;margin-bottom:2px;}}
.bio-title{{font-size:11px;color:#C5A258;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;}}
.bio-text{{font-size:13px;line-height:1.6;color:#444;}}
.press-strip{{display:flex;justify-content:center;align-items:center;gap:28px;flex-wrap:wrap;margin:24px 0;padding:16px 20px;background:#f0f4f8;border-radius:6px;}}
.press-strip-label{{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#888;font-weight:600;}}
.press-logo{{font-size:13px;font-weight:700;color:#1B3A5C;letter-spacing:0.5px;}}
.condition-note-label{{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#C5A258;margin-bottom:8px;}}
.img-float-right{{float:right;width:48%;margin:0 0 16px 20px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);}}.img-float-right img{{width:100%;display:block;}}
.os-two-col{{display:grid;grid-template-columns:55% 45%;gap:24px;align-items:start;margin-bottom:24px;}}.os-right{{font-size:10.5px;line-height:1.45;color:#555;}}.os-right h3{{font-size:13px;margin:0 0 8px;}}.os-right p{{margin-bottom:4px;}}
.loc-grid{{display:grid;grid-template-columns:58% 42%;gap:28px;align-items:start;}}.loc-left p{{font-size:13.5px;line-height:1.7;margin-bottom:14px;}}.loc-right{{display:block;}}.loc-wide-map{{width:100%;height:200px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin-top:20px;}}.loc-wide-map img{{width:100%;height:100%;object-fit:cover;object-position:center;display:block;}}
.tr-tagline{{font-size:20px;font-weight:600;color:#1B3A5C;text-align:center;padding:16px 24px;margin-bottom:20px;border-left:4px solid #C5A258;background:#FFF8E7;border-radius:0 4px 4px 0;font-style:italic;}}.tr-map-print{{display:none;}}.tr-service-quote{{margin:24px 0;}}.tr-service-quote h3{{font-size:18px;font-weight:700;color:#1B3A5C;margin-bottom:8px;line-height:1.3;}}.tr-service-quote p{{font-size:14px;line-height:1.7;}}.tr-mission{{background:#f0f4f8;border-left:4px solid #1B3A5C;padding:20px 24px;margin-bottom:24px;border-radius:0 4px 4px 0;}}.tr-mission h3{{font-size:18px;font-weight:700;color:#1B3A5C;margin-bottom:12px;}}.tr-mission p{{font-size:13px;line-height:1.7;margin-bottom:10px;}}
.inv-split{{display:grid;grid-template-columns:50% 50%;gap:24px;}}.inv-left .metrics-grid-4{{grid-template-columns:repeat(2,1fr);}}.inv-text p{{font-size:13px;line-height:1.6;margin-bottom:10px;}}.inv-logo{{width:200px;margin-top:16px;opacity:0.7;}}.inv-right{{display:flex;flex-direction:column;gap:16px;}}.inv-photo{{height:280px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);}}.inv-photo img{{width:100%;height:100%;object-fit:cover;object-position:center;display:block;}}.inv-highlights{{background:#f0f4f8;border:1px solid #dce3eb;border-radius:8px;padding:16px 20px;flex:1;}}.inv-highlights h4{{color:#1B3A5C;font-size:13px;margin-bottom:8px;}}.inv-highlights ul{{margin:0;padding-left:18px;}}.inv-highlights li{{font-size:12px;line-height:1.5;margin-bottom:5px;}}
.buyer-split{{display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:start;}}.buyer-objections .obj-item{{margin-bottom:14px;}}.buyer-objections .obj-q{{font-weight:700;color:#1B3A5C;margin-bottom:4px;font-size:14px;}}.buyer-objections .obj-a{{font-size:13px;color:#444;line-height:1.6;}}.buyer-photo{{width:100%;height:220px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin-top:24px;}}.buyer-photo img{{width:100%;height:100%;object-fit:cover;object-position:center;display:block;}}
.prop-tables-bottom{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:24px;}}.prop-tables-bottom .sub-heading{{font-size:15px;margin:0 0 10px;}}
.mkt-quote{{background:#FFF8E7;border-left:4px solid #C5A258;padding:16px 24px;margin:20px 0;border-radius:0 4px 4px 0;font-size:15px;font-style:italic;line-height:1.6;color:#1B3A5C;}}.mkt-channels{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px;}}.mkt-channel{{background:#f0f4f8;border-radius:8px;padding:16px 20px;}}.mkt-channel h4{{color:#1B3A5C;font-size:14px;margin-bottom:8px;}}.mkt-channel ul{{margin:0;padding-left:18px;}}.mkt-channel li{{font-size:13px;line-height:1.5;margin-bottom:4px;}}
.perf-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px;}}.perf-card{{background:#f0f4f8;border-radius:8px;padding:16px 20px;}}.perf-card h4{{color:#1B3A5C;font-size:14px;margin-bottom:8px;}}.perf-card ul{{margin:0;padding-left:18px;}}.perf-card li{{font-size:13px;line-height:1.5;margin-bottom:4px;}}.platform-strip{{display:flex;justify-content:center;align-items:center;gap:20px;flex-wrap:wrap;margin-top:24px;padding:14px 20px;background:#1B3A5C;border-radius:6px;}}.platform-strip-label{{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#C5A258;font-weight:600;}}.platform-name{{font-size:12px;font-weight:600;color:#fff;letter-spacing:0.5px;}}
@media(max-width:768px){{.cover-content{{padding:30px 20px;}}.cover-title{{font-size:32px;}}.cover-price{{font-size:36px;}}.cover-logo{{width:220px;}}.cover-headshots{{gap:24px;}}.cover-headshot{{width:60px;height:60px;}}.pdf-float-btn{{padding:10px 18px;font-size:12px;bottom:16px;right:16px;}}.section{{padding:30px 16px;}}.photo-grid{{grid-template-columns:1fr;}}.two-col{{grid-template-columns:1fr;}}.metrics-grid,.metrics-grid-4{{grid-template-columns:repeat(2,1fr);gap:12px;}}.metric-card{{padding:14px 10px;}}.metric-value{{font-size:22px;}}.footer-team{{flex-direction:column;align-items:center;}}.leaflet-map{{height:300px;}}.embed-map-wrap iframe{{height:320px;}}.toc-nav{{padding:0 6px;}}.toc-nav a{{font-size:10px;padding:10px 6px;letter-spacing:0.2px;}}.table-scroll table{{min-width:560px;}}.bio-grid{{grid-template-columns:1fr;gap:16px;}}.bio-headshot{{width:60px;height:60px;}}.press-strip{{gap:16px;}}.press-logo{{font-size:11px;}}.costar-badge-title{{font-size:18px;}}.img-float-right{{float:none;width:100%;margin:0 0 16px 0;}}.os-two-col{{grid-template-columns:1fr;}}.loc-grid{{grid-template-columns:1fr;}}.loc-wide-map{{height:180px;margin-top:16px;}}.inv-split{{grid-template-columns:1fr;}}.inv-photo{{height:240px;}}.buyer-split{{grid-template-columns:1fr;}}.mkt-channels,.perf-grid{{grid-template-columns:1fr;}}}}
@media(max-width:420px){{.cover-content{{padding:24px 16px;}}.cover-logo{{width:180px;}}.cover-title{{font-size:24px;}}.cover-subtitle{{font-size:15px;}}.cover-price{{font-size:28px;}}.cover-stats{{gap:10px;}}.cover-stat-value{{font-size:18px;}}.cover-stat-label{{font-size:9px;}}.cover-label{{font-size:11px;}}.cover-headshots{{gap:16px;margin-top:16px;}}.cover-headshot{{width:50px;height:50px;}}.pdf-float-btn{{padding:10px 14px;font-size:0;bottom:14px;right:14px;}}.pdf-float-btn svg{{width:22px;height:22px;}}.metrics-grid,.metrics-grid-4{{grid-template-columns:1fr;}}.metric-card{{padding:12px 10px;}}.metric-value{{font-size:20px;}}.section{{padding:24px 12px;}}.section-title{{font-size:20px;}}.footer{{padding:24px 12px;}}.footer-team{{gap:16px;}}.toc-nav{{padding:0 4px;}}.toc-nav a{{font-size:8px;padding:10px 4px;letter-spacing:0;}}.leaflet-map{{height:240px;}}}}
@media print{{
@page{{size:letter landscape;margin:0.4in 0.5in;}}
.pdf-float-btn,.toc-nav,.leaflet-map,.embed-map-wrap,.embed-map-caption,.embed-map-fallback{{display:none !important;}}
.map-fallback{{display:block !important;}}
body{{font-size:11px;line-height:1.5;color:#222;}}
p{{font-size:11px;line-height:1.5;margin-bottom:10px;orphans:3;widows:3;}}

.cover{{min-height:7.5in;padding:0;page-break-after:always;display:flex;align-items:center;justify-content:center;}}
.cover-bg{{filter:brightness(0.35);-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.cover-content{{padding:30px 60px 24px;max-width:100%;}}
.cover-logo{{width:220px;margin-bottom:14px;}}
.cover-label{{font-size:10px;letter-spacing:2px;margin-bottom:8px;}}
.cover-title{{font-size:32px;margin-bottom:6px;}}
.cover-subtitle{{font-size:16px;margin-bottom:12px;}}
.cover-stats{{gap:24px;margin-bottom:14px;}}
.cover-stat-value{{font-size:20px;}}
.cover-stat-label{{font-size:8px;letter-spacing:1px;}}
.client-greeting{{font-size:13px;margin-top:10px;}}
.cover-headshots{{margin-top:14px;gap:28px;display:none;}}

.section{{padding:12px 0;max-width:100%;}}
.section-title{{font-size:20px;margin-bottom:3px;}}
.section-subtitle{{font-size:9px;letter-spacing:1px;margin-bottom:8px;}}
.section-divider{{margin-bottom:12px;height:2px;}}
.sub-heading{{font-size:14px;margin:14px 0 8px;}}

#track-record{{page-break-before:auto;}}
#investment{{page-break-before:always;}}
#location{{page-break-before:auto;}}
#property-info{{page-break-before:auto;}}
#development{{page-break-before:always;}}
#adu-opportunity{{page-break-before:always;}}
#sale-comps{{page-break-before:always;}}
#on-market{{page-break-before:auto;}}
#rent-comps{{page-break-before:auto;}}
#financials{{page-break-before:always;}}
.footer{{page-break-before:always;padding:24px 40px;}}

.metrics-grid,.metrics-grid-4{{page-break-inside:avoid;}}
.metric-card{{page-break-inside:avoid;}}
.highlight-box,.buyer-profile,.condition-note,.broker-insight{{page-break-inside:avoid;}}
.os-two-col{{page-break-inside:avoid;grid-template-columns:55% 45%;gap:16px;}}.os-right{{font-size:9.5px;line-height:1.35;}}.os-right p{{margin-bottom:3px;}}.os-right h3{{font-size:11px;margin:0 0 6px;}}
.loc-grid{{display:grid;grid-template-columns:58% 42%;gap:16px;page-break-inside:avoid;align-items:start;}}.loc-left p{{font-size:9.5px;line-height:1.35;margin-bottom:5px;}}.loc-wide-map{{height:250px;margin-top:8px;}}.loc-wide-map img{{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}.loc-right .info-table td{{padding:3px 8px;font-size:10px;}}.loc-right .info-table{{margin-bottom:0;}}
.tr-map-print{{display:block;width:100%;height:260px;border-radius:4px;overflow:hidden;margin-bottom:10px;}}.tr-map-print img{{width:100%;height:100%;object-fit:cover;object-position:center;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}.tr-page2{{page-break-before:always;}}.tr-tagline{{font-size:14px;padding:10px 16px;margin-bottom:10px;}}.tr-service-quote h3{{font-size:13px;margin-bottom:4px;}}.tr-service-quote p{{font-size:10px;line-height:1.45;margin-bottom:6px;}}.tr-mission{{padding:12px 16px;margin-bottom:14px;}}.tr-mission h3{{font-size:13px;margin-bottom:6px;}}.tr-mission p{{font-size:10px;line-height:1.4;margin-bottom:5px;}}
.bio-grid{{gap:16px;margin:12px 0;}}.bio-headshot{{width:60px;height:60px;}}.bio-name{{font-size:14px;}}.bio-title{{font-size:9px;}}.bio-text{{font-size:10px;line-height:1.4;}}.costar-badge{{padding:12px 16px;margin:14px auto;}}.costar-badge-title{{font-size:16px;}}.costar-badge-sub{{font-size:10px;}}.press-strip{{padding:10px 16px;margin:10px 0;gap:16px;}}.press-strip-label{{font-size:8px;}}.press-logo{{font-size:10px;}}
#marketing{{page-break-before:always;}}.mkt-quote{{padding:10px 16px;margin:10px 0;font-size:11px;}}.mkt-channels{{gap:12px;margin-top:12px;}}.mkt-channel{{padding:10px 14px;}}.mkt-channel h4{{font-size:11px;margin-bottom:5px;}}.mkt-channel li{{font-size:9.5px;line-height:1.4;margin-bottom:2px;}}
#performance{{page-break-before:always;}}.perf-grid{{gap:12px;margin-top:12px;}}.perf-card{{padding:10px 14px;}}.perf-card h4{{font-size:11px;margin-bottom:5px;}}.perf-card li{{font-size:9.5px;line-height:1.4;margin-bottom:2px;}}.platform-strip{{padding:8px 14px;margin-top:14px;gap:12px;}}.platform-strip-label{{font-size:8px;}}.platform-name{{font-size:9px;}}
#investment{{page-break-after:always;}}.inv-split{{grid-template-columns:50% 50%;gap:14px;}}.inv-text p{{font-size:9.5px;line-height:1.4;margin-bottom:5px;}}.inv-logo{{width:140px;margin-top:8px;}}.inv-photo{{height:220px;}}.inv-highlights{{padding:10px 14px;}}.inv-highlights h4{{font-size:10px;}}.inv-highlights li{{font-size:8.5px;line-height:1.3;margin-bottom:2px;}}.inv-left .metrics-grid-4{{gap:6px;margin-bottom:8px;}}
#prop-details{{page-break-before:always;}}.prop-tables-bottom{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:10px;}}.prop-tables-bottom table{{font-size:9px;margin-bottom:6px;}}.prop-tables-bottom th{{font-size:7.5px;padding:3px 6px;}}.prop-tables-bottom td{{padding:3px 6px;font-size:9px;}}.prop-tables-bottom .sub-heading{{font-size:11px;margin:0 0 6px;}}
.buyer-split{{grid-template-columns:1fr 1fr;gap:16px;page-break-inside:avoid;}}.buyer-profile li{{font-size:10.5px;line-height:1.5;padding:5px 0;}}.buyer-objections .obj-item{{margin-bottom:10px;}}.buyer-objections .obj-q{{font-size:11.5px;margin-bottom:3px;}}.buyer-objections .obj-a{{font-size:10px;line-height:1.45;}}.buyer-photo{{height:220px;margin-top:12px;border-radius:4px;overflow:hidden;}}.buyer-photo img{{width:100%;height:100%;object-fit:cover;object-position:center;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.price-reveal{{page-break-before:always;}}
table{{page-break-inside:auto;font-size:10.5px;margin-bottom:12px;}}
thead{{display:table-header-group;}}
tr{{page-break-inside:avoid;}}
th{{padding:4px 8px;font-size:8.5px;}}
td{{padding:4px 8px;}}
h2,h3,.section-title,.sub-heading{{page-break-after:avoid;}}

.narrative{{column-count:2;column-gap:24px;column-rule:1px solid #e0e0e0;}}
.narrative p{{font-size:10.5px;line-height:1.45;margin-bottom:8px;}}

.info-table td{{padding:4px 8px;font-size:10.5px;}}
.table-scroll{{overflow:visible;}}
.table-scroll table{{min-width:0 !important;width:100%;}}

.photo-grid{{gap:6px;margin-bottom:12px;}}
.photo-grid img{{height:160px;}}
.adu-img-wrap{{margin-bottom:10px;}}
.adu-img-wrap img{{max-height:240px;width:auto;margin:0 auto;display:block;}}

.metrics-grid{{grid-template-columns:repeat(3,1fr);}}
.metrics-grid-4{{grid-template-columns:repeat(4,1fr);}}
.metrics-grid,.metrics-grid-4{{gap:8px;margin-bottom:12px;}}
.metric-card{{padding:8px 6px;border:1px solid #ddd;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.metric-value{{font-size:18px;}}
.metric-label{{font-size:8px;margin-top:2px;}}
.metric-sub{{font-size:7px;}}

.highlight-box{{padding:10px 14px;margin:10px 0;}}
.highlight-box h4{{font-size:11px;margin-bottom:5px;}}
.highlight-box li{{font-size:10px;margin-bottom:3px;line-height:1.4;}}
.buyer-profile{{padding:10px 14px;margin:10px 0;}}
.buyer-profile-label{{font-size:10px;margin-bottom:6px;}}
.buyer-profile li{{padding:4px 0;font-size:10px;line-height:1.4;}}
.condition-note{{padding:8px 12px;margin:10px 0;font-size:10px;line-height:1.45;}}

.two-col{{gap:14px;margin-bottom:12px;}}
.img-float-right{{float:right;width:40%;margin:0 0 10px 14px;}}
.img-float-right img{{max-height:200px;width:auto;}}
.price-reveal .condition-note{{padding:6px 10px;margin:8px 0;font-size:9.5px;line-height:1.35;}}
.price-reveal .condition-note p{{font-size:9.5px;line-height:1.35;}}

.footer-logo{{width:120px;margin-bottom:12px;}}
.footer-headshot{{width:50px;height:50px;}}
.footer-name{{font-size:13px;}}
.footer-title{{font-size:10px;}}
.footer-contact{{font-size:10px;line-height:1.6;}}
.footer-office{{font-size:10px;}}
.footer-disclaimer{{font-size:8px;}}
}}
</style>
</head>
<body>
""")

# COVER (full-bleed hero background, headshots)
html_parts.append(f"""
<div class="cover">
<div class="cover-bg" style="background-image:url('{IMG['hero']}');"></div>
<div class="cover-content">
<img src="{IMG['logo']}" class="cover-logo" alt="LAAA Team">
<div class="cover-label">Confidential Broker Opinion of Value</div>
<div class="cover-title">420-428 W Stocker Street</div>
<div class="cover-address" style="font-size:20px;font-weight:300;margin-bottom:28px;color:rgba(255,255,255,0.8);">Glendale, California 91202</div>
<div class="gold-line" style="width:80px;margin:0 auto 24px;"></div>
<div class="cover-stats">
<div class="cover-stat"><span class="cover-stat-value">27</span><span class="cover-stat-label">Units</span></div>
<div class="cover-stat"><span class="cover-stat-value">22,674</span><span class="cover-stat-label">Square Feet</span></div>
<div class="cover-stat"><span class="cover-stat-value">1953/1954</span><span class="cover-stat-label">Year Built</span></div>
<div class="cover-stat"><span class="cover-stat-value">1.11 Ac</span><span class="cover-stat-label">Acres</span></div>
</div>
<p class="client-greeting" id="client-greeting"></p>
<div class="cover-headshots">
<div class="cover-headshot-wrap">
<img class="cover-headshot" src="{IMG['glen']}" alt="Glen Scher">
<div class="cover-headshot-name">Glen Scher</div>
<div class="cover-headshot-title">SMDI</div>
</div>
<div class="cover-headshot-wrap">
<img class="cover-headshot" src="{IMG['filip']}" alt="Filip Niculete">
<div class="cover-headshot-name">Filip Niculete</div>
<div class="cover-headshot-title">SMDI</div>
</div>
</div>
<p style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:8px;">February 2026</p>
<p style="font-size:11px;letter-spacing:2px;color:rgba(255,255,255,0.35);margin-top:8px;text-transform:uppercase;">NYSE: MMI</p>
</div>
</div>
""")

# TOC NAV (updated section order)
html_parts.append(f"""
<nav class="toc-nav" id="toc-nav">
<a href="#track-record">Track Record</a>
<a href="#marketing">Marketing</a>
<a href="#investment">Investment</a>
<a href="#location">Location</a>
<a href="#prop-details">Property</a>
<a href="#development">Development</a>
<a href="#adu-opportunity">ADU</a>
<a href="#sale-comps">Sale Comps</a>
<a href="#on-market">On-Market</a>
<a href="#rent-comps">Rent Comps</a>
<a href="#financials">Financials</a>
<a href="#contact">Contact</a>
</nav>
<a href="{PDF_LINK}" class="pdf-float-btn" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zm-1 13l-4-4h3V9h2v4h3l-4 4z"/></svg>Download PDF</a>
""")

# TRACK RECORD — Page 1: Results & Capabilities, Page 2: Our Team
html_parts.append(f"""
<div class="section section-alt" id="track-record">
<div class="section-title">Team Track Record</div>
<div class="section-subtitle">LA Apartment Advisors at Marcus &amp; Millichap</div>
<div class="section-divider"></div>

<div class="tr-tagline">LAAA Team of Marcus &amp; Millichap: Expertise, Execution, Excellence.</div>

<div class="metrics-grid metrics-grid-4">
<div class="metric-card"><span class="metric-value">501</span><span class="metric-label">Closed Transactions</span><span class="metric-sub">All-Time</span></div>
<div class="metric-card"><span class="metric-value">$1.6B</span><span class="metric-label">Total Sales Volume</span><span class="metric-sub">All-Time</span></div>
<div class="metric-card"><span class="metric-value">5,000+</span><span class="metric-label">Units Sold</span><span class="metric-sub">All-Time</span></div>
<div class="metric-card"><span class="metric-value">34</span><span class="metric-label">Median Days on Market</span><span class="metric-sub">Apartments</span></div>
</div>

<div class="embed-map-wrap"><iframe src="https://www.google.com/maps/d/u/0/embed?mid=1ewCjzE3QX9p6m2MqK-md8b6fZitfIzU&ehbc=2E312F" allowfullscreen loading="lazy"></iframe></div>
<div class="embed-map-caption">All-Time Closings Map  -  LA Apartment Advisors</div>
<div class="embed-map-fallback">View our interactive closings map at <strong>www.LAAA.com</strong></div>
<div class="tr-map-print"><img src="{IMG['closings_map']}" alt="LAAA Team All-Time Closings Map - LA County"></div>

<div class="tr-service-quote">
<h3>We Didn&rsquo;t Invent Great Service, We Just Work Relentlessly to Provide It</h3>
<p>With over $1.6 billion in sales volume and 500+ closed transactions since 2013, the LA Apartment Advisors (LAAA Team) strive to offer an uncompromising, transparent and elevated real estate experience within the procurement and disposition of multifamily property and land for multifamily development throughout Los Angeles county.</p>
</div>

<p>Over <strong>60% of all Marcus &amp; Millichap transactions involve a 1031 exchange</strong>, creating a perpetual buyer pipeline that benefits every LAAA listing. This exchange network, combined with M&amp;M's proprietary MNet buyer-matching system across 80+ offices and 1,700+ agents nationally, delivers a level of market exposure and deal execution that competitors cannot replicate. Half of our apartment listings sell in under 5 weeks.</p>

<div class="tr-page2">

<div class="tr-mission">
<h3>LAAA Team Mission Statement</h3>
<p>At LAAA Team, we are dedicated to delivering expert multifamily brokerage services in Los Angeles, helping investors navigate the market with precision, strategy, and results-driven execution. With over 500 closed transactions and $1.6B in total sales volume, our team thrives on providing data-driven insights, strategic deal structuring, and hands-on client service to maximize value for our clients.</p>
<p>Founded by Glen Scher and Filip Niculete, LAAA Team operates with a commitment to transparency, efficiency, and unmatched market expertise. We take a relationship-first approach, guiding property owners, investors, and developers through every stage of acquisition, disposition, and asset repositioning.</p>
<p>Our mission is simple: To be the most trusted and results-oriented multifamily advisors in Los Angeles, leveraging deep market knowledge, innovative technology, and a proactive deal-making strategy to drive long-term success for our clients.</p>
</div>

<div class="bio-grid">
<div class="bio-card">
<img id="bio-glen-headshot" class="bio-headshot" src="{IMG['glen']}" alt="Glen Scher">
<div>
<div class="bio-name">Glen Scher</div>
<div class="bio-title">Senior Managing Director Investments</div>
<div class="bio-text">Senior Managing Director at Marcus &amp; Millichap and co-founder of the LAAA Team. Over 500 transactions and $1.6B in closed sales across LA and the Ventura &amp; Santa Barbara counties, consistently closing 40+ deals per year. Glen joined M&amp;M in 2014 after graduating from UC Santa Barbara with a degree in Economics. Before real estate, he was a Division I golfer at UCSB, earning three individual titles, a national top-50 ranking, and UCSB Male Athlete of the Year.</div>
</div>
</div>
<div class="bio-card">
<img id="bio-filip-headshot" class="bio-headshot" src="{IMG['filip']}" alt="Filip Niculete">
<div>
<div class="bio-name">Filip Niculete</div>
<div class="bio-title">Senior Managing Director Investments</div>
<div class="bio-text">Senior Managing Director at Marcus &amp; Millichap and co-founder of the LAAA Team. Together, Glen and Filip have closed over $1.6B in transactions and consistently lead the market in inventory. Born in Romania and raised in the San Fernando Valley, Filip studied Finance at San Diego State University and joined M&amp;M in 2011. He has built a reputation for execution, integrity, and relentless work ethic across 15 years in Los Angeles multifamily.</div>
</div>
</div>
</div>

<div class="costar-badge">
<div class="costar-badge-title">#1 Most Active Multifamily Sales Team in LA County</div>
<div class="costar-badge-sub">CoStar &bull; 2019, 2020, 2021 &bull; #4 in California</div>
</div>

<div class="condition-note" style="margin-top:20px;">
<div class="condition-note-label">Key Achievements</div>
<p style="font-size:13px; line-height:1.8;">
&bull; <strong>Chairman's Club</strong>  -  Marcus &amp; Millichap's top-tier annual honor (Glen: 2021; Filip: 2018, 2021)<br>
&bull; <strong>National Achievement Award</strong>  -  Glen: 5 years; Filip: 8 consecutive years<br>
&bull; <strong>Sales Recognition Award</strong>  -  Glen: 10 consecutive years; Filip: 12 years total<br>
&bull; <strong>Traded.co National Rankings</strong>  -  Glen Scher: #8 Deal Junkies, #8 Hot List, #8 Rising Talent<br>
&bull; <strong>Connect CRE Next Generation Award</strong>  -  Filip Niculete (2019)<br>
&bull; <strong>SFVBJ Rookie of the Year</strong>  -  Glen Scher
</p>
</div>

<div class="press-strip">
<span class="press-strip-label">As Featured In</span>
<span class="press-logo">BISNOW</span>
<span class="press-logo">YAHOO FINANCE</span>
<span class="press-logo">CONNECT CRE</span>
<span class="press-logo">SFVBJ</span>
<span class="press-logo">THE PINNACLE LIST</span>
</div>

</div>
</div>
""")

# ==================== OUR MARKETING APPROACH (standard template, same for every BOV) ====================
html_parts.append("""
<div class="section" id="marketing">
<div class="section-title">Our Marketing Approach</div>
<div class="section-subtitle">How We Market Your Listing</div>
<div class="section-divider"></div>

<div class="metrics-grid-4">
<div class="metric-card"><span class="metric-value">30,000+</span><span class="metric-label">Emails Sent</span><span class="metric-sub">Per Listing</span></div>
<div class="metric-card"><span class="metric-value">10,000+</span><span class="metric-label">Online Views</span><span class="metric-sub">Per Listing</span></div>
<div class="metric-card"><span class="metric-value">3.7</span><span class="metric-label">Average Offers</span><span class="metric-sub">Per Listing</span></div>
<div class="metric-card"><span class="metric-value">18</span><span class="metric-label">Days to Escrow</span><span class="metric-sub">Average</span></div>
</div>

<div class="mkt-quote">
<p>"We are <strong>PROACTIVE</strong> marketers, not reactive. We don't list online and wait for calls. We pick up the phone, call every probable buyer, and explain why your property is a good investment for them."</p>
</div>

<div class="mkt-channels">
<div class="mkt-channel">
<h4>Direct Phone Outreach</h4>
<ul>
<li><strong>30+ probable buyers</strong> called directly per listing</li>
<li><strong>1,500 cold calls per week</strong> across our team of 8 agents</li>
<li>Focus on 1031 exchange buyers, recent purchasers, and nearby property owners</li>
</ul>
</div>
<div class="mkt-channel">
<h4>Email Campaigns</h4>
<ul>
<li><strong>30,000+ verified</strong> investor and broker email addresses</li>
<li><strong>~8,000 unique opens</strong> per "Just Listed" email blast</li>
<li><strong>~800 clicks</strong> per campaign downloading the full marketing package</li>
</ul>
</div>
<div class="mkt-channel">
<h4>Online Platforms</h4>
<ul>
<li><strong>9 listing platforms</strong> with highest-tier exposure on each</li>
<li><strong>10,000+ views per listing</strong> across all platforms combined</li>
<li>Custom profile created on MLS, CoStar, LoopNet, Crexi, Brevitas, Redfin, M&amp;M, LAAA.com, and ApartmentBuildings.com</li>
</ul>
</div>
<div class="mkt-channel">
<h4>Additional Channels</h4>
<ul>
<li><strong>"Just Listed" postcards</strong> mailed to nearby property owners</li>
<li><strong>Social media</strong> across Facebook, LinkedIn, Instagram, and X</li>
<li><strong>Current inventory attachment</strong> sent ~25 times/day by all team members to active buyers</li>
</ul>
</div>
</div>

</div>
""")

# ==================== LISTING PERFORMANCE (standard template, same for every BOV) ====================
html_parts.append("""
<div class="section section-alt" id="performance">
<div class="section-title">Listing Performance</div>
<div class="section-subtitle">Historical Results Across 500+ Listings</div>
<div class="section-divider"></div>

<div class="metrics-grid-4">
<div class="metric-card"><span class="metric-value">97.6%</span><span class="metric-label">Average SP/LP</span><span class="metric-sub">Sale Price to List Price</span></div>
<div class="metric-card"><span class="metric-value">21%</span><span class="metric-label">Sell At or Above</span><span class="metric-sub">Asking Price</span></div>
<div class="metric-card"><span class="metric-value">10</span><span class="metric-label">Day Avg Contingency</span><span class="metric-sub">Due Diligence Period</span></div>
<div class="metric-card"><span class="metric-value">61%</span><span class="metric-label">Sellers Do 1031</span><span class="metric-sub">Exchange</span></div>
</div>

<div class="perf-grid">
<div class="perf-card">
<h4>Pricing Accuracy</h4>
<ul>
<li><strong>97.6%</strong> average sale-price-to-list-price ratio</li>
<li><strong>1 in 5 listings</strong> sell at or above the asking price</li>
<li>Our pricing methodology is data-driven and comp-backed</li>
</ul>
</div>
<div class="perf-card">
<h4>Marketing Speed</h4>
<ul>
<li><strong>18 days</strong> average to open escrow after hitting the market</li>
<li><strong>17.5%</strong> of our listings sell in the first week</li>
<li><strong>3.7 signed offers</strong> per listing on average</li>
</ul>
</div>
<div class="perf-card">
<h4>Contract Strength</h4>
<ul>
<li><strong>10-day average</strong> contingency period</li>
<li>We almost never allow a loan or appraisal contingency</li>
<li><strong>Less than 60 days</strong> average escrow timeframe</li>
<li><strong>10%</strong> of our listings open escrow with zero contingencies</li>
</ul>
</div>
<div class="perf-card">
<h4>Exchange Expertise</h4>
<ul>
<li><strong>61%</strong> of our sellers complete a 1031 exchange</li>
<li><strong>29%</strong> of listings sell to a 1031 exchange buyer</li>
<li><strong>76%</strong> of our transactions involve at least one exchange party</li>
</ul>
</div>
</div>

<div class="platform-strip">
<span class="platform-strip-label">Advertised On</span>
<span class="platform-name">MLS</span>
<span class="platform-name">CoStar</span>
<span class="platform-name">LoopNet</span>
<span class="platform-name">Crexi</span>
<span class="platform-name">Brevitas</span>
<span class="platform-name">Redfin</span>
<span class="platform-name">Marcus &amp; Millichap</span>
<span class="platform-name">LAAA.com</span>
<span class="platform-name">ApartmentBuildings.com</span>
</div>

</div>
""")

# ==================== INVESTMENT OVERVIEW (Bedford St. split layout) ====================
html_parts.append(f"""
<div class="section" id="investment">
<div class="inv-split">
<div class="inv-left">
<div class="section-title">Investment Overview</div>
<div class="section-subtitle">Stocker Gardens  -  420-428 W Stocker St, Glendale 91202</div>
<div class="section-divider"></div>

<div class="metrics-grid-4">
<div class="metric-card"><span class="metric-value">27</span><span class="metric-label">Total Units</span></div>
<div class="metric-card"><span class="metric-value">22,674</span><span class="metric-label">Building SF</span></div>
<div class="metric-card"><span class="metric-value">1.11 Ac</span><span class="metric-label">Combined Lot</span></div>
<div class="metric-card"><span class="metric-value">1953/54</span><span class="metric-label">Year Built</span></div>
</div>

<div class="inv-text">
<p>The LAAA Team of Marcus &amp; Millichap is pleased to present <strong>Stocker Gardens</strong>, a 27-unit multifamily portfolio located at 420-428 W Stocker St in Glendale's premier Glenwood neighborhood. The offering consists of two adjacent parcels totaling 1.11 acres with five wood-frame buildings, including a 4-bedroom Craftsman front house and 26 apartment units. The property delivers approximately 19% rental upside, significant ADU development potential under SB 1211, and over $117,000 in recently completed capital improvements, making it a well-positioned value-add opportunity in the Glendale submarket.</p>

<p>Built in 1953/1954, Stocker Gardens encompasses 22,674 square feet of gross building area across 27 units: one 4BR/3BA Craftsman house (2,500 SF), 24 two-bedroom/one-bath apartments (750 SF each), and two one-bedroom/one-bath apartments (650 SF each). The combined lot measures approximately 160 feet wide by 300 feet deep, creating a rare 48,353 SF site with approximately 8,000 SF of rear parking area ideally suited for ADU infill. All apartment units are individually metered for gas and electricity, minimizing owner utility exposure. Current gross scheduled rent totals $740,748 annually, with pro forma potential of $878,280, representing approximately $137,500 in annual rental upside achievable through natural tenant turnover and light interior renovations.</p>

<p>The seller has invested heavily in the property's physical plant, completing over $117,000 in capital improvements in 2024 alone, including plumbing and electrical upgrades, deck reconstruction, window replacements, HVAC repairs, exterior painting, and appliance replacements. Units A through H on the 420 parcel were repiped in 2005, and the 428 building's walkway and stair surfaces were recoated with fiberglass in 2023-2024 with all inspections passed. These completed improvements meaningfully reduce a buyer's near-term capital exposure and allow for immediate focus on income growth through unit turns and ADU construction.</p>
</div>
<img class="inv-logo" src="{IMG['logo']}" alt="LAAA Team">
</div>

<div class="inv-right">
<div class="inv-photo"><img src="{IMG['grid1']}" alt="420 Stocker St - Property Photo"></div>
<div class="inv-highlights">
<h4>Investment Highlights</h4>
<ul>
<li><strong>19% Rental Upside Through Turnover</strong>  -  In-place rents are approximately 19% below full market potential, with gross scheduled rent of $740,748 growing to a pro forma of $878,280. Vacancy decontrol under California law allows rent resets to market upon unit turnover with no cap on initial asking rent for new tenants.</li>
<li><strong>$117,000+ in 2024 Capital Improvements</strong>  -  Plumbing/electrical upgrades ($43,000), deck reconstruction ($38,500), window replacements ($10,700), exterior painting ($10,000), appliance replacements ($9,000), and HVAC repairs ($4,500).</li>
<li><strong>SB 1211 ADU Potential (Up to 6 Units)</strong>  -  ~8,000 SF of rear parking area across both parcels can accommodate up to 6 detached two-story ADUs with by-right ministerial approval, no parking replacement required. Estimated ~$127,000 annual NOI and ~54% ROI.</li>
<li><strong>1.11-Acre Combined Site on Two Parcels</strong>  -  Each parcel measures 80 ft by 300 ft, creating a combined 160 ft x 300 ft site that is exceptionally large for a Glendale multifamily property.</li>
<li><strong>R-1250 Zoning with Development Headroom</strong>  -  Current FAR of just 0.47 vs. 1.2 maximum, leaving over 35,000 SF of additional buildable area. Existing 27 units sit below the 38-unit density cap.</li>
<li><strong>Glendale Regulatory Advantage</strong>  -  No local rent board, no unit registration, no transfer tax. City operates under AB 1482 statewide cap (5% + CPI, max 10%) with relocation triggers only above 7%.</li>
<li><strong>34+ Year Ownership with Prop 13 Basis</strong>  -  Assessed value ~$4.24M reflects 34+ years of Prop 13 protection. Current taxes ~$49,300 will be reassessed at close of escrow based on sale price.</li>
<li><strong>Prime Location with 88 Walk Score</strong>  -  North of Glenoaks Blvd, near top-rated Glendale Unified schools, SR-134 freeway access, and Burbank entertainment studios.</li>
</ul>
</div>
</div>
</div>
</div>
""")

# ==================== LOCATION OVERVIEW (3-box: paragraphs left, table right, wide map bottom) ====================
loc_wide_map_html = f'<div class="loc-wide-map"><img src="{IMG["loc_map"]}" alt="Property Location - 420-428 W Stocker St, Glendale"></div>' if IMG.get("loc_map") else ''
html_parts.append(f"""
<div class="section section-alt" id="location">
<div class="section-title">Location Overview</div>
<div class="section-subtitle">Glenwood Submarket  -  Northwest Glendale, 91202</div>
<div class="section-divider"></div>

<div class="loc-grid">
<div class="loc-left">
<p>Stocker Gardens is situated in Glendale's Glenwood neighborhood, north of Glenoaks Boulevard in the highly desirable 91202 zip code. The location has been described by competing listing agents as "arguably the best location in Glendale," nestled just below multimillion-dollar hillside homes while remaining steps from daily conveniences including Starbucks, cafes, and neighborhood shops. Three schools are within one block walking distance, and the property benefits from the Glendale Unified School District, one of the highest-performing districts in Los Angeles County. The Walk Score of 88 (Very Walkable) reflects the neighborhood's strong access to everyday amenities on foot.</p>

<p>The property is positioned within a well-established rental corridor along W Stocker Street, surrounded by similar vintage multifamily properties ranging from 5 to 33 units. Regional access is excellent via the SR-134 Freeway (Pacific Avenue exit, approximately half a mile south), connecting residents to Burbank, Pasadena, and the greater LA basin. Downtown Glendale, with its concentration of retail, dining, and entertainment at the Americana at Brand and Glendale Galleria, is a 4-minute drive or 7-minute bike ride. The Glendale Transportation Center provides Metrolink commuter rail service to Downtown LA and points throughout the region. Employment drivers include proximity to major entertainment studios in neighboring Burbank, including Warner Bros., Walt Disney Studios, and DreamWorks, which sustain consistent tenant demand throughout northwest Glendale.</p>

<p>From a hazard and environmental standpoint, the property carries a low risk profile. It is not located in a fire hazard severity zone (confirmed by city permit records), sits in FEMA Zone X (shaded) indicating moderate flood risk with no federal flood insurance requirement, and has no known environmental contamination per DTSC and GeoTracker records. Glendale does not have a mandatory soft-story retrofit ordinance, though buyers may wish to evaluate voluntary seismic improvements given the 1953/1954 wood-frame construction.</p>
</div>
<div class="loc-right">
<table class="info-table">
<tr><td>Walk Score</td><td>88 (Very Walkable)</td></tr>
<tr><td>Transit Score</td><td>44 (Some Transit)</td></tr>
<tr><td>Bike Score</td><td>59 (Bikeable)</td></tr>
<tr><td>School District</td><td>Glendale Unified (top-performing)</td></tr>
<tr><td>Nearest Freeway</td><td>SR-134 (~0.5 mi south)</td></tr>
<tr><td>Submarket</td><td>Glenwood (MLS Area 1255)</td></tr>
<tr><td>Zip Code</td><td>91202 (Northwest Glendale)</td></tr>
<tr><td>FEMA Flood Zone</td><td>Zone X (Shaded)</td></tr>
<tr><td>Fire Hazard Zone</td><td>Not in VHFHSZ</td></tr>
<tr><td>Environmental</td><td>No known contamination</td></tr>
</table>
</div>
</div>
{loc_wide_map_html}

</div>
""")

# ==================== PROPERTY DETAILS (consolidated: all tables on one page) ====================
html_parts.append("""
<div class="section" id="prop-details">
<div class="section-title">Property Details</div>
<div class="section-subtitle">420-428 W Stocker St, Glendale, CA 91202</div>
<div class="section-divider"></div>

<div class="two-col">
<table class="info-table">
<tr><td>Address</td><td>420-428 W Stocker St, Glendale, CA 91202</td></tr>
<tr><td>APN</td><td>5636-001-020 (420) / 5636-001-021 (428)</td></tr>
<tr><td>Year Built</td><td>1953 / 1954</td></tr>
<tr><td>Units</td><td>27 (1 house + 24x 2BR + 2x 1BR)</td></tr>
<tr><td>Building SF</td><td>22,674</td></tr>
<tr><td>Lot Size</td><td>1.11 Acres (48,353 SF)</td></tr>
<tr><td>Lot Dimensions</td><td>160 ft x 300 ft (combined)</td></tr>
<tr><td>Per Parcel</td><td>80 ft x 300 ft each</td></tr>
<tr><td>Construction</td><td>Wood Frame</td></tr>
<tr><td>Buildings</td><td>5</td></tr>
</table>
<table class="info-table">
<tr><td>Zoning</td><td>R-1250 (High Density Residential)</td></tr>
<tr><td>FAR</td><td>0.47 current (1.2 max)</td></tr>
<tr><td>Rent Control</td><td>AB 1482 + Glendale Ord. 5922</td></tr>
<tr><td>Stories</td><td>1-2</td></tr>
<tr><td>Parking</td><td>Surface + Carport</td></tr>
<tr><td>Rear Parking Area</td><td>~50 ft x 160 ft (~8,000 SF)</td></tr>
<tr><td>School District</td><td>Glendale Unified</td></tr>
<tr><td>FEMA Flood Zone</td><td>Zone X (Shaded)</td></tr>
<tr><td>Fire Hazard</td><td>Not in VHFHSZ</td></tr>
<tr><td>Submarket</td><td>Glenwood (NW Glendale)</td></tr>
</table>
</div>

<div class="prop-tables-bottom">
<div>
<h3 class="sub-heading" style="margin-top:0;">Building Systems &amp; Capital Improvements</h3>
<table>
<thead><tr><th>System</th><th>Status</th><th>Year</th></tr></thead>
<tbody>
<tr><td>Roof (420 House + Garage)</td><td>Comp shingle</td><td>2012</td></tr>
<tr><td>Roof (428)</td><td>Comp shingle Class A</td><td>2007</td></tr>
<tr><td>Plumbing (420)</td><td>Repiped, Units A-H</td><td>2005</td></tr>
<tr><td>Plumbing (428)</td><td>18 vents, 16 T&P valves</td><td>2004</td></tr>
<tr><td>HVAC</td><td>FAU (420 Unit I); Window units (428)</td><td>Various</td></tr>
<tr><td>Electrical</td><td>Major plumbing/electrical work</td><td>2024</td></tr>
<tr><td>Windows</td><td>Replaced ($10,700)</td><td>2024</td></tr>
<tr><td>Deck/Walkway (428)</td><td>Fiberglass recoat, permitted</td><td>2023-24</td></tr>
<tr><td>Exterior Paint</td><td>Full exterior repaint</td><td>2024</td></tr>
<tr><td>Appliances</td><td>Replacements ($9,005)</td><td>2024</td></tr>
</tbody>
</table>
</div>
<div>
<h3 class="sub-heading" style="margin-top:0;">Regulatory &amp; Compliance</h3>
<table>
<thead><tr><th>Item</th><th>Status</th></tr></thead>
<tbody>
<tr><td>Rent Control</td><td>AB 1482 + Glendale Ord. 5922</td></tr>
<tr><td>Just Cause Eviction</td><td>Required (pre-1995 construction)</td></tr>
<tr><td>Rent Increase Cap</td><td>5% + CPI (max 10%); relocation if >7%</td></tr>
<tr><td>Code Violations</td><td>None on file</td></tr>
<tr><td>Soft-Story Retrofit</td><td>Not mandatory in Glendale</td></tr>
<tr><td>Seismic</td><td>Standard SoCal zone</td></tr>
<tr><td>Protected Tree</td><td>1 coast live oak (420 parcel)</td></tr>
</tbody>
</table>
</div>
</div>

<h3 class="sub-heading">Transaction History</h3>
<table>
<thead><tr><th>Date</th><th>Event</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>1991</td><td>Earliest recorded deed</td><td>Gerald family ownership begins</td></tr>
<tr><td>2007</td><td>Family transfer</td><td>Michael A Gerald to Isabelle P Gerald</td></tr>
<tr><td>2015</td><td>Refinance</td><td>Chase, $3,500,000</td></tr>
<tr><td>2022</td><td>Refinance</td><td>Chase, $1,350,000 (420) + $250,000 (428)</td></tr>
<tr class="highlight"><td>2026</td><td>Proposed Sale</td><td>First arms-length sale in 34+ years</td></tr>
</tbody>
</table>

</div>
""")

# ==================== BUYER PROFILE + ANTICIPATED BUYER OBJECTIONS (side-by-side) ====================
html_parts.append(f"""
<div class="section section-alt" id="property-info">
<div class="section-title">Buyer Profile &amp; Anticipated Objections</div>
<div class="section-subtitle">Target Investors &amp; Data-Backed Responses</div>
<div class="section-divider"></div>

<div class="buyer-split">
<div class="buyer-split-left">
<div class="buyer-profile">
<div class="buyer-profile-label">Target Buyer Profile</div>
<ul>
<li><strong>1031 Exchange Investors</strong>  -  Rare scale (27 units) in an institutional-quality 91202 zip code. Immediate cash flow with layered organic upside from rent growth and ADU construction.</li>
<li><strong>Value-Add Operators with ADU Strategy</strong>  -  Push rents to market ($138K/yr upside) and build 6 detached ADUs in the rear parking area (~$127K/yr additional NOI). Total value creation potential of ~$900K+ on ~$1.65M investment.</li>
<li><strong>Local Operators</strong>  -  Self-manage, capture rent upside within 12-24 months, then pursue ADU construction at your own pace.</li>
<li><strong>Family Offices</strong>  -  Premier Glendale location with generational hold appeal. Excess zoning capacity provides long-term densification optionality on 1.11 acres.</li>
</ul>
<p class="bp-closing">Broad appeal across buyer segments supports competitive pricing and a short expected marketing period.</p>
</div>
</div>

<div class="buyer-split-right">
<h3 class="sub-heading" style="margin-top:0;">Anticipated Buyer Objections</h3>
<div class="buyer-objections">

<div class="obj-item">
<p class="obj-q">"$333K per unit is aggressive for 1953 construction. Comps don't support it."</p>
<p class="obj-a">The primary anchor comp at 617 W Stocker St (same street, all 2BR/1BA units, same zip code) sold at $394K/unit in February 2025. The subject at $333K/unit represents a 15% discount to this direct comp. Additionally, 1244 N Columbus Ave (same 1953 vintage) traded at $304K/unit but was 83% one-bedroom units vs. the subject's 89% two-bedroom mix. The subject's 1.11-acre lot with 8,000 SF of ADU-buildable area further justifies the basis well below the street comp.</p>
</div>

<div class="obj-item">
<p class="obj-q">"Your pro forma rents at $2,650 for 2BR units are too aggressive."</p>
<p class="obj-a">Three rent comps in the Glenwood submarket support the $2,650 target: 550 W Stocker St ($2,595-$2,695 for 2BR/1BA), 439 W Stocker St ($2,500-$2,750), and 1207 N Columbus Ave ($2,550-$2,800). The pro forma is positioned at the midpoint of the comparable range, not the top. Several recently turned units at these properties have achieved rents above $2,700.</p>
</div>

<div class="obj-item">
<p class="obj-q">"The property is 70+ years old. What about deferred maintenance?"</p>
<p class="obj-a">The current owner invested $117,264 in capital improvements during 2024, including plumbing/electrical work, deck reconstruction, window replacements, HVAC repairs, exterior painting, and appliance replacements. Roofs on all three structures were replaced between 2007 and 2012, and the 420 building was fully repiped in 2005. These completed improvements meaningfully reduce near-term capital exposure for a buyer.</p>
</div>

<div class="obj-item">
<p class="obj-q">"Why should I pay an ADU premium when I still have to build them?"</p>
<p class="obj-a">The $350,000 ADU premium represents approximately 39% of the estimated $896,000 development profit. The buyer retains 61% of the upside even at full ask. The premium reflects the scarcity of 1.1-acre multifamily sites with 8,000 SF of buildable rear area and the near-zero entitlement risk of SB 1211's ministerial approval process. At the trade floor of $8,850,000, the premium drops to $200,000 (22% of profit).</p>
</div>

</div>
</div>
</div>

<div class="buyer-photo"><img src="{IMG['grid2']}" alt="428 Stocker St - Property Photo"></div>

</div>
""")

# ==================== DEVELOPMENT POTENTIAL (REWRITTEN FROM DOCX) ====================
html_parts.append("""
<div class="section" id="development">
<div class="section-title">Development Potential &amp; Land Value Analysis</div>
<div class="section-subtitle">Zoning Capacity, Density Bonus, and Economic Reality</div>
<div class="section-divider"></div>

<p>The subject property consists of two side-by-side parcels totaling 1.11 acres (48,353 SF) in Glendale's R-1250 High Density Residential zone. Each parcel has approximately 80 feet of street frontage on W Stocker Street for a combined total of approximately 160 feet.</p>

<div class="condition-note" style="margin-top:16px;">
<div class="condition-note-label">What This Section Covers</div>
<p style="font-size:14px; line-height:1.7;">In simple terms, this section answers two questions: <strong>Could someone tear this down and build something bigger?</strong> And <strong>would that make financial sense?</strong> The short answer is that tearing down and rebuilding would cost roughly $35 million but create a property worth only $20-22 million - a loss of $13-15 million. The smarter path is adding new units (ADUs) in the rear parking area without disturbing the existing buildings or tenants.</p>
</div>

<h3 class="sub-heading">Part A: What Can Be Built Under Current Zoning</h3>

<p>The R-1250 zone permits 1 dwelling unit per 1,250 SF of lot area. For the combined 48,353 SF site, this yields a base maximum of <strong>38 units</strong> (48,353 / 1,250 = 38.7, rounded down). The table below shows what the zoning code allows versus what exists today:</p>

<div class="table-scroll"><table>
<thead><tr><th>Standard</th><th>R-1250 Limit</th><th>Current</th><th>Source</th></tr></thead>
<tbody>
<tr><td>Maximum Density</td><td>1 DU / 1,250 SF = <strong>38 units</strong></td><td>27 units</td><td>GMC &sect;30.11.030</td></tr>
<tr><td>Maximum Height</td><td><strong>2 stories / 26 ft</strong> (lots &le;90 ft wide)</td><td>2 stories</td><td>GMC &sect;30.11.030, Table 30.11-B</td></tr>
<tr><td>Maximum FAR</td><td>1.2 (58,024 SF)</td><td>0.47 (22,674 SF)</td><td>GMC &sect;30.11.030</td></tr>
<tr><td>Maximum Lot Coverage</td><td>50%</td><td>~30% estimated</td><td>GMC &sect;30.11.030</td></tr>
<tr><td>Min Open Space</td><td>25% permanently landscaped</td><td>TBD</td><td>GMC &sect;30.11.030</td></tr>
<tr><td>Common Outdoor Space</td><td>200 SF/unit (first 25), 150 SF/unit (next 25)</td><td> - </td><td>GMC &sect;30.11.050(C)</td></tr>
<tr><td>Min Unit Size</td><td>600 SF (1BR), 800 SF (2BR), 1,000 SF (3BR)</td><td> - </td><td>GMC &sect;30.11.050(A)</td></tr>
</tbody>
</table></div>

<h4 style="color:#1B3A5C;font-size:15px;margin:20px 0 10px;">The 90-Foot Lot Width Threshold: The Critical Variable</h4>

<p>Glendale's zoning code creates a two-tier system for multifamily development based on lot width. Per GMC &sect;30.11.030 (Table 30.11-B), lots <strong>under 90 feet wide</strong> are limited to <strong>2 stories / 26 feet</strong>, while lots <strong>90 feet or wider</strong> can build up to <strong>3 stories / 36 feet</strong>. "Lot width" is defined as the dimension at the front property line (GMC &sect;30.70).</p>

<p>Each parcel at 420-428 W Stocker has approximately 80 feet of frontage, which falls below the 90-foot threshold. At 80 feet, each individual parcel is capped at 2 stories and 26 feet of height. <strong>This is the single most restrictive constraint on the property's development potential.</strong></p>

<p>The practical impact: a developer working with the two parcels individually would tear down 27 existing units to build a maximum of approximately 38 units in a 2-story configuration - a <strong>net gain of only 11 units</strong>. The 2-story building envelope, not the FAR, is the binding constraint.</p>

<div class="condition-note" style="margin-top:16px;background:#f0f4f8;border-left-color:#1B3A5C;">
<div class="condition-note-label" style="color:#1B3A5C;">Plain-English Summary</div>
<p style="font-size:13px; line-height:1.6;">Because each lot is 80 feet wide (just 10 feet short of the city's 90-foot cutoff), a developer can only build 2-story buildings. That means tearing down 27 apartments to build about 38 - gaining only 11 units. The math does not justify demolition.</p>
</div>

<h4 style="color:#1B3A5C;font-size:15px;margin:20px 0 10px;">Lot Merger Scenario: Unlocking the Third Story</h4>

<p>If both parcels were merged into a single legal lot through a lot line adjustment (per GMC Title 16, Chapter 16.36), the combined lot would have approximately 160 feet of frontage - nearly double the 90-foot threshold. This is an administrative (not discretionary) process handled by the Director of Community Development. The merged parcel must comply with area, width, frontage, and yard requirements of the R-1250 zone; since the merger creates a larger conforming lot, approval is straightforward.</p>

<p>A merged 160-foot lot would unlock three benefits:</p>

<p><strong>1. Height increase from 2 stories / 26 ft to 3 stories / 36 ft.</strong> An additional full story of buildable area across a 48,353 SF lot is a significant increase to the building envelope.</p>

<p><strong>2. Enhanced density.</strong> The code permits additional dwelling units per acre on lots exceeding 90 feet in width. This enhanced density also serves as the base for State Density Bonus calculations per GMC &sect;30.36.030 and &sect;30.35.030, both of which state: "The maximum density for a housing development on a lot that qualifies for additional density based on lot width shall be the highest allowable density." This means the density bonus percentage is applied to the higher base, compounding the benefit.</p>

<p><strong>3. Additional open space tradeoff.</strong> Per GMC &sect;30.31.020, a lot 90+ feet wide with enhanced density must provide an additional 900 SF of open space contiguous to the street front/side setback, plus 20 SF for each foot of lot width beyond 90 feet. At 160 feet: 900 + (70 &times; 20) = 2,300 SF of additional open space.</p>

<p><strong>Key insight:</strong> When the parcels are separate, the height cap (2 stories / 26 ft) is the binding constraint, making it physically impossible to use the full 1.2 FAR. When merged, the third story unlocks enough building volume that FAR (not height) becomes the binding constraint. This shift from a height-constrained envelope to a FAR-constrained envelope represents a meaningful increase in the site's practical development capacity.</p>

<p><em>Important nuance:</em> Independent analysis by Let's Go LA noted that in Glendale, "because density is increased but FAR is not" proportionally for wider lots, "the average unit size is actually driven down, despite being allowed to make the building one story taller." In practice, "many [multi-lot projects] have not maxed out the density, electing to build fewer, but larger units." The parking requirement of 2 subterranean spaces per unit may also cap practical unit count based on achievable garage capacity.</p>

<div class="condition-note" style="margin-top:16px;">
<div class="condition-note-label">Long-Term Optionality, Not Near-Term Strategy</div>
<p style="font-size:14px; line-height:1.7;"><strong>However, this enhanced capacity does not change the fundamental economic conclusion.</strong> As demonstrated in Part C below, even under the most favorable development assumptions the economics produce a $13-15M loss. The lot merger scenario preserves future densification potential for a generational holder - a buyer acquiring both parcels controls 160 feet of continuous R-1250 frontage with 3-story capacity - but the practical value-creation path today remains ADU infill construction in the rear parking area.</p>
</div>

<h3 class="sub-heading">Part B: State Density Bonus Law</h3>

<p>California's Density Bonus Law (Gov. Code &sect;65915) allows developers who include affordable units to receive up to a 50% density bonus above the base zoning allowance. The table below shows what this means in practice for the subject site:</p>

<div class="table-scroll"><table>
<thead><tr><th>Affordability Set-Aside</th><th>Density Bonus</th><th>Max Units (base 38)</th></tr></thead>
<tbody>
<tr><td>5% Very Low Income</td><td>20%</td><td>46</td></tr>
<tr><td>10% Low Income</td><td>20%</td><td>46</td></tr>
<tr><td>15% Very Low Income</td><td>50%</td><td>57</td></tr>
</tbody>
</table></div>

<p><strong>Critical interaction with lot width:</strong> Glendale's code (GMC &sect;30.36.030 and &sect;30.35.030) explicitly provides that the "maximum density for a housing development on a lot that qualifies for additional density based on lot width shall be the highest allowable density." This means a merged 160-foot lot's enhanced density would serve as the base for density bonus calculations, compounding the benefit. The density bonus percentage is applied to the higher base, not the standard base.</p>

<p>Even with a density bonus, the height limit remains a practical constraint for the individual 80-foot parcels (2 stories / 26 ft). For a merged lot, the 3-story / 36-ft envelope provides significantly more room to accommodate bonus units. Density bonus concessions can also include additional height waivers in certain circumstances, potentially pushing a merged project to 4+ stories.</p>

<p><em>Real-world precedent:</em> Glendale has approved density bonus projects with significant concessions. The 515 Pioneer Drive project received height increases from 36 feet (the R-3050 base for lots 90+ feet wide) to 69 feet via automatic density bonus height increases, illustrating how the lot width threshold directly interfaces with state law to enable larger projects.</p>

<p>However, the density bonus requires deed-restricting affordable units for 55 years, fundamentally changing the project economics. SB 423 (extending SB 35) could provide ministerial approval for qualifying affordable projects, but the underlying cost-value gap remains.</p>

<h3 class="sub-heading">Part C: Why Ground-Up Redevelopment Does Not Pencil</h3>

<p>Even under the most favorable assumptions - including a merged lot with 3-story capacity and a 38-unit base project - the economics of demolition and rebuild produce a significant loss. Here is what it would cost to tear down and rebuild:</p>

<div class="table-scroll"><table>
<thead><tr><th>Cost Component</th><th>Amount</th><th>Source</th></tr></thead>
<tbody>
<tr><td>Land basis (at apartment value)</td><td>$9,000,000</td><td>Income analysis</td></tr>
<tr><td>Demolition (27 units, 22,674 SF, 5 buildings)</td><td>~$200,000</td><td>Industry estimate ($8-10/SF)</td></tr>
<tr><td>Hard construction (38 units &times; $430,000)</td><td>$16,340,000</td><td>RAND Corp. April 2025, RR-A3743-1</td></tr>
<tr><td>Soft costs (architecture, engineering, permits - 25%)</td><td>$4,085,000</td><td>RAND 2025: soft costs 25-30%</td></tr>
<tr><td>Municipal development/impact fees (38 &times; $29,000)</td><td>$1,102,000</td><td>RAND 2025: CA avg ~$29K/unit</td></tr>
<tr><td>Tenant relocation (27 units &times; 3 months' rent)</td><td>~$186,000</td><td>Glendale Ord. 5922</td></tr>
<tr><td>Lost rental income (4 years &times; $449,791 NOI)</td><td>$1,799,164</td><td>Current normalized NOI</td></tr>
<tr><td>Financing/carry costs (~5% of hard &times; 3 years)</td><td>~$2,450,000</td><td>Estimated construction loan</td></tr>
<tr style="font-weight:700;background:#FFF8E7;"><td>TOTAL ALL-IN DEVELOPMENT COST</td><td>~$35,160,000</td><td></td></tr>
</tbody>
</table></div>

<p><em>Primary source: Ward, Jason M. &amp; Schlake, Luke, "The High Cost of Producing Multifamily Housing in California," RAND Corporation, RR-A3743-1, April 2025. Key finding: California's average market-rate multifamily production cost is approximately $430,000 per unit - 2.5&times; Texas (~$150K) and nearly 2&times; Colorado (~$240K). Los Angeles metro is among the most expensive submarkets in California.</em></p>

<p>And here is what the finished building would be worth, assuming brand-new Class A rents of $3,250/month per unit:</p>

<div class="table-scroll"><table>
<thead><tr><th>Metric</th><th>Calculation</th><th>Value</th></tr></thead>
<tbody>
<tr><td>Gross rent (38 units &times; $3,250/mo &times; 12)</td><td></td><td>$1,482,000</td></tr>
<tr><td>Less: Vacancy (5%)</td><td></td><td>($74,100)</td></tr>
<tr><td>Less: Operating expenses (35% of gross)</td><td></td><td>($518,700)</td></tr>
<tr><td><strong>Stabilized NOI</strong></td><td></td><td><strong>$889,200</strong></td></tr>
<tr><td>Value at 4.5% cap</td><td>$889,200 / 0.045</td><td><strong>$19,760,000</strong></td></tr>
<tr><td>Value at 4.0% cap</td><td>$889,200 / 0.040</td><td><strong>$22,230,000</strong></td></tr>
<tr style="font-weight:700;background:#FFF8E7;"><td>Loss at 4.5% cap</td><td>$19.76M - $35.16M</td><td><strong>($15,400,000)</strong></td></tr>
<tr style="font-weight:700;background:#FFF8E7;"><td>Loss at 4.0% cap</td><td>$22.23M - $35.16M</td><td><strong>($12,930,000)</strong></td></tr>
</tbody>
</table></div>

<div class="condition-note" style="margin-top:20px;background:#FFF8E7;border-left-color:#C5A258;">
<div class="condition-note-label">Bottom Line</div>
<p style="font-size:14px; line-height:1.7;"><strong>A developer would spend approximately $35.2 million to create a property worth $19.8-$22.2 million.</strong> That is a loss of $13-15 million. Under no reasonable assumption does ground-up redevelopment produce a positive return. Even if a merged lot and third story enabled a more efficient 45-unit project (reducing per-unit costs through economies of scale), the gap between all-in cost and stabilized value remains prohibitive. The existing buildings are the highest-and-best use of this site.</p>
</div>

<h3 class="sub-heading">Part D: Legal &amp; Regulatory Barriers to Demolition</h3>

<p>Beyond the economics, five layers of California and Glendale law create significant barriers to demolishing the existing apartments:</p>

<p><strong>1. SB 330 - Housing Crisis Act (Gov. Code &sect;66300 et seq.):</strong> Prohibits net loss of residential units. All 27 demolished units must be replaced in the new project at the same affordability level. If current tenants are lower-income (likely, given rents of $900-$2,050 for several units), replacement units must be deed-restricted affordable. No demolition permit can be issued until replacement and relocation agreements are executed and recorded with the city.</p>

<p><strong>2. Ellis Act / AB 1399 (Gov. Code &sect;7060 et seq.):</strong> If the owner uses the Ellis Act to withdraw the property from the rental market, the withdrawal date is the latest termination date of any unit - all 27 units must be simultaneously vacated. If any unit is re-rented during the constraint period, the entire property must be returned to the rental market at prior rents.</p>

<p><strong>3. Glendale Tenant Protections (Ordinance 5922):</strong> Just cause eviction is required for all covered units (built before Feb 1, 1995). Relocation assistance of 3 months' rent is payable to each displaced tenant (~$186,000 total for 27 units). Demolition qualifies as just cause only when work costs exceed 8&times; monthly rent per unit and renders the unit uninhabitable for more than 30 days.</p>

<p><strong>4. CEQA:</strong> A 38-unit ground-up project in Glendale would likely require environmental review under the California Environmental Quality Act unless it qualifies for a categorical exemption or streamlined review. Glendale's Design Review process (GMC Chapter 30.47) adds discretionary review, additional time, and the risk of public opposition.</p>

<p><strong>5. SB 423 Limitations:</strong> Even SB 423's ministerial approval path requires affordable housing set-asides (below-market units with 55-year deed restrictions). While this could bypass CEQA and design review, the underlying economic gap ($13-15M loss) remains.</p>

<div class="condition-note" style="margin-top:20px;">
<div class="condition-note-label">Conclusion</div>
<p style="font-size:14px; line-height:1.7;">The combined 160-foot frontage created by merging the two parcels does exceed Glendale's 90-foot lot width threshold, which unlocks a third story (36 ft) and enhanced density. This is a meaningful increase in development capacity compared to the individual 80-foot parcels. However, this enhanced capacity does not change the fundamental economic conclusion. The combination of $430,000+ per-unit construction costs, SB 330 replacement requirements, Ellis Act constraints, and CEQA review make ground-up redevelopment economically irrational under current market conditions. The value of the lot merger is as a <strong>long-term optionality play</strong>, not a near-term development catalyst. The practical path to value creation is ADU infill construction in the existing rear parking area, which requires no tenant displacement, no CEQA review, and no discretionary approval.</p>
</div>

<p style="font-size:11px;color:#888;font-style:italic;margin-top:16px;"><em>Note: This analysis should be verified with the Glendale Planning Department (818-548-3200) to confirm the specific development standards as applied to the subject parcels and the precise lot widths per the recorded surveys.</em></p>

</div>
""")

# ==================== ADU OPPORTUNITY (MASSIVELY EXPANDED) ====================
html_parts.append(f"""
<div class="section section-alt" id="adu-opportunity">
<div class="section-title">SB 1211 ADU Development Opportunity</div>
<div class="section-subtitle">By-Right Value Creation in the Rear Parking Area</div>
<div class="section-divider"></div>

<div class="photo-grid">
<img src="{IMG['adu_aerial']}" alt="Property Photo">
<img src="{IMG['adu_parking']}" alt="Property Photo">
</div>

<p>As shown in the aerial image above, the rear approximately 50 feet of the combined property (highlighted in yellow) currently serves as surface parking for both buildings. This ~8,000 SF area, spanning the full 160-foot width of the combined site, represents the primary buildable zone for ADU construction under California's SB 1211 legislation.</p>

<h3 class="sub-heading">Part A: SB 1211 Legal Framework</h3>

<p>California Senate Bill 1211 (signed by Governor Newsom on September 19, 2024; effective January 1, 2025) dramatically expanded ADU rights on multifamily properties, increasing the detached ADU cap from 2 to <strong>8 per lot</strong>. ADU construction is a by-right, ministerial process  -  no public hearing, no CEQA review, and a 60-day statutory approval timeline.</p>

<div class="table-scroll"><table>
<thead><tr><th>Provision</th><th>Rule</th><th>Legal Citation</th></tr></thead>
<tbody>
<tr><td>Detached ADUs per lot</td><td>Up to <strong>8</strong> (capped at existing unit count)</td><td>SB 1211; Gov. Code &sect;66323(a)(4)</td></tr>
<tr><td>Conversion ADUs (interior)</td><td>Up to <strong>25%</strong> of existing units</td><td>Gov. Code &sect;66323(a)(3)</td></tr>
<tr><td>Maximum size per ADU</td><td>850 SF (studio/1BR) to 1,200 SF (detached)</td><td>Gov. Code &sect;66321(c)(2)(B)</td></tr>
<tr><td>Height</td><td><strong>18 ft</strong> (on lots with existing multistory MF)</td><td>Gov. Code &sect;66321(c)(2)(D)(iii)</td></tr>
<tr><td>Stories</td><td><strong>2 stories</strong> (18 ft = 9 ft/floor &times; 2)</td><td>State law; preempts local limits</td></tr>
<tr><td>Setbacks from lot lines</td><td><strong>4 ft</strong> side and rear</td><td>Gov. Code &sect;66323(a)(4)</td></tr>
<tr><td>Building separation (fire)</td><td>~6 ft between structures</td><td>CA Building Code Table 602, Type V</td></tr>
<tr><td>Parking replacement</td><td><strong>Not required</strong></td><td>SB 1211; Gov. Code &sect;66323(a)(4)(B)</td></tr>
<tr><td>Approval process</td><td><strong>Ministerial</strong>  -  60-day timeline</td><td>Gov. Code &sect;66321(a)(3)</td></tr>
<tr><td>Owner occupancy</td><td><strong>Not required</strong></td><td>AB 976 (effective 2025)</td></tr>
<tr><td>Impact fees</td><td>ADUs &lt;750 SF exempt; larger proportional</td><td>Gov. Code &sect;66323(f)(3)</td></tr>
</tbody>
</table></div>

<h3 class="sub-heading">Part B: Legal Maximum (22 ADUs)</h3>

<p>Since 420 and 428 W Stocker are separate legal parcels with separate APNs, each independently qualifies for SB 1211 allowances:</p>

<div class="table-scroll"><table>
<thead><tr><th></th><th>420 Parcel (9 existing)</th><th>428 Parcel (18 existing)</th><th>Combined</th></tr></thead>
<tbody>
<tr><td>Detached ADU cap</td><td>8</td><td>8</td><td><strong>16</strong></td></tr>
<tr><td>Conversion ADU cap (25%)</td><td>2</td><td>4</td><td><strong>6</strong></td></tr>
<tr style="font-weight:700;"><td>Legal maximum</td><td>10</td><td>12</td><td><strong>22</strong></td></tr>
</tbody>
</table></div>

<h3 class="sub-heading">Part C: Physical Feasibility  -  6 ADUs</h3>

<p>While the legal maximum is 22 ADUs, the physical site constrains the buildable count. The rear parking area measures approximately 50 feet deep by 160 feet wide. After applying required setbacks:</p>

<div class="table-scroll"><table>
<thead><tr><th>Setback</th><th>Distance</th><th>Applied To</th><th>Source</th></tr></thead>
<tbody>
<tr><td>Rear property line</td><td>4 ft</td><td>Back edge</td><td>State ADU law</td></tr>
<tr><td>Exterior side</td><td>4 ft</td><td>North/south edges</td><td>State ADU law</td></tr>
<tr><td>Interior lot line (between parcels)</td><td>4 ft &times; 2 = 8 ft gap</td><td>Middle</td><td>State ADU law</td></tr>
<tr><td>Separation from existing buildings</td><td>~6 ft</td><td>West edge</td><td>CA Building Code fire separation</td></tr>
</tbody>
</table></div>

<p><strong>Net buildable per parcel:</strong> 80 ft - 4 ft (exterior) - 4 ft (interior) = 72 ft width. 50 ft - 4 ft (rear) - 6 ft (building separation) = 40 ft depth. <strong>72 ft &times; 40 ft = 2,880 SF per parcel.</strong></p>

<p><strong>ADU building layout (3 per parcel):</strong> Each ADU is a 2-story detached structure measuring 20 ft wide by 22 ft deep (440 SF footprint &times; 2 stories = 880 SF total). With 6 ft of fire separation between buildings: 20 + 6 + 20 + 6 + 20 = <strong>72 ft, fitting exactly within the buildable width</strong>. The 22 ft building depth within the 40 ft available leaves 18 ft for rear access and walkways, exceeding fire access requirements.</p>

<p><strong>Feasible total: 6 detached two-story ADUs (3 per parcel, 880 SF each).</strong> Height of 18 ft is allowed by right under Gov. Code &sect;66321(c)(2)(D)(iii) for lots with existing multistory multifamily buildings, preempting Glendale's local 16-foot limit. Note: one coast live oak tree on the 420 parcel (protected under Glendale's Indigenous Tree Ordinance) may affect placement  -  verify on site visit.</p>

<h3 class="sub-heading">Part D: ADU Economics (Three Scenarios)</h3>

<div class="table-scroll"><table>
<thead><tr><th>Assumption</th><th>Optimistic</th><th>Realistic</th><th>Conservative</th></tr></thead>
<tbody>
<tr><td>Cost per ADU (all-in + contingency)</td><td>$250,000</td><td><strong>$275,000</strong></td><td>$325,000</td></tr>
<tr><td>Total cost (6 units)</td><td>$1,500,000</td><td><strong>$1,650,000</strong></td><td>$1,950,000</td></tr>
<tr><td>Rent per unit/month</td><td>$2,400</td><td><strong>$2,300</strong></td><td>$2,200</td></tr>
<tr><td>Annual gross (6 units)</td><td>$172,800</td><td><strong>$165,600</strong></td><td>$158,400</td></tr>
<tr><td>Annual NOI (after 5% vacancy + OpEx)</td><td>$137,160</td><td><strong>$127,320</strong></td><td>$117,480</td></tr>
<tr><td>Value created (at 5% cap)</td><td>$2,743,200</td><td><strong>$2,546,400</strong></td><td>$2,349,600</td></tr>
<tr><td>Estimated profit</td><td>$1,243,200</td><td><strong>$896,400</strong></td><td>$399,600</td></tr>
<tr><td>ROI on investment</td><td>83%</td><td><strong>54%</strong></td><td>20%</td></tr>
</tbody>
</table></div>

<p>Construction cost assumes $275/SF all-in (hard costs + soft costs + permits) for 880 SF units, plus $10,000/unit allocated site work and $25,000/unit contingency (10%). Economies of scale from building 6 identical units simultaneously (shared mobilization, one set of architectural plans, bulk materials) place per-unit costs at the lower end of the $200-$350/SF market range for LA-area ADU construction. Rent of $2,300/month reflects new construction in a rear-lot position, conservatively below same-street renovated 2BR comps ($2,595-$2,695 at 550 W Stocker). Operating expenses include property tax reassessment on new construction, insurance, management, and reserves.</p>

<h3 class="sub-heading">Part E: Value of the ADU Opportunity</h3>

<p>The ADU development potential represents a tangible, executable value-creation path for a buyer. Under the realistic scenario, an investment of approximately $1.65M generates ~$127,000 in new annual NOI and creates approximately $900,000 in equity value  -  a 54% return on investment. This opportunity is rare in the Glendale market: very few multifamily properties offer 8,000 SF of buildable rear area on a 1.1-acre site with by-right ministerial approval under SB 1211.</p>

<p>The <strong>certainty</strong> of the entitlement (ministerial, 60-day approval, no CEQA, no public hearing) and the <strong>scarcity</strong> of qualifying sites make this ADU potential a meaningful component of the property's overall value proposition. The implications for pricing are discussed in the Financial Analysis section below.</p>

<h3 class="sub-heading">Part F: ADUs vs. Ground-Up  -  Side by Side</h3>

<div class="table-scroll"><table>
<thead><tr><th>Factor</th><th>ADU Construction (6 units)</th><th>Ground-Up Redevelopment (38 units)</th></tr></thead>
<tbody>
<tr><td>Units added</td><td><strong>6 new</strong> (no units lost)</td><td>11 net (38 built - 27 demolished)</td></tr>
<tr><td>Approval</td><td><strong>Ministerial, 60 days</strong></td><td>Discretionary, 12-24 months</td></tr>
<tr><td>CEQA</td><td><strong>Exempt</strong></td><td>Required</td></tr>
<tr><td>Tenant displacement</td><td><strong>None</strong></td><td>All 27 units</td></tr>
<tr><td>Relocation costs</td><td><strong>$0</strong></td><td>~$186,000</td></tr>
<tr><td>Lost income during build</td><td><strong>$0</strong></td><td>~$1,800,000 (4 yrs)</td></tr>
<tr><td>Construction cost</td><td><strong>$1.65M</strong></td><td>~$20.4M</td></tr>
<tr><td>Total investment</td><td><strong>$1.65M</strong></td><td>~$35.2M</td></tr>
<tr><td>Timeline</td><td><strong>12-18 months</strong></td><td>4-6 years</td></tr>
<tr><td>Value added / (lost)</td><td><strong>+$896,000 profit</strong></td><td><strong>($13M-$15M) loss</strong></td></tr>
<tr><td>ROI</td><td><strong>54%</strong></td><td><strong>Deeply negative</strong></td></tr>
</tbody>
</table></div>

<div class="condition-note"><strong>Key Takeaway:</strong> Under the realistic scenario, a buyer investing approximately $1.65M in ADU construction generates ~$127,000 in additional annual NOI and creates approximately $900,000 in equity value  -  a 54% return on investment. Combined with the existing $138,000 in rent upside, the total value-add opportunity exceeds $1.0M in new annual income. ADU construction requires no tenant displacement, no CEQA review, and no discretionary approval. It is the clear, executable path to value creation on this site.</div>


</div>
""")

# ==================== SALE COMPS (EXPANDED with narratives) ====================
html_parts.append(f"""
<div class="section" id="sale-comps">
<div class="section-title">Comparable Sales Analysis</div>
<div class="section-subtitle">8 Confirmed Closed Sales in Glendale  -  Past 14 Months</div>
<div class="section-divider"></div>

<div id="saleMap" class="leaflet-map"></div>
<p class="map-fallback">Interactive map available at the live URL.</p>

<div class="table-scroll"><table>
<thead><tr><th>#</th><th>Address</th><th>Submarket</th><th>Units</th><th>Sale Date</th><th>Price</th><th>$/Unit</th><th>$/SF</th><th>Cap</th><th>GRM</th><th>Yr Built</th><th>Notes</th></tr></thead>
<tbody>
{sale_comps_html}
</tbody>
</table></div>

<h3 class="sub-heading">Individual Comp Analysis</h3>

{''.join(COMP_NARRATIVES)}

<h3 class="sub-heading">Four-Metric Positioning at $9.0M Apartment Value</h3>

<div class="table-scroll"><table>
<thead><tr><th>Metric</th><th>Subject @$9.0M</th><th>Comp Range</th><th>Comp Median</th><th>Position</th></tr></thead>
<tbody>
<tr><td><strong>$/Unit</strong></td><td>$333,333</td><td>$304K - $471K</td><td>$382,000</td><td>13% below median  -  value entry point</td></tr>
<tr><td><strong>$/SF</strong></td><td>$396.93</td><td>$267 - $492</td><td>$407</td><td>2% below median  -  at market</td></tr>
<tr><td><strong>Cap Rate</strong></td><td>5.00%</td><td>4.38% - 5.17%</td><td>4.84%</td><td>16 bps above median  -  more yield</td></tr>
<tr><td><strong>GRM</strong></td><td>12.15</td><td>11.60 - 16.11</td><td>13.57</td><td>10% below median  -  tighter multiple</td></tr>
</tbody>
</table></div>

<p>The four-metric analysis positions the subject as a value-oriented acquisition with above-market income yield and significant organic upside  -  exactly where a 27-unit, 1953-vintage, light-value-add portfolio should price relative to smaller, newer, renovated comparables in the same market. The comparable sales data supports the apartment income valuation presented in the Financial Analysis section below.</p>


</div>
""")

# ==================== ON-MARKET COMPS ====================
html_parts.append(f"""
<div class="section section-alt" id="on-market">
<div class="section-title">On-Market Comparables</div>
<div class="section-subtitle">Active Listings in Glendale</div>
<div class="section-divider"></div>

<div id="activeMap" class="leaflet-map"></div>
<p class="map-fallback">Interactive map available at the live URL.</p>

<div class="table-scroll"><table>
<thead><tr><th>#</th><th>Address</th><th>Units</th><th>List Price</th><th>$/Unit</th><th>$/SF</th><th>DOM</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>1</td><td>1151 N Columbus Ave</td><td>5</td><td>$1,699,000</td><td>$339,800</td><td>$496</td><td>19</td><td>Turn-key trust sale. Front house + 4 rear 1BR units. All major capex completed (plumbing, roof, repaved). Fully upgraded interiors.</td></tr>
<tr><td>2</td><td>719 N Jackson St</td><td>6</td><td>$1,950,000</td><td>$325,000</td><td>$368</td><td>20</td><td>M&amp;M listing (Greg Shindler). Full gut renovation, in-unit W/D, individual HVAC. Rear garage with ADU potential noted in listing. Glendale 91206.</td></tr>
<tr><td>3</td><td>1207 N Columbus Ave</td><td>10</td><td>$4,695,000</td><td>$469,500</td><td>$493</td><td>219</td><td>219 DOM, price reduced from $4.8M. All 2BR/2BA, 1989 build, central AC, subterranean parking. 4.43% cap rate stated. One vacancy.</td></tr>
</tbody>
</table></div>

<p>The active inventory ranges from $325,000/unit (719 N Jackson, a 6-unit gut renovation) to $469,500/unit (1207 N Columbus, a 1989-build 10-unit with central AC and subterranean parking that has been on market for 219 DOM after a price reduction). The prolonged marketing time and price drop at 1207 Columbus suggest that $469K/unit is the ceiling of buyer tolerance for Glendale multifamily, even for newer, amenitized product. The subject's scale (27 units), value-add potential, and ADU opportunity differentiate it from the smaller active listings and support pricing discussed in the Financial Analysis section.</p>


</div>
""")

# ==================== RENT COMPS ====================
html_parts.append(f"""
<div class="section" id="rent-comps">
<div class="section-title">Rent Comparables</div>
<div class="section-subtitle">Current Market Rents in the Stocker St / Glenwood Submarket</div>
<div class="section-divider"></div>

<div id="rentMap" class="leaflet-map"></div>
<p class="map-fallback">Interactive map available at the live URL.</p>

<h3 class="sub-heading">2-Bedroom Rent Comparables</h3>
<div class="table-scroll"><table>
<thead><tr><th>#</th><th>Address</th><th>Type</th><th>SF</th><th>Rent</th><th>$/SF</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>1</td><td>550 W Stocker St</td><td>2BR/2BA</td><td>1,100</td><td>$2,595-$2,695</td><td>$2.36-$2.45</td><td>Same street. Renovated kitchens, stainless appliances, central HVAC, hardwood floors, gated parking.</td></tr>
<tr><td>2</td><td>439 W Stocker St</td><td>2BR/2BA</td><td>1,093-1,200</td><td>$3,479-$3,498</td><td>$2.90-$3.18</td><td>Directly across the street. Fully gut-renovated luxury: granite, stainless, LVP, fireplaces, pool, fitness center. TOP of market.</td></tr>
<tr><td>3</td><td>618 W Dryden St</td><td>2BR</td><td>n/a</td><td>$2,550-$2,650</td><td>n/a</td><td>1 block north. 16 units, 1987 build, gated community. Central HVAC, dishwasher, on-site management.</td></tr>
<tr><td>4</td><td>409 W Dryden St</td><td>2BR/2BA</td><td>n/a</td><td>$2,470-$2,800</td><td>n/a</td><td>1 block north. 8 units. Hardwood floors, granite counters, central AC, gated parking, pet friendly.</td></tr>
<tr><td>5</td><td>404 W Stocker St</td><td>2BR condo</td><td>n/a</td><td>$2,800</td><td>n/a</td><td>Condo rental on same block. Higher condition but useful as same-block data point.</td></tr>
<tr style="font-weight:600;background:#FFF8E7;"><td></td><td><strong>Subject 2BR/1BA</strong></td><td>2BR/1BA</td><td>750</td><td>$900-$2,630</td><td>$1.20-$3.51</td><td>Market potential: $2,650/mo</td></tr>
</tbody>
</table></div>

<h3 class="sub-heading">1-Bedroom Rent Comparables</h3>
<div class="table-scroll"><table>
<thead><tr><th>#</th><th>Address</th><th>Type</th><th>SF</th><th>Rent</th><th>$/SF</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>1</td><td>The Henley (245 W Loraine)</td><td>1BR</td><td>759</td><td>$2,347-$2,459</td><td>$3.09-$3.24</td><td>Institutional/Class A (Essex property). In-unit W/D, quartz counters, two pools, fitness center. Currently offering $900 concession.</td></tr>
<tr><td>2</td><td>550 W Stocker St</td><td>1BR</td><td>n/a</td><td>$1,950+</td><td>n/a</td><td>Same street, renovated. Part of 35-unit building.</td></tr>
<tr style="font-weight:600;background:#FFF8E7;"><td></td><td><strong>Subject 1BR/1BA</strong></td><td>1BR/1BA</td><td>650</td><td>$1,895-$1,950</td><td>$2.92-$3.00</td><td>Market potential: $2,295/mo</td></tr>
</tbody>
</table></div>

<p>The subject's 2BR units currently rent between $900 and $2,630/month, with a market potential of $2,650. The mid-market comps on Stocker Street and Dryden Street ($2,470-$2,695 for updated 2BRs) establish the achievable rent level for units with light renovations. The luxury comp at 439 W Stocker ($3,479-$3,498) represents the ceiling after full gut renovation. With 22 of 24 apartment 2BR units currently below the $2,650 market threshold, there is approximately <strong>$138,000 in annual rent upside</strong> achievable through organic lease turnover and measured rent increases under AB 1482's 5% + CPI framework.</p>

<p><strong>Front house rent estimate:</strong> The 4BR/3BA Craftsman at 420 W Stocker (2,500 SF) is modeled at $5,000/month. Standalone 4BR SFR comps in 91202 range from $5,500-$7,500/month, but a 15-25% discount is applied for the multifamily-lot setting (shared parking, foot traffic, less privacy). The property was listed at $3,850-$3,900/month in 2009 and expired without leasing, confirming the multifamily discount was a factor even then. Adjusting for approximately 35-50% Glendale rent growth since 2009 supports the $5,000/month estimate.</p>


</div>
""")

# ==================== FINANCIAL ANALYSIS (Presentation Flow) ====================
html_parts.append(f"""
<div class="section section-alt" id="financials">
<div class="section-title">Financial Analysis</div>
<div class="section-subtitle">Investment Underwriting</div>
<div class="section-divider"></div>

<!-- SCREEN 1: RENT ROLL -->
<h3 class="sub-heading">Unit Mix &amp; Rent Roll</h3>
<div class="table-scroll"><table>
<thead><tr><th>Unit</th><th>Type</th><th>SF</th><th>Current Rent</th><th>Rent/SF</th><th>Market Rent</th><th>Market/SF</th></tr></thead>
<tbody>{rent_roll_html}</tbody>
</table></div>
<p style="font-size:11px;color:#888;font-style:italic;margin-top:-16px;margin-bottom:20px;">Note: Unit numbering skips 428-13 per original building convention. All 27 units are accounted for. Total SF in the rent roll reflects approximate livable area per unit; the 22,674 SF used in $/SF calculations is gross building area per LA County Assessor records.</p>

<!-- SCREEN 2: OPERATING STATEMENT + NOTES (side-by-side) -->
<div class="os-two-col">
<div class="os-left">
<h3 class="sub-heading">Operating Statement</h3>
<table>
<thead><tr><th>Income</th><th class="num">Annual</th><th class="num">Per Unit</th><th class="num">% EGI</th></tr></thead>
<tbody>{op_income_html}</tbody>
</table>
<table>
<thead><tr><th>Expenses</th><th class="num">Annual</th><th class="num">Per Unit</th><th class="num">% EGI</th></tr></thead>
<tbody>{op_expense_html}</tbody>
</table>
<p style="font-size:10px;color:#888;font-style:italic;margin-top:-12px;">Note: Property taxes reassessed at the $9,000,000 apartment income value. The pricing matrix recalculates taxes at each price point.</p>
</div>
<div class="os-right">
<h3 class="sub-heading">Notes to Operating Statement</h3>
<p><strong>[1] Other Income:</strong> Parking revenue of $485/mo ($5,820/yr) across both buildings. No laundry income collected.</p>
<p><strong>[2] Real Estate Taxes:</strong> Estimated at 1.13% of sale price. Current Prop 13 basis is $48,588. Buyer should anticipate reassessment at close of escrow.</p>
<p><strong>[3] Insurance:</strong> $1,040/unit reflecting current LA County market. Owner's 2024 actual was $18,127; increase reflects post-wildfire rate environment.</p>
<p><strong>[4] Water &amp; Power:</strong> Water, sewer, and common area electric. Units individually metered for gas and electric. Owner's 2024 actual was $18,756.</p>
<p><strong>[5] Gas:</strong> Common area usage only. All units individually metered. Owner's 2024 actual was $2,240.</p>
<p><strong>[6] Trash Removal:</strong> $656/unit. Owner's 2024 actual was $13,308; adjusted for Glendale rate increases.</p>
<p><strong>[7] Repairs &amp; Maintenance:</strong> Normalized at $750/unit. Owner's 2024 R&amp;M was $11,833 plus $117,264 in non-recurring capex.</p>
<p><strong>[8] Landscaping:</strong> Owner's 2024 actual of $4,800.</p>
<p><strong>[9] Pest Control:</strong> Owner's 2024 actual of $660, rounded to $700.</p>
<p><strong>[10] On-site Manager:</strong> Required per CA Civil Code Section 17995.1 for 16+ units. Estimated rent-free unit + stipend. Owner's 2024 payroll was $5,116.</p>
<p><strong>[11] General &amp; Administrative:</strong> $80/unit for legal, accounting, office, misc. Owner's 2024 actual was $1,050.</p>
<p><strong>[12] Operating Reserves:</strong> $150/unit for capital replacement. Owner completed $117,264 in 2024 improvements.</p>
<p><strong>[13] Management Fee:</strong> 4.0% of EGI. Third-party professional management. Owner currently self-manages.</p>
</div>
</div>

<!-- SCREEN 3: FINANCIAL DETAIL (Returns + Financing side-by-side) -->
<div class="two-col">
<div>
<h3 class="sub-heading">Returns at Asking Price</h3>
<table class="info-table">
<tr><td>Cap Rate (Current)</td><td>{AT_LIST['cur_cap']:.2f}%</td></tr>
<tr><td>Cap Rate (Pro Forma)</td><td>{AT_LIST['pf_cap']:.2f}%</td></tr>
<tr><td>GRM (Current)</td><td>{AT_LIST['grm']:.2f}</td></tr>
<tr><td>Price Per Unit</td><td>${AT_LIST['per_unit']:,.0f}</td></tr>
<tr><td>Price Per SF</td><td>${AT_LIST['per_sf']:,.0f}</td></tr>
</table>
</div>
<div>
<h3 class="sub-heading">Financing Terms</h3>
<table class="info-table">
<tr><td>Loan Amount (55% LTV)</td><td>${LIST_PRICE * 0.55:,.0f}</td></tr>
<tr><td>Down Payment (45%)</td><td>${LIST_PRICE * 0.45:,.0f}</td></tr>
<tr><td>Interest Rate</td><td>5.75%</td></tr>
<tr><td>Amortization</td><td>30 Years</td></tr>
<tr><td>Loan Term</td><td>3 Years (Due 2029)</td></tr>
<tr><td>Loan Constant</td><td>7.00%</td></tr>
</table>
</div>
</div>

<!-- SCREEN 4: PRICE REVEAL + PRICING MATRIX -->
<div class="price-reveal">
<div style="text-align:center; margin-bottom:32px;">
<div style="font-size:13px; text-transform:uppercase; letter-spacing:2px; color:#C5A258; font-weight:600; margin-bottom:8px;">Suggested List Price</div>
<div style="font-size:56px; font-weight:700; color:#1B3A5C; line-height:1;">${LIST_PRICE:,}</div>
</div>

<div class="metrics-grid metrics-grid-4">
<div class="metric-card"><span class="metric-value">${AT_LIST['per_unit']:,.0f}</span><span class="metric-label">Price Per Unit</span></div>
<div class="metric-card"><span class="metric-value">${AT_LIST['per_sf']:,.0f}</span><span class="metric-label">Price Per SF</span></div>
<div class="metric-card"><span class="metric-value">{AT_LIST['cur_cap']:.2f}%</span><span class="metric-label">Current Cap Rate</span></div>
<div class="metric-card"><span class="metric-value">{AT_LIST['grm']:.2f}</span><span class="metric-label">Current GRM</span></div>
</div>

<div class="condition-note" style="margin-top:24px;">
<div class="condition-note-label">Key Market Thresholds</div>
<p style="font-size:14px; line-height:1.7;">Two critical thresholds define the pricing strategy for this offering:<br><br>
<strong>$10M psychological barrier:</strong> Glendale multifamily transactions above $10M are rare and attract a fundamentally different (and smaller) buyer pool. Pricing at $9.35M keeps the offering accessible to the broadest possible audience, including 1031 exchange investors and local operators who filter searches below $10M. Every $100K above $9.5M materially narrows the buyer funnel.<br><br>
<strong>5% cap rate floor:</strong> Below a 5% current cap rate, income-driven buyers (the majority of the Glendale apartment market) begin to drop out. At $9.35M the subject delivers a 4.79% cap, which is defensible given the 19% rent upside and ADU opportunity. At $9.75M the cap drops to 4.61%, a level that historically requires premium product attributes (newer build, central AC, subterranean parking) to sustain buyer interest.</p>
</div>

<h3 class="sub-heading">Pricing Matrix</h3>
<p style="font-size:12px;color:#666;margin-bottom:12px;"><em>Highlighted row represents the suggested list price. Cap rates are tax-adjusted (property taxes recalculated at 1.13% of sale price per Glendale Prop 13 reassessment), which adjusts NOI and cap rate at every row.</em></p>
<div class="table-scroll"><table>
<thead><tr><th class="num">Price</th><th class="num">Cap Rate</th><th class="num">$/Unit</th><th class="num">$/SF</th><th class="num">GRM</th></tr></thead>
<tbody>{matrix_html}</tbody>
</table></div>

<h3 class="sub-heading">Pricing Rationale</h3>

<p>The suggested list price of <strong>$9,350,000</strong> comprises two components:</p>

<p><strong>Apartment income value: $9,000,000.</strong> Supported by a 5.00% cap rate on $449,791 in normalized current NOI. This is anchored by the same-street comparable at 617 W Stocker St ($394,000/unit, $402/SF), which sold at a 15% per-unit premium appropriate for its smaller scale and updated condition. The best size-match comparable at 950 N Louise St (25 units, $370,000/unit) traded at an 11% premium despite premium location and $1M+ in capex. At $333,333/unit, the subject is conservatively positioned relative to both anchors, offering buyers a value entry point with $138,000 in organic rent upside. The $9.0M apartment value also sits in the middle of the four-metric comp analysis: below median on $/unit (value), at median on $/SF (fair), above median on cap (yield), and below median on GRM (efficient).</p>

<p><strong>ADU development premium: $350,000.</strong> Reflects approximately 39% of the estimated $896,000 development profit under realistic assumptions ($275K/unit construction cost, $2,300/month rent, 54% ROI). Even at the full premium, a buyer retains $546,000 of profit at a 33% ROI on the $1.65M ADU investment. The premium is further justified by the scarcity of 1.1-acre multifamily sites with by-right ADU entitlement in Glendale's Glenwood submarket and the near-zero entitlement risk of SB 1211's ministerial approval process.</p>

<p><strong>Trade range: $8,850,000 to $9,350,000.</strong> The floor of $8,850,000 reflects a 5.10% cap on the apartment income plus a $200,000 minimum ADU premium (22% of profit). At this level, the buyer captures virtually all ADU development upside while acquiring the apartments at an above-market yield.</p>

<div class="condition-note"><strong>Assumptions &amp; Conditions:</strong> Financing terms are estimates and subject to change; contact your Marcus &amp; Millichap Capital Corporation representative. Vacancy modeled at 5.0% based on Glendale market conditions. Management fee of 4.0% of EGI reflects third-party professional management; the current owner self-manages. Real estate taxes estimated at 1.13% of sale price reflecting Proposition 13 reassessment at close of escrow. Operating reserves at $150/unit for capital replacement. ADU economics presented as supplemental analysis and are not incorporated into the base operating statement or pricing matrix. All information believed reliable but not guaranteed; buyer to verify independently.</div>
</div>

</div>
""")

# ==================== FOOTER (same as V1) ====================
html_parts.append(f"""
<div class="footer" id="contact">
<img src="{IMG['logo']}" class="footer-logo" alt="LAAA Team">
<div class="footer-team">
<div class="footer-person">
<img src="{IMG['glen']}" class="footer-headshot" alt="Glen Scher">
<div class="footer-name">Glen Scher</div>
<div class="footer-title">Senior Managing Director Investments</div>
<div class="footer-contact"><a href="tel:8182122808">(818) 212-2808</a><br><a href="mailto:Glen.Scher@marcusmillichap.com">Glen.Scher@marcusmillichap.com</a><br>CA License: 01962976</div>
</div>
<div class="footer-person">
<img src="{IMG['filip']}" class="footer-headshot" alt="Filip Niculete">
<div class="footer-name">Filip Niculete</div>
<div class="footer-title">Senior Managing Director Investments</div>
<div class="footer-contact"><a href="tel:8182122748">(818) 212-2748</a><br><a href="mailto:Filip.Niculete@marcusmillichap.com">Filip.Niculete@marcusmillichap.com</a><br>CA License: 01905352</div>
</div>
</div>
<div class="footer-office">16830 Ventura Blvd, Ste. 100, Encino, CA 91436 | marcusmillichap.com/laaa-team</div>
<div class="footer-disclaimer">This information has been secured from sources we believe to be reliable, but we make no representations or warranties, expressed or implied, as to the accuracy of the information. Buyer must verify the information and bears all risk for any inaccuracies. Marcus &amp; Millichap Real Estate Investment Services, Inc. | License: CA 01930580.</div>
</div>
""")

# JAVASCRIPT (same as V1)
html_parts.append(f"""
<script>
var params = new URLSearchParams(window.location.search);
var client = params.get('client');
if (client) {{ var el = document.getElementById('client-greeting'); if (el) el.textContent = 'Prepared Exclusively for ' + client; }}
document.querySelectorAll('.toc-nav a').forEach(function(link) {{ link.addEventListener('click', function(e) {{ e.preventDefault(); var target = document.querySelector(this.getAttribute('href')); if (target) {{ var navHeight = document.getElementById('toc-nav').offsetHeight; var targetPos = target.getBoundingClientRect().top + window.pageYOffset - navHeight - 4; window.scrollTo({{ top: targetPos, behavior: 'smooth' }}); }} }}); }});
var tocLinks = document.querySelectorAll('.toc-nav a'); var tocSections = []; tocLinks.forEach(function(link) {{ var id = link.getAttribute('href').substring(1); var section = document.getElementById(id); if (section) tocSections.push({{ link: link, section: section }}); }});
function updateActiveTocLink() {{ var navHeight = document.getElementById('toc-nav').offsetHeight + 20; var scrollPos = window.pageYOffset + navHeight; var current = null; tocSections.forEach(function(item) {{ if (item.section.offsetTop <= scrollPos) current = item.link; }}); tocLinks.forEach(function(link) {{ link.classList.remove('toc-active'); }}); if (current) current.classList.add('toc-active'); }}
window.addEventListener('scroll', updateActiveTocLink); updateActiveTocLink();
{sale_map_js}
{active_map_js}
{rent_map_js}
</script>
</body></html>""")

# Write output
html = "".join(html_parts)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\nBOV V2 generated: {OUTPUT}")
print(f"File size: {os.path.getsize(OUTPUT) / 1024 / 1024:.2f} MB")
print("Done!")
