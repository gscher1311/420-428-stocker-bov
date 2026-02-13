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

## How to Apply

To commit these changes to the master template:

1. Review each item above and decide which to include
2. Edit `bov_web_presentation.md` in `gscher1311/LAAA-AI-Prompts`
3. Update the Jinja2 template in `LAAA-Team/bov-engine/templates/bov.html` if applicable
4. Commit with message: "Update BOV template: [list of changes from Stocker BOV]"
