# Proposed Updates to Master BOV Template

> **Source:** Stocker Gardens BOV (420-428 W Stocker St, Glendale) - February 2026
> **Target:** `bov_web_presentation.md` in `gscher1311/LAAA-AI-Prompts`
> **Status:** STAGING - Review before committing to master template

---

## 1. No Em Dashes or Double Dashes

**Rule:** All BOVs should use single hyphens (` - `) instead of em dashes (`&mdash;`) or double dashes (` -- `). This improves readability across devices and PDF rendering.

**Add to bov_web_presentation.md under "Common Pitfalls":**
> 21. **No em dashes** - Use single hyphens (` - `) throughout all BOV content. Do not use `&mdash;` or ` -- ` in narrative text, table notes, or callout boxes.

---

## 2. Anticipated Buyer Questions Section (Optional)

**Description:** A new optional section placed after the Target Buyer Profile that identifies 4-5 likely buyer objections and provides concise broker responses. The AI should analyze the deal as a buyer, identify probable concerns, then write responses from the broker's perspective.

**Placement:** Inside the Property Information section, after the `.bp-closing` paragraph, before the Property Details sub-heading.

**Styling:** Each objection is a bold navy question with a 2-3 sentence factual response below.

**Add to bov_web_presentation.md under "Required Sections" after the Target Buyer Profile description:**
> **Optional: Anticipated Buyer Questions** - After the Target Buyer Profile, include 4-5 questions a sophisticated buyer would likely raise about this specific deal, each followed by a concise, factual response. Think like a buyer analyzing the deal's weaknesses, then respond as the broker with data-backed answers. Avoid defensive tone; be direct and transparent.

---

## 3. Metric Cards Above Photos in Investment Overview

**Rule:** In the Investment Overview section, place the 4 key metric cards (Units, Building SF, Lot Size, Buildings) immediately after the section divider, before the photo grid. This gives the reader the headline numbers first.

**Current template order:** title > divider > photos > narrative > metric cards
**Proposed order:** title > divider > metric cards > photos > narrative

---

## 4. Broker Perspective Tone Guidelines

**Rule:** Broker's Perspective callouts should sound like a knowledgeable advisor, not a salesperson. Avoid realtor-style hyperbole.

**Add to bov_web_presentation.md under "Broker's Perspective Callouts":**
> **Tone guidelines:**
> - No superlatives: avoid "unmatched," "most compelling," "arguably the best," "among the most favorable"
> - No over-promises: avoid "should generate strong initial interest," "will attract competitive offers"
> - Use measured language: "is designed to attract," "may create perceived value," "the data supports," "appears achievable"
> - Be factual and specific: reference actual numbers, comp addresses, and market data rather than making broad claims
> - Sound optimistic but professional: you want to earn the listing, not overpromise results

---

## 5. Track Record: Local Market Experience Instead of Broker's Perspective

**Rule:** In the Track Record section, replace the generic Broker's Perspective callout with a "Local Market Experience" callout (using `.condition-note` styling) that references specific nearby closings and submarket familiarity. This is more credible than a sales pitch.

**CSS:** Use existing `.condition-note` with `.condition-note-label` set to "Local Market Experience"

---

## 6. Image Sizing Guidelines

**Rule:** Not every image needs to be full-width. Use the following guidelines:

- **Full-width:** Cover hero, closings map iframe, Leaflet comp maps, main 4-photo grid
- **Side-by-side (`.photo-grid`):** Paired images like aerial + ground-level views (e.g., ADU section)
- **Float-right at 48% (`.img-float-right`):** Supplementary images like aerial property outlines, context photos. Text wraps around them.
- **Photo grid height:** 180px instead of 220px for more compact presentation

**New CSS class to add to template:**
```css
.img-float-right { float: right; width: 48%; margin: 0 0 16px 20px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.img-float-right img { width: 100%; display: block; }
/* 768px breakpoint: */
.img-float-right { float: none; width: 100%; margin: 0 0 16px 0; }
```

---

