# CLAUDE.md — World Food Movement Corporate Fundraising Agent

## WHO YOU ARE WORKING FOR

**World Food Movement (WFM)** is a U.S.-based 501(c)(3) nonprofit fighting student food insecurity at community colleges. The California chapter operates food pantries and meal programs at three campuses in the San Francisco Bay Area:

| Campus | City | Region | Zip Codes |
|--------|------|--------|-----------|
| De Anza College | Cupertino, CA | South Bay / Silicon Valley | 95014 |
| Foothill College | Los Altos Hills, CA | South Bay / Silicon Valley | 94022 |
| Chabot College | Hayward, CA | East Bay | 94545 |

**The problem:** ~33% of California community college students experience food insecurity. WFM currently receives $0 from corporate sources despite being located in one of the most philanthropically active regions in the country.

**Your job:** Help the Funding & Partnerships lead build and execute a corporate fundraising pipeline — starting with research and prospecting.

---

## FILES IN THIS REPO

- `Corporate_Prospect_Tracker.xlsx` — The master spreadsheet with three tabs:
  - **Prospect Pipeline** — 10 pre-loaded Bay Area companies with columns for company info, contacts, scoring (Alignment/Proximity/Capacity, each 1–5), pipeline stage, actions, and amounts. Has 50 rows ready.
  - **Grant Deadlines** — For tracking foundation grant application windows.
  - **Dashboard** — Auto-calculates pipeline metrics from the Prospect Pipeline tab.

- `Corporate_Fundraising_Playbook.docx` — Strategy document covering the four channels of corporate giving (Corporate Foundations, CSR Budgets, Employee Matching, In-Kind), the 7-step fundraising process, outreach email templates, talking points, and a 90-day launch plan.

- `wfm-corporate-strategy.html` — Interactive browser-based presentation for team alignment meetings. Open with any browser.

---

## THE 4 TASKS TO EXECUTE TODAY

### TASK 1: Expand the Prospect List from 10 → 50 Companies

**Goal:** Build a comprehensive list of 50 Bay Area companies that are strong candidates for corporate giving to WFM.

**How to research:**
1. Start with the 10 companies already in the tracker (Apple, Google, Intuit, Cisco, Salesforce, Kaiser Permanente, Wells Fargo, Applied Materials, Palo Alto Networks, Clorox).
2. Add 40 more companies using these criteria:
   - Headquartered or with major offices within 25 miles of any of the three campuses
   - Revenue large enough to have a giving program (generally $500M+ annual revenue, but include notable mid-size companies too)
   - Mix of industries: tech, healthcare, financial services, consumer goods, food/agriculture, retail, professional services, energy
   - Prioritize companies known to have active foundations or CSR programs

**Target companies to research and add (starting suggestions — verify and expand):**
- **Tech / South Bay:** Adobe, Netflix, ServiceNow, Broadcom, VMware/Broadcom, Hewlett Packard Enterprise, HP Inc., PayPal, eBay, Zoom, Synopsys, Cadence Design, Western Digital, Seagate, Juniper Networks, Arista Networks, Fortinet, Pure Storage, Nutanix, Roku
- **Tech / broader Bay Area:** Meta, Uber, Airbnb, Block (Square), Stripe, Twilio, Okta, Splunk, Workday, LinkedIn/Microsoft
- **Healthcare:** Stanford Health Care, Sutter Health, Kaiser Permanente (already in), Genentech/Roche, Gilead Sciences, AbbVie (South SF)
- **Financial:** Visa, Schwab, SVB/First Citizens, PG&E
- **Consumer / Food / Retail:** Costco (regional), Safeway/Albertsons, Target (regional), Ross Stores (already in), Clorox (already in), Del Monte Foods
- **Professional Services:** Deloitte (SJ office), KPMG, Accenture, McKinsey (SF office)

**For each company, capture:**
- Company name
- Industry
- HQ city (or nearest major office if HQ is elsewhere)
- Nearest WFM campus (De Anza, Foothill, Chabot, or All Campuses)
- Whether they have a foundation, CSR program, or both
- Their giving focus areas (look for: food security, hunger, education, community development, health/wellness, equity, basic needs)
- Any publicly listed grant sizes or ranges
- URL of their community/foundation/CSR page

