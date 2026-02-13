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

## How to Apply

To commit these changes to the master template:

1. Review each item above and decide which to include
2. Edit `bov_web_presentation.md` in `gscher1311/LAAA-AI-Prompts`
3. Update the Jinja2 template in `LAAA-Team/bov-engine/templates/bov.html` if applicable
4. Commit with message: "Update BOV template: [list of changes from Stocker BOV]"