## 7. Cover Page Headshot Structure

**Rule:** Use the Beach BOV's `cover-headshot-wrap` structure with abbreviated titles:
```html
<div class="cover-headshot-wrap">
  <img class="cover-headshot" src="..." alt="Agent Name">
  <div class="cover-headshot-name">Agent Name</div>
  <div class="cover-headshot-title">SMDI</div>
</div>
```

This replaces the older `cover-hs` pattern. Include a `.gold-line` divider between the address and stats.

---

## 8. TOC Nav Compact Sizing for 12-14 Links

**Rule:** The TOC nav must fit all links on a single row at 1000px desktop width without visible overflow. Use these proven values:

- **Desktop:** `font-size: 11px`, `padding: 12px 8px`, `letter-spacing: 0.3px`, container `padding: 0 12px`
- **Hidden scrollbar:** Add `scrollbar-width: none; -ms-overflow-style: none;` on `.toc-nav` and `.toc-nav::-webkit-scrollbar { display: none; }` for clean mobile horizontal scroll
- **768px:** `font-size: 10px`, `padding: 10px 6px`, `letter-spacing: 0.2px`
- **420px:** `font-size: 8px`, `padding: 10px 4px`, `letter-spacing: 0`

These values accommodate up to 14 links (the Stocker BOV has 14 including Development and ADU). The Beach BOV with 12 links uses the same desktop sizing and fits comfortably.

---

## 9. Dynamic PDF Filename via Cloudflare Worker

**Rule:** The Cloudflare PDF Worker (`laaa-pdf-worker`) now supports an optional `filename` query parameter. Each BOV should pass a descriptive filename in its PDF download link instead of relying on the default "bov.pdf".

**Implementation:** In the build script, construct the PDF link with `&filename=BOV+-+{Address}.pdf`:
```python
PDF_FILENAME = "BOV - 420-428 W Stocker St, Glendale.pdf"
PDF_LINK = PDF_WORKER_URL + "/?url=" + urllib.parse.quote(BOV_BASE_URL + "/", safe="") + "&filename=" + urllib.parse.quote(PDF_FILENAME, safe="")
```

If no `filename` param is passed, the worker derives one from the URL hostname (e.g., `420428stocker.laaa.com` becomes `420428stocker.pdf`).

**Add to bov_web_presentation.md under "Phase 5: Deploy":**
> Always include a `filename` parameter in the PDF worker URL so the downloaded file has a descriptive name (e.g., "BOV - 2341 Beach Ave, Venice.pdf" instead of "bov.pdf").

---

## 10. Broker's Perspective Sections - Removed from Stocker BOV

**Decision:** All 12 Broker's Perspective callouts were removed from the Stocker Gardens BOV. The content felt repetitive and overly salesy for a seller-facing document. The factual content in each section already speaks for itself.

**For future BOVs:** Consider whether Broker's Perspective callouts add value or are redundant. If retained, follow the tone guidelines in item #4 above. If removed, ensure each section's narrative is strong enough to stand alone.

---

## 11. Financial Analysis - Presentation Flow Order

**Rule:** Restructure the Financial Analysis section for a live presentation flow. The price reveal should come *after* the income/expense data, not before it. This builds the data story before showing the number.

**New order:**
1. **Rent Roll** - Unit Mix & Rent Roll table
2. **Operating Statement + Notes** (side-by-side) - Income/Expense tables on the left (~55%), numbered notes on the right (~45%). Uses `.os-two-col` CSS grid. Both fit on one screen/PDF page.
3. **Returns + Financing** - Returns at Asking Price and Financing Terms side-by-side (existing `.two-col`)
4. **Price Reveal + Pricing Matrix** - Suggested List Price (big centered), 4 metric cards, Key Market Thresholds, Pricing Matrix, Pricing Rationale, Assumptions