**Where to find this information:**
- Company websites: look for pages titled "Community," "Foundation," "Corporate Responsibility," "Social Impact," "ESG," "Giving," or "Philanthropy"
- Search: `[company name] corporate foundation grants` or `[company name] community giving program`
- For foundations specifically: search ProPublica Nonprofit Explorer (https://projects.propublica.org/nonprofits/) for the foundation's 990 filing

**Output:** Update the `Corporate_Prospect_Tracker.xlsx` Prospect Pipeline tab with all 50 companies. Fill in every column you can. Set pipeline stage to "1-Research" for all new entries.

---

### TASK 2: Pull 990 Data for Corporate Foundations

**Goal:** For every company on the list that has a corporate foundation, pull their IRS Form 990 data to understand who they fund, how much they give, and whether food security / education / community orgs are in their portfolio.

**How to do this:**
1. Identify which companies on the prospect list have a separate corporate foundation (e.g., "The Google Foundation," "Cisco Foundation," "Wells Fargo Foundation," "Intuit Foundation," etc.)
2. For each foundation, look up their 990 filing on ProPublica Nonprofit Explorer:
   - API endpoint: `https://projects.propublica.org/nonprofits/api/v2/search.json?q=[foundation name]`
   - Or search the website: `https://projects.propublica.org/nonprofits/`
3. From the 990 data, extract:
   - Total grants paid (Schedule I or Part IX Line 1)
   - List of grantees if available (Schedule I)
   - Focus areas based on mission statement and grant recipients
   - Whether they've funded food banks, hunger relief, education, or community college programs
   - Geographic focus (national vs. regional vs. Bay Area specific)
   - Average grant size (total grants / number of grantees)

**Output:** Create a new file called `foundation_990_analysis.md` with a structured summary for each foundation. Include:
- Foundation name
- EIN
- Total assets
- Total grants paid (most recent year available)
- Key grantees relevant to WFM's mission (food security, education, community)
- Average grant size
- Assessment: "Strong fit," "Moderate fit," or "Weak fit" for WFM
- Notes on anything relevant (geographic restrictions, specific program interests, etc.)

Also update the tracker with Capacity scores based on the 990 data.

---

### TASK 3: Score and Prioritize All 50 Prospects

**Goal:** Assign Alignment, Proximity, and Capacity scores to all 50 companies so we have a ranked list of who to approach first.

**Scoring rubric:**

**Alignment Score (1–5):** How closely does the company's giving focus match WFM's mission?
- 5 = Explicitly funds food security, hunger relief, or student basic needs
- 4 = Funds education, community development, or health/wellness (adjacent)
- 3 = Funds broad community/social impact but no specific food or education focus
- 2 = Gives primarily in unrelated areas (arts, environment only, etc.) but has community giving
- 1 = No clear giving program or completely misaligned focus areas

**Proximity Score (1–5):** How close is the company to WFM's campuses?
- 5 = HQ in Cupertino, Los Altos Hills, or Hayward (same city as a campus)
- 4 = HQ within 10 miles of a campus (Mountain View, Sunnyvale, Santa Clara, Milpitas, Fremont, San Jose, Palo Alto, Union City)
- 3 = HQ within 25 miles (San Francisco, Oakland, Redwood City, San Mateo, Newark, Pleasanton)
- 2 = HQ in broader Bay Area (50 miles) or major regional office near campuses
- 1 = No significant presence near campuses

**Capacity Score (1–5):** How large is the company's giving program?
- 5 = Foundation with $10M+ in annual grants, or company revenue $50B+
- 4 = Foundation with $1M–$10M in annual grants, or company revenue $10B–$50B
- 3 = Active giving program with $100K–$1M annual grants, or revenue $1B–$10B
- 2 = Smaller giving program or company revenue $500M–$1B
- 1 = Minimal or no formal giving program

**Output:** Update all scoring columns in the tracker. The Total Score formula is already built in (sum of all three). Sort or flag the top 15 prospects (score 12+) — these are the priority outreach targets.

---

### TASK 4: Draft Personalized Outreach Emails for Top 15

**Goal:** Create individualized cold outreach emails for the 15 highest-scoring prospects that can be sent (after human review and editing) to kick off the corporate fundraising pipeline.

**Email structure (keep under 150 words per email):**

```
Subject: [Something specific to their company + student hunger near their location]

Dear [First Name or "Community Team" if no name found],

[1 sentence: Why you're reaching out — reference their specific giving focus or recent initiative]

[1–2 sentences: Who WFM is and what we do — mention the specific campus nearest to their HQ]

[1 sentence: A compelling data point — "1 in 3 community college students in our district experiences food insecurity" or similar]

[1 sentence: The ask — a 20-minute introductory call, NOT a funding request]

[1 sentence: Thank them for their commitment to [their specific focus area]]

Best regards,
[Name placeholder]
Funding & Partnerships Lead
World Food Movement, California Chapter
```

**Personalization requirements for each email:**
- Reference the company's actual CSR/giving focus area (from your research in Task 1)
- Mention the WFM campus that is closest to their HQ by name
- If they have a foundation, reference it by name
- If their 990 shows they've funded similar orgs, mention it: "We noticed [Foundation] has supported organizations addressing [food security/education/community needs] in the Bay Area..."
- Vary the subject lines — don't use the same template for all 15

**What NOT to do:**
- Don't ask for money in the first email
- Don't make it longer than 150 words
- Don't be generic — every email should feel like it was written specifically for that company
- Don't use buzzwords or nonprofit jargon

**Output:** Create a file called `outreach_emails.md` with all 15 emails, clearly labeled by company. Include:
- Company name
- Contact name and title (if found) or "Community Affairs Team"
- Contact email (if found) or note "Find via LinkedIn / Apollo"
- The draft email
- A note on what to personalize further before sending (e.g., "Insert exact number of students served at De Anza last semester")

Also update the tracker: set pipeline stage to "2-Contact Identified" for any company where you found a specific contact, and to "3-Outreach Sent" once the human confirms they've sent the email.

---

## WORKING STYLE

- **Be thorough but practical.** Real data beats assumptions. If you can't find a company's giving program page, note that and move on — don't fabricate.
- **Show your work.** For each company, note the URL where you found giving program info so the human can verify.
- **Flag uncertainties.** If a company's foundation might be defunct or their CSR page is vague, say so.
- **Update the tracker as you go.** The spreadsheet is the single source of truth.
- **Create separate output files** for the 990 analysis and outreach emails — don't cram everything into the tracker.
- **Prioritize the top prospects.** If time is limited, spend more effort on the high-scoring companies and less on the long shots.

## IMPORTANT CONTEXT

- WFM is a real nonprofit doing real work. The outreach emails will actually be sent to real people. Quality and accuracy matter.
- The human running this is doing it alongside other responsibilities — they don't have time to redo your work. Get it right the first time.
- This is the very first corporate fundraising push for WFM California. There are no existing corporate relationships to build on. Everything is cold outreach.
- The three campuses are in the Foothill-De Anza Community College District (De Anza + Foothill) and the Chabot-Las Positas Community College District (Chabot).