**New CSS class for side-by-side OS + Notes:**
```css
.os-two-col { display: grid; grid-template-columns: 55% 45%; gap: 24px; align-items: start; }
.os-right { font-size: 10.5px; line-height: 1.45; color: #555; }
.os-right h3 { font-size: 13px; margin: 0 0 8px; }
.os-right p { margin-bottom: 4px; }
/* 768px: */ .os-two-col { grid-template-columns: 1fr; }
/* Print: */ .os-two-col { page-break-inside: avoid; }
```

The `.price-reveal` wrapper gets `page-break-before: always` in print CSS so the price starts a fresh PDF page.

---

## 12. Chairman's Club Description - Accurate Wording

**Rule:** When describing the Chairman's Club award, use "a top-tier annual honor" rather than "the highest annual honor." The latter implies it is definitively the single highest award, which may not be accurate and could be seen as an overstatement.

**Correct:** `Chairman's Club - Marcus & Millichap's top-tier annual honor`
**Incorrect:** `Chairman's Club - Marcus & Millichap's highest annual honor`

---

## 13. Location Overview - Two-Column Grid Layout

**Rule:** The Location Overview section should use a two-column grid layout (`.loc-grid`) so that all content fits on one screen (desktop) and one page (PDF):

- **Left column (58%):** All narrative paragraphs stacked vertically
- **Right column (42%):** Static map image on top, single merged info table below (all 10 rows in one table instead of two side-by-side tables)

**Static map:** Downloaded at build time from OpenStreetMap's static map service using the subject property coordinates, embedded as base64. This ensures it renders in both the web view and PDF (unlike Leaflet interactive maps which are hidden in print).

**CSS classes:**
- `.loc-grid` — CSS grid, 2 columns on desktop/print, 1 column on mobile
- `.loc-left` — paragraph container
- `.loc-right` — map + table container (flexbox column)
- `.loc-map` — rounded corners, shadow, contains `<img>`

**Responsive behavior:**
- **Mobile (768px):** Stacks to single column; `.loc-right` gets `order: -1` so the map appears first
- **Print/PDF:** Keeps 2-column layout with smaller fonts (`10px` paragraphs, `10px` table cells) and `page-break-inside: avoid`

---

## 14. Cover Page - Full-Bleed PDF Fix

**Rule:** The cover page must fill the entire PDF page. In `@media print`, use `min-height: 7.5in` (not `auto`) so the hero background image spans the full landscape letter page. Keep `display: flex; align-items: center; justify-content: center;` for vertical centering of the overlay content.

**Also required:** Add `-webkit-print-color-adjust: exact; print-color-adjust: exact;` on `.cover-bg` to ensure the background image actually renders in PDF (browsers strip background images by default in print).

**Desktop and mobile** are unchanged — `min-height: 100vh` already fills the viewport correctly.

```css
/* @media print */
.cover { min-height: 7.5in; padding: 0; page-break-after: always; display: flex; align-items: center; justify-content: center; }
.cover-bg { filter: brightness(0.35); -webkit-print-color-adjust: exact; print-color-adjust: exact; }
```

---

## 15. Track Record - 2-Page PDF Template with Tagline, Service Quote, and Mission Statement

**Rule:** The Track Record section should render as exactly 2 well-designed pages in PDF:

**Page 1 -- Results & Capabilities:**
- `.tr-tagline` banner: "LAAA Team of Marcus & Millichap: Expertise, Execution, Excellence."
- 4 metric cards (transactions, volume, units, DOM)
- Closings map: interactive Google Maps iframe on web, static image (`.tr-map-print`) on PDF. The static image is hidden on web (`display:none`) and shown only in print CSS.
- "We Didn't Invent Great Service..." quote block (`.tr-service-quote`)
- 1031 exchange / M&M platform paragraph

**Page 2 -- Our Team:**
- Mission Statement in a styled callout box (`.tr-mission`)
- Bio grid (headshots + bios side by side)
- CoStar badge + Key Achievements + Press strip

**Removed:** "Local Market Experience" callout (redundant with the comp sections).

**Stats to update each BOV:** Transaction count, sales volume, units sold in the metric cards, service quote paragraph, mission statement, and individual bios.

---

## 16. Location Overview - 3-Box Template (replaces #13)

**Rule:** The Location Overview uses a 3-box layout:
- **Top-left:** Title + subtitle + divider + narrative paragraphs (`.loc-left`)
- **Top-right:** Info table only, no map (`.loc-right`)
- **Bottom:** Full-width map image in a fixed frame (`.loc-wide-map`, 200px desktop, 150px print)

The map image (`location-map.png`) is a user-provided screenshot placed in the `images/` folder. The fixed frame uses `object-fit: cover; object-position: center` to center-crop any image into the box.

**Mobile:** Stacks to single column. Paragraphs first, then table, then map.
**Print:** Keeps 2-column top grid + map at bottom, all on one page with `page-break-inside: avoid`.

---

## 17. Investment Overview + Property Details - 2-Page Template

**Page 1 -- Investment Overview (`.inv-split`):**
Bedford St. inspired split layout:
- **Left column (50%):** Title, subtitle, divider, 4 metric cards, narrative paragraphs, M&M/LAAA logo
- **Right column (50%):** 1 property photo in fixed image frame (`.inv-photo`, 280px), Investment Highlights box below (`.inv-highlights`, `flex:1` fills remaining space)

Investment Highlights (8 bullet points) are moved OUT of the Property Information section into this page.

**Page 2 -- Property Details (`#prop-details`):**
Full-page `.prop-details-area` container (capped at `max-height: 680px` in print with `overflow: hidden`). AI fills this with property-specific tables: Property Overview, Site & Infrastructure, Capital Improvements, Building Systems, etc. For the Stocker BOV, this uses the existing 2-column table layout + aerial image + site description paragraph.

**AI guidelines:** Keep narrative to 3 concise paragraphs, highlights to 8 bullets max, so content fits the pre-sized boxes.

---

## 18. Buyer Profile + Anticipated Buyer Objections - Side-by-Side Template

**Rule:** The Buyer Profile and Buyer Objections display side-by-side in a `.buyer-split` 2-column grid on one page.

- **Left column:** Target Buyer Profile (4 buyer types + closing sentence)
- **Right column:** "Anticipated Buyer Objections" (renamed from "Buyer Questions")

**AI guidelines for writing objections:**
- Think like a **skeptical buyer looking for reasons to lowball or walk away**
- Focus on **pricing, cap rate, rent assumptions, condition, and deal-specific risks**
- Do NOT write objections about things that are:
  - Already in the financial underwriting (Prop 13 reassessment, insurance costs)
  - Common to all California deals (AB 1482 statewide, general seismic risk)
  - Theoretical/academic (ground-up redevelopment feasibility)
- Each response must cite **specific data**: comp addresses, actual rent figures, dollar amounts, percentages
- Keep to **4 objections max** so it fits on the page alongside Buyer Profile
- Format: bold question in quotes, then 2-3 sentence factual, data-backed response

---

## 19. Page-Aware PDF Formatting Pass - Consolidation & Sizing

**Rule:** Every BOV section must be designed to fill exactly one landscape PDF page (10" x 7.7" usable) and approximately one desktop viewport at 100% zoom. No bunched text, no wasted whitespace, no distorted images.

**Key changes from this pass:**

1. **Track Record Page 1:** Hide `.embed-map-fallback` in print (static map replaces it). Reduce Google Maps iframe from 450px to 350px on desktop so the page fits one viewport.

2. **Investment Overview:** Force `.inv-left .metrics-grid-4` to `grid-template-columns: repeat(2, 1fr)` so metric cards display as a 2x2 grid (not 4-across, which is too narrow in the 50% column). Replace "5 Buildings" metric with "1953/54 Year Built". Reduce `.inv-text p` to `font-size: 13px; line-height: 1.6` on desktop.

3. **Location Overview:** Expand `.loc-wide-map` from 150px to 250px in print to fill the page. Tighten `.loc-left p` to `9.5px / 1.35` in print.

4. **Property Details (consolidated):** Building Systems, Regulatory & Compliance, and Transaction History tables are merged into one `#prop-details` page. Uses `.prop-tables-bottom` 2-column grid for Building Systems (left) and Regulatory (right), with Transaction History full-width below. The `#building-systems`, `#regulatory`, and `#transactions` sections are deleted. Their TOC nav links are removed.

5. **Buyer Profile & Objections:** Increased print font sizes (10.5px profile, 11.5px questions, 10px answers). Added full-width property photo (`.buyer-photo`, 220px) below the `.buyer-split` grid to fill remaining page space.

**Print CSS budgets (target ~80-90% of 740px per page):**
- Track Record Page 1: ~600px content
- Track Record Page 2: ~540px content
- Investment Overview: ~510px content
- Location Overview: ~650px content
- Property Details: ~635px content
- Buyer Profile: ~590px content

**Image frames:** All use `object-fit: cover; object-position: center` in fixed-height containers. No image distortion is possible.

---

## 20. Our Marketing Approach + Listing Performance - 2-Page Standard Template

**Rule:** A 2-page "Our Marketing Approach" + "Listing Performance" section is inserted between Track Record and Investment Overview. This is **standard template content** -- the same for every BOV, with stats updated approximately once per year.

**Page 1 -- Our Marketing Approach (`#marketing`):**
- 4 metric cards: 30,000+ Emails Sent, 10,000+ Online Views, 3.7 Avg Offers, 18 Days to Escrow
- Proactive quote callout (`.mkt-quote`): "We are PROACTIVE marketers, not reactive..."
- 2x2 channel grid (`.mkt-channels`): Direct Phone Outreach, Email Campaigns, Online Platforms, Additional Channels -- each with 3 bullet stats

**Page 2 -- Listing Performance (`#performance`):**
- 4 metric cards: 97.6% SP/LP, 21% Sell At/Above Ask, 10-Day Contingency, 61% Sellers Do 1031
- 2x2 performance grid (`.perf-grid`): Pricing Accuracy, Marketing Speed, Contract Strength, Exchange Expertise -- each with 3-4 bullet stats
- Platform strip (`.platform-strip`): navy bar listing all 9 advertising platforms

**Stats source:** Listing Performance Statistics FAQs document + email campaign averages across 200+ campaigns.

**CSS classes:** `.mkt-quote`, `.mkt-channels`, `.mkt-channel`, `.perf-grid`, `.perf-card`, `.platform-strip`, `.platform-strip-label`, `.platform-name`

**Yearly update checklist:** Update the 8 metric card numbers, email count, and any new platforms added.

---

## 21. Page-Aware PDF Matching

**Rule:** The PDF output must match the desktop website view. This is achieved through three coordinated changes:

**1. PDF Worker Viewport:** The Cloudflare PDF worker (`laaa-pdf-worker`) sets `page.setViewport({ width: 1100, height: 850 })` to render at the same 1100px width as the desktop website. Previously it used Puppeteer's default 800px, causing layout mismatches.

**2. Print CSS with 11-12px Fonts:** The `@media print` block uses **11-12px fonts** as the sweet spot between readability and page fit. This is larger than the original 9-10px (which was too small/bunched) but smaller than desktop 13-14px (which overflowed every page). Each section is individually tuned to fit within the ~847px effective viewport height per landscape letter page. Section padding is reduced to 20px 20px in print. Key font sizes: body 11px, section-title 18px, sub-heading 13px, table cells 9-10px, highlights 9-10px.

**3. Page Dividers:** A `.page-break-marker` element (dashed gray line) is inserted between sections on the website, showing users exactly where PDF page breaks will occur. These markers are hidden in print via `display: none`.

**4. Property Details Table Headers:** All info-tables on the Property Details page have `<thead>` rows with navy-blue headers for consistency (Property Overview, Site & Zoning, Building Systems, Regulatory).

**5. Investment Overview Photo Alignment:** The `.inv-right` column has `padding-top: 70px` so the property photo's top edge aligns with the top of the metric cards in the left column.

**Result:** The PDF closely matches the desktop layout structure with properly legible text that fits on landscape letter pages. Each templated section (Track Record, Marketing, Performance, Investment Overview, Location, Property Details, Buyer Profile) fits on exactly one PDF page. Page dividers on the website show where breaks occur.

---

## 22. Track Record Restructure, Marketing Merge, Location Fix, Property Details Trim

**Track Record Page 1:** The "We Didn't Invent Great Service..." heading now leads directly into the 3 mission statement paragraphs (moved from Page 2). The old standalone mission statement section and the 1031 exchange paragraph are removed.

**Track Record Page 2:** Glen/Filip bios with headshots at top, followed by a 3-column `.team-grid` showing all 9 team members (7 associates + 2 support staff) with 40px circular headshots, name, and title. Then CoStar badge, Key Achievements, and Press Strip.

**Marketing & Performance Combined:** The two half-empty pages merged into one `#marketing` section titled "Our Marketing Approach & Results". Two rows of 4 metric cards (marketing stats top, performance stats bottom) + proactive quote + 2x2 channel grid + 2x2 performance grid + platform strip. The `#performance` section is deleted.

**Cover Page Headshots:** Print CSS changed from `.cover-headshots { display: none }` to `display: flex` so headshots render in PDF.

**Google Maps Iframe:** Increased from 350px to 420px on desktop for better visual presence. No PDF impact (iframe hidden in print).

**Gold Sub-Labels:** `.metric-sub` increased from 7px to 9px in print for readability. Text made more descriptive where needed.

**Location Overview Fixed Boxes:** `.loc-left` and `.loc-right` constrained to `max-height: 380px` desktop / `320px` print with `overflow: hidden`. Info-table gets blue `<thead>` header row ("Location Details"). AI must keep paragraphs concise to fit the fixed box.

**Property Details Max Row Budget:** Tables trimmed to fit one page. "Lot Dimensions" and "Per Parcel" merged into Lot Size. Two Roof rows merged into one. Two Plumbing rows merged into one. "Seismic" and "Protected Tree" removed from Regulatory. **Template rule: max 35 total data rows across all tables on this page.** AI priority: remove duplicates, condense related items, then delete least buyer-relevant.

---

## 23. Team Page Restructure, Cover/Marketing/Property Details PDF Fixes, NYSE Removal

**Tagline:** Split "LAAA Team of Marcus & Millichap: Expertise, Execution, Excellence." into two lines with the company name on line 1 (bigger, bolder via `font-size:1.2em`) and the motto on line 2. Desktop font bumped from 20px to 24px, print from 13px to 15px.

**NYSE: MMI Removed:** The `NYSE: MMI` line on the cover page was removed entirely from both desktop and PDF. Not needed for client-facing BOV presentations.

**Team Page Restructured (Page 2):** New layout order: (1) "Our Team" section title at top, (2) CoStar #1 Most Active banner, (3) Glen/Filip bio cards with 100px headshots (desktop) / 75px (print), (4) 9-person team grid with 60px headshots (desktop) / 45px (print). **Template rule: bio headshots (Glen/Filip) should be 1.5-2x the team grid headshots.** "As Featured In" press strip deleted. Duplicate "Our Team" sub-heading and duplicate CoStar badge removed.

**Cover PDF Fix:** Print CSS now constrains cover headshots to 55px with 20px gap (was 80px/28px) to prevent the cover page from overflowing onto two PDF pages. Desktop headshot size unchanged at 80px. **Template rule: always add `.cover-headshot` size constraints in print CSS when headshots are shown on cover.**

**Marketing Overflow Fix:** The redundant second `metrics-grid-4` row (97.6% SP/LP, 21% Above Ask, 10-Day Contingency, 61% 1031) was removed. These stats are already explained in detail in the `perf-grid` cards below. Saves ~80px in print, keeping the full marketing page on one PDF page.

**Property Details Overflow Fix:** Three duplicate rows removed from the Site & Zoning table (School District, FEMA Flood Zone, Fire Hazard) -- these already appear in the Location Overview table. Reduces row count and keeps property details on one PDF page.

**Buyer Profile Page Break:** Added `#property-info { page-break-before: always; }` in print CSS so the Buyer Profile & Objections section gets its own PDF page. Previously it flowed after Property Details with no break, causing the buyer-photo image to overflow onto the next page.

---

## 24. PDF Layout Fixes -- Team, Investment, Location, Property Details, Pricing Summary

**Our Team Page Overflow Fix:** Three changes to fit the team page on one PDF page: (1) Removed "LA Apartment Advisors at Marcus & Millichap" subtitle from the team page header -- the "Our Team" title is sufficient and the company name appears elsewhere. Saves ~25px. (2) Replaced the inline `style="font-size:13px; line-height:1.8;"` on the Key Achievements paragraph with a class `.achievements-list` that uses 13px/1.8 on desktop but 10px/1.45 in print CSS. The inline style was overriding print CSS and adding ~70px of unnecessary height. **Template rule: never use inline font-size/line-height on elements that need to be compact in print; use a class with separate desktop and print rules.** (3) Tightened CoStar badge print margins from `margin:10px auto` to `margin:6px auto`.

**Investment Overview Height Fix:** Three changes: (1) Reduced `inv-photo` from 200px to 170px in print CSS. (2) Trimmed investment highlights from 8 to 6 items -- removed "R-1250 Zoning with Development Headroom" (merged the FAR detail into the "1.11-Acre Combined Site" bullet) and "34+ Year Ownership with Prop 13 Basis" (supporting detail, not primary thesis). (3) Tightened `inv-highlights li` font from 9px/1.3 to 8.5px/1.25 in print. Reduced `inv-right padding-top` from 45px to 30px. **Template rule: keep investment highlights to 5-6 items maximum for PDF fit; longer lists should use smaller fonts or be split.**

**Location Overview Fine-Tuning:** Increased `loc-left` and `loc-right` `max-height` from 320px to 340px in print CSS, and increased `loc-wide-map` from 200px to 220px. This fills the page better without overflowing. Desktop unchanged.

**Property Details 2x2 Grid:** Restructured the property details section into a unified 2x2 grid using new `.prop-grid-4` class (CSS grid with `grid-template-columns: 1fr 1fr; grid-template-rows: auto auto`). Top-left: Property Overview. Top-right: Site & Zoning. Bottom-left: Building Systems. Bottom-right: Regulatory & Compliance. Transaction History table removed entirely per user request. **Template rule: property details should always be a 2x2 grid of 4 tables; avoid full-width tables below the grid that extend the page.**

**Key Market Thresholds Removed:** Deleted the entire "Key Market Thresholds" condition-note section from the price-reveal page. The $10M barrier and 5% cap floor analysis was removed as it is not needed in the client-facing BOV.

**Financial Summary Page (mirrors pricing model page 5):** Replaced the old "Returns at Asking Price + Financing Terms" side-by-side section with a comprehensive Financial Summary page. New layout uses `.summary-two-col` (2-column grid):

Left column:
- OPERATING DATA table (Price, Down Payment, Units, $/Unit, $/SF, Gross SF, Lot Size, Year Built)
- RETURNS table (Cap Rate, GRM, Cash-on-Cash, DCR -- Current vs Pro Forma)
- FINANCING table (Loan Amount, Loan Type, Interest Rate, Amortization, Loan Constant, Year Due)
- UNIT SUMMARY table (1BR, 2BR, 4BR with unit count, avg SF, scheduled rent, market rent)

Right column:
- INCOME table (GSR, Vacancy, ERI, Other Income, EGI -- Current vs Pro Forma)
- CASH FLOW table (NOI, Debt Service, Net Cash Flow, Cash-on-Cash %, Principal Reduction, Total Return)
- EXPENSES table (all 12 line items -- Current vs Pro Forma, plus totals, % of EGI, per unit, per SF)

Bottom: Trade range callout ($8,850,000 -- $9,350,000).

**calc_metrics enhancement:** Added financing calculations to the `calc_metrics()` function: `cash_on_cash`, `dcr`, `debt_service`, `net_cf`, `principal_reduction` (year 1 monthly amortization), `total_return`. Added financing constants: `INTEREST_RATE`, `AMORTIZATION_YEARS`, `LTV`, `LOAN_CONSTANT`. New `calc_principal_reduction_yr1()` helper function. **Template rule: the calc_metrics function should always return all financing-derived metrics so the summary page can be generated dynamically from any price point.**

**Pricing Matrix Updated:** Added 3 new columns to the pricing matrix: Pro Forma Cap Rate, Cash-on-Cash Return, and Pro Forma GRM. Now 7 columns total (Purchase Price, Current Cap, Pro Forma Cap, Cash-on-Cash, $/SF, $/Unit, PF GRM). Matches the pricing model PDF format.

Print CSS for summary page uses 8.5px body font with 7.5px headers and 2px/6px cell padding to fit the dense financial data on one 11x8.5 page. Summary page has `page-break-before: always` in print to ensure it starts on its own PDF page.

---

## 25. Financial Analysis Section Restructure -- Operating Statement, Summary Page, Trade Range

**Operating Statement Page Break:** Added `page-break-before: always` to `.os-two-col` in print CSS so the Operating Statement + Notes section always starts on its own PDF page. The rent roll can flow to multiple pages for large unit counts, but the operating statement is always a standalone PDF page. **Template rule: the operating statement and its notes must always be on their own PDF page.**

**Operating Statement Equal-Height Columns:** Changed `.os-two-col` from `align-items: start` to `align-items: stretch` so the left column (tables) and right column (notes) stretch to the same height. The notes column now has a subtle background (`#f8f9fb`) and border to visually distinguish it and fill the full height. This matches the PDF model's layout where the operating statement and notes appear as two equal-height panels.

**Note Reference Numbers on Expense Items:** Added `[1]` through `[13]` reference numbers to each income/expense line item in the operating statement table. Income items: `[1]` = Other Income. Expense items: `[2]` = Real Estate Taxes through `[13]` = Management Fee. These correspond to the numbered notes in the right column. Uses `.note-ref` class (gold, superscript, 9px desktop / 7px print). **Template rule: every expense/income item that has a corresponding note must show its reference number inline.**

**Trade Range Moved:** The trade range callout ("A TRADE PRICE IN THE CURRENT INVESTMENT ENVIRONMENT OF $8,850,000 -- $9,350,000") was moved from the bottom of the Financial Summary page to below the Pricing Matrix table and above the Pricing Rationale text on the price-reveal page. This is the correct placement -- the trade range is a pricing conclusion, not a financial summary element.

**Financial Summary Restyled to Match PDF Model:** The Financial Summary page was restyled to closely match the pricing model PDF's page 5:
- Added "SUMMARY" banner at the top (navy background, white text, centered, uppercase)
- All summary tables now have visible 1px borders (`border: 1px solid #dce3eb`)
- Navy section headers with white text match the PDF model's section delineation
- Added alternating row backgrounds (`tr:nth-child(even)`) for readability
- Summary/total rows have navy top border + light background matching the PDF model's bold totals
- Print CSS uses 8px body / 7px headers / 2-5px cell padding for maximum density
- Container has border + border-radius on desktop for clean visual separation
- **Template rule: the Financial Summary page should mirror the pricing model's page 5 layout exactly -- SUMMARY banner, two-column grid, navy section headers, bordered tables, alternating row colors.**

---

## How to Apply

To commit these changes to the master template:

1. Review each item above and decide which to include
2. Edit `bov_web_presentation.md` in `gscher1311/LAAA-AI-Prompts`
3. Update the Jinja2 template in `LAAA-Team/bov-engine/templates/bov.html` if applicable
4. Commit with message: "Update BOV template: [list of changes from Stocker BOV]"
