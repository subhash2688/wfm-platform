"""ProPublica Nonprofit Explorer API client for 990 data."""
import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from models.database import db_session
from models.prospect import Prospect
from models.foundation import FoundationData
from models.activity_log import ActivityLog
from config import PROPUBLICA_API_BASE


# NTEE code → human-readable program area
NTEE_CODES = {
    'A': 'Arts, Culture & Humanities',
    'B': 'Education',
    'C': 'Environment',
    'D': 'Animal-Related',
    'E': 'Health Care',
    'F': 'Mental Health & Crisis Intervention',
    'G': 'Diseases, Disorders & Medical Disciplines',
    'H': 'Medical Research',
    'I': 'Crime & Legal-Related',
    'J': 'Employment',
    'K': 'Food, Agriculture & Nutrition',
    'L': 'Housing & Shelter',
    'M': 'Public Safety, Disaster & Relief',
    'N': 'Recreation & Sports',
    'O': 'Youth Development',
    'P': 'Human Services',
    'Q': 'International, Foreign Affairs & National Security',
    'R': 'Civil Rights, Social Action & Advocacy',
    'S': 'Community Improvement & Capacity Building',
    'T': 'Philanthropy, Voluntarism & Grantmaking',
    'U': 'Science & Technology',
    'V': 'Social Science',
    'W': 'Public & Societal Benefit',
    'X': 'Religion-Related',
    'Y': 'Mutual & Membership Benefit',
    'Z': 'Unknown',
}

# More specific NTEE sub-codes for detailed program description
NTEE_SUBCODES = {
    'B20': 'Elementary & Secondary Education',
    'B40': 'Higher Education',
    'B50': 'Graduate & Professional Schools',
    'B60': 'Adult Education',
    'B80': 'Student Services',
    'B90': 'Educational Services',
    'E20': 'Hospitals',
    'E30': 'Ambulatory & Primary Health Care',
    'K20': 'Agricultural Programs',
    'K25': 'Farmland Preservation',
    'K30': 'Food Programs',
    'K31': 'Food Banks & Pantries',
    'K34': 'Congregate Meals',
    'K35': 'Meals on Wheels',
    'K36': 'Nutrition Programs',
    'L20': 'Housing Development & Management',
    'O20': 'Youth Centers & Clubs',
    'P20': 'Human Service Organizations',
    'P30': 'Children & Youth Services',
    'P60': 'Emergency Assistance',
    'P80': 'Services to Promote the Independence of Specific Populations',
    'S20': 'Community & Neighborhood Development',
    'T20': 'Private Grantmaking Foundations',
    'T30': 'Public Foundations',
    'T31': 'Community Foundations',
    'T70': 'Fund Raising & Fund Distribution',
    'W20': 'Government & Public Administration',
}


def search_foundation(query):
    """Search ProPublica for a foundation by name. Returns list of org dicts."""
    encoded = urllib.parse.quote(query)
    url = f'{PROPUBLICA_API_BASE}/search.json?q={encoded}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WFM-CorporateGiving/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get('organizations', [])
    except Exception as e:
        return {'error': str(e)}


def get_organization(ein):
    """Get full organization details + filings from ProPublica."""
    url = f'{PROPUBLICA_API_BASE}/organizations/{ein}.json'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WFM-CorporateGiving/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data
    except Exception as e:
        return {'error': str(e)}


def _parse_ntee(ntee_code):
    """Parse NTEE code into human-readable description."""
    if not ntee_code:
        return 'General Philanthropy', []

    # Try specific sub-code first (e.g., K30)
    prefix = ntee_code[:3].rstrip('Z').rstrip('0') if len(ntee_code) >= 3 else ntee_code[:1]
    # Try 3-char match
    desc = NTEE_SUBCODES.get(ntee_code[:3])
    if not desc:
        # Try major category
        desc = NTEE_CODES.get(ntee_code[0], 'General Philanthropy')

    # Determine program areas from NTEE
    areas = []
    major = ntee_code[0] if ntee_code else ''
    if major == 'K':
        areas = ['Food & Nutrition', 'Agriculture']
    elif major == 'B':
        areas = ['Education']
    elif major == 'E':
        areas = ['Health Care']
    elif major == 'P':
        areas = ['Human Services']
    elif major == 'T':
        areas = ['Philanthropy & Grantmaking']
    elif major == 'S':
        areas = ['Community Development']
    elif major == 'O':
        areas = ['Youth Development']
    elif major == 'L':
        areas = ['Housing & Shelter']
    elif major == 'J':
        areas = ['Employment & Workforce']
    elif major in ('A',):
        areas = ['Arts & Culture']
    elif major == 'C':
        areas = ['Environment']
    else:
        areas = [desc]

    return desc, areas


def _extract_program_areas_from_mission(mission):
    """Extract specific cause areas from the mission statement text."""
    if not mission:
        return []
    text = mission.lower()
    found = []
    area_keywords = {
        'Food & Hunger Relief': ['food', 'hunger', 'meal', 'nutrition', 'feeding', 'food bank',
                                  'food pantry', 'food security', 'food insecurity'],
        'Education': ['education', 'school', 'student', 'scholarship', 'learning', 'college',
                      'university', 'literacy', 'academic'],
        'Community Development': ['community', 'neighborhood', 'civic', 'community development'],
        'Health & Wellness': ['health', 'wellness', 'medical', 'hospital', 'clinic', 'mental health'],
        'Youth Development': ['youth', 'children', 'young people', 'after-school', 'mentoring'],
        'Workforce & Economic': ['job', 'workforce', 'employment', 'economic', 'career', 'skills training'],
        'Equity & Inclusion': ['equity', 'diversity', 'inclusion', 'underserved', 'low-income',
                                'disadvantaged', 'underrepresented', 'social justice'],
        'Housing & Basic Needs': ['housing', 'shelter', 'homelessness', 'basic needs'],
        'Environment & Sustainability': ['environment', 'climate', 'sustainability', 'conservation', 'green'],
        'Arts & Culture': ['arts', 'culture', 'creative', 'museum', 'music'],
        'Technology & Innovation': ['technology', 'tech', 'innovation', 'digital', 'stem', 'science'],
        'Disaster Relief': ['disaster', 'relief', 'emergency', 'crisis', 'humanitarian'],
    }
    for area, keywords in area_keywords.items():
        for kw in keywords:
            if kw in text:
                found.append(area)
                break
    return found


def _determine_filing_type(latest):
    """Determine the filing type from the filing data."""
    formtype = latest.get('formtype', '')
    if formtype == 2 or str(formtype) == '2':
        return '990-PF'
    elif formtype == 1 or str(formtype) == '1':
        return '990'
    elif formtype == 3 or str(formtype) == '3':
        return '990-EZ'
    return '990'


def _build_foundation_url(company_name, foundation_name):
    """Build likely foundation website URL from company name."""
    # Common patterns for corporate foundation websites
    name = (company_name or '').lower().replace(' ', '').replace(',', '').replace('.', '')
    # Remove common suffixes
    for suffix in ['inc', 'corp', 'corporation', 'llc', 'ltd', 'co', 'company', 'systems', 'technologies']:
        name = name.replace(suffix, '')
    name = name.strip()
    if name:
        return f'https://www.{name}.com/foundation'
    return ''


def fetch_foundation_data(prospect_id):
    """End-to-end: search -> match -> parse -> store foundation data for a prospect."""
    prospect = db_session.query(Prospect).get(prospect_id)
    if not prospect:
        return {'error': 'Prospect not found'}

    # Determine search query
    search_name = prospect.foundation_name or f'{prospect.company_name} foundation'
    results = search_foundation(search_name)

    if isinstance(results, dict) and 'error' in results:
        return results
    if not results:
        results = search_foundation(prospect.company_name)
        if isinstance(results, dict) and 'error' in results:
            return results
        if not results:
            return {'error': f'No foundation found for "{search_name}"'}

    # Find best match — prefer foundations
    best = None
    company_lower = prospect.company_name.lower().split('/')[0].strip()
    for org in results:
        org_name = (org.get('name') or '').lower()
        if 'foundation' in org_name or 'fund' in org_name:
            if company_lower.split()[0] in org_name:
                best = org
                break
    if not best and results:
        for org in results:
            if 'foundation' in (org.get('name') or '').lower():
                best = org
                break
    if not best:
        best = results[0]

    ein = best.get('ein')
    if not ein:
        return {'error': 'No EIN found for matched organization'}

    # Get full org details
    org_data = get_organization(ein)
    if isinstance(org_data, dict) and 'error' in org_data:
        return org_data

    org_info = org_data.get('organization', {})
    filings = org_data.get('filings_with_data', [])
    latest = filings[0] if filings else {}

    # --- Financial summary ---
    total_assets = latest.get('totassetsend', 0) or 0
    total_revenue = latest.get('totrevenue', 0) or 0
    total_expenses = latest.get('totfuncexpns', 0) or 0
    tax_period = latest.get('tax_prd_yr', '')
    pdf_url = latest.get('pdf_url', '')

    # Grants paid
    grants_paid = latest.get('contrpdpbks', 0) or 0
    if not grants_paid:
        grants_paid = (latest.get('grntstogovt', 0) or 0) + (latest.get('grntstoindiv', 0) or 0)
    if not grants_paid:
        grants_paid = total_expenses  # fallback

    # --- Revenue breakdown ---
    contributions_received = latest.get('grscontrgifts', 0) or 0
    interest_income = latest.get('intrstrvnue', 0) or 0
    dividend_income = latest.get('dividndsamt', 0) or 0
    investment_income = interest_income + dividend_income
    capital_gains = latest.get('totexcapgn', 0) or 0
    other_income = latest.get('otherincamt', 0) or 0

    # --- Expense breakdown ---
    admin_expenses = latest.get('topradmnexpnsa', 0) or 0
    officer_comp = latest.get('topradmnexpnsb', 0) or latest.get('compofficers', 0) or 0
    program_expenses = latest.get('totexpnsexempt', 0) or 0

    # --- Net investment & distribution ---
    net_investment = latest.get('netinvstinc', 0) or 0
    min_invest_return = latest.get('cmpmininvstret', 0) or 0
    distributable = latest.get('distribamt', 0) or 0

    # --- Grant characteristics ---
    gives_to_individuals = 'Y' if latest.get('grntindivcd') == 'Y' else 'N'
    gives_to_orgs = 'Y' if latest.get('nchrtygrntcd') == 'Y' or grants_paid > 0 else 'N'
    furnishes_goods = 'Y' if latest.get('furngoodscd') == 'Y' else 'N'

    # --- Classification ---
    ntee_code = org_info.get('ntee_code', '')
    subsection_code = str(org_info.get('subsection_code', ''))
    foundation_code = str(org_info.get('foundation_code', ''))
    filing_type = _determine_filing_type(latest)
    ntee_desc, ntee_areas = _parse_ntee(ntee_code)

    # --- Program areas (combine NTEE + mission) ---
    mission = org_info.get('mission', '') or ''
    mission_areas = _extract_program_areas_from_mission(mission)
    # Merge and deduplicate
    all_areas = list(dict.fromkeys(ntee_areas + mission_areas))

    # --- Location ---
    foundation_city = org_info.get('city', '')
    foundation_state = org_info.get('state', '')
    foundation_address = org_info.get('address', '')
    foundation_zip = org_info.get('zipcode', '')

    # --- Estimate grantees ---
    avg_grant = 0
    num_grantees = 0
    if grants_paid > 0:
        if grants_paid > 100_000_000:
            num_grantees = 500
        elif grants_paid > 50_000_000:
            num_grantees = 200
        elif grants_paid > 10_000_000:
            num_grantees = 100
        elif grants_paid > 1_000_000:
            num_grantees = 50
        elif grants_paid > 100_000:
            num_grantees = 20
        else:
            num_grantees = 10
        avg_grant = grants_paid / num_grantees

    # --- Fit assessment ---
    fit = _assess_fit(mission, org_info.get('name', ''), all_areas)

    # --- Geographic focus ---
    geo = _determine_geographic_focus(foundation_city, foundation_state)

    # --- Foundation URL ---
    foundation_url = _build_foundation_url(prospect.company_name, org_info.get('name', ''))

    # --- Save to database ---
    existing = db_session.query(FoundationData).filter_by(prospect_id=prospect.id).first()
    if existing:
        fd = existing
    else:
        fd = FoundationData(prospect_id=prospect.id)
        db_session.add(fd)

    fd.foundation_name = org_info.get('name', best.get('name', ''))
    fd.ein = str(ein)
    fd.tax_period = str(tax_period)

    # Financial summary
    fd.total_assets = total_assets
    fd.total_grants_paid = grants_paid
    fd.total_revenue = total_revenue
    fd.total_expenses = total_expenses
    fd.average_grant_size = avg_grant
    fd.num_grantees = num_grantees

    # Revenue breakdown
    fd.contributions_received = contributions_received
    fd.investment_income = investment_income
    fd.capital_gains = capital_gains
    fd.other_income = other_income

    # Expense breakdown
    fd.grants_to_orgs = grants_paid
    fd.admin_expenses = admin_expenses
    fd.officer_compensation = officer_comp
    fd.program_expenses = program_expenses

    # Net investment
    fd.net_investment_income = net_investment
    fd.minimum_investment_return = min_invest_return
    fd.distributable_amount = distributable

    # Classification
    fd.ntee_code = ntee_code
    fd.ntee_description = ntee_desc
    fd.subsection_code = subsection_code
    fd.foundation_code = foundation_code
    fd.filing_type = filing_type

    # Program areas
    fd.program_areas = json.dumps(all_areas)
    fd.focus_keywords = json.dumps(_extract_keywords(mission))

    # Location
    fd.foundation_city = foundation_city
    fd.foundation_state = foundation_state
    fd.foundation_address = foundation_address
    fd.foundation_zip = foundation_zip

    # Foundation website
    fd.foundation_url = foundation_url

    # Grant info
    fd.gives_to_individuals = gives_to_individuals
    fd.gives_to_orgs = gives_to_orgs
    fd.furnishes_goods = furnishes_goods

    # Fit
    fd.fit_assessment = fit
    fd.mission_statement = mission
    fd.geographic_focus = geo
    fd.pdf_url = pdf_url

    fd.raw_response = json.dumps({'organization': org_info, 'latest_filing': latest})

    from datetime import datetime
    fd.fetched_at = datetime.utcnow()

    # Update prospect
    prospect.has_foundation = True
    prospect.foundation_name = fd.foundation_name
    prospect.research_status = 'foundation_fetched'

    # Log activity
    log = ActivityLog(
        prospect_id=prospect.id,
        action_type='fetch_990',
        description=f'Fetched 990 data for {fd.foundation_name} (EIN: {ein}). '
                    f'Assets: ${total_assets:,.0f}, Grants: ${grants_paid:,.0f}, '
                    f'Causes: {", ".join(all_areas[:3]) if all_areas else "General"}, Fit: {fit}',
    )
    db_session.add(log)
    db_session.commit()

    return fd.to_dict()


def _assess_fit(mission, name, program_areas):
    """Assess how well a foundation fits WFM's mission."""
    text = (mission + ' ' + name).lower()
    areas_lower = [a.lower() for a in program_areas]

    strong_keywords = ['food', 'hunger', 'nutrition', 'meal', 'feeding', 'food security',
                       'food insecurity', 'food bank', 'food pantry']
    moderate_keywords = ['education', 'community college', 'student', 'youth', 'workforce',
                         'health', 'wellness', 'basic needs', 'community development',
                         'equity', 'underserved', 'low-income', 'human services']

    for kw in strong_keywords:
        if kw in text:
            return 'Strong fit'
    if 'food' in ' '.join(areas_lower):
        return 'Strong fit'

    for kw in moderate_keywords:
        if kw in text:
            return 'Moderate fit'
    for area in areas_lower:
        if any(kw in area for kw in ['education', 'human', 'youth', 'community']):
            return 'Moderate fit'

    return 'Weak fit'


def _determine_geographic_focus(city, state):
    """Determine geographic focus from foundation location."""
    if not state:
        return 'Unknown'
    bay_area_cities = ['san jose', 'san francisco', 'oakland', 'cupertino', 'sunnyvale',
                       'mountain view', 'palo alto', 'menlo park', 'redwood city',
                       'santa clara', 'fremont', 'hayward', 'los altos']
    if city and city.lower() in bay_area_cities:
        return 'Bay Area, CA'
    elif state == 'CA':
        return 'California'
    else:
        return f'{city}, {state}' if city else state


def _extract_keywords(mission):
    """Extract relevant keywords from mission statement."""
    if not mission:
        return []
    text = mission.lower()
    relevant = []
    keywords = ['food', 'hunger', 'education', 'student', 'community', 'health',
                'youth', 'workforce', 'equity', 'basic needs', 'nutrition',
                'innovation', 'technology', 'environment', 'arts', 'diversity',
                'inclusion', 'housing', 'poverty', 'economic', 'science',
                'scholarship', 'college', 'wellness']
    for kw in keywords:
        if kw in text:
            relevant.append(kw)
    return relevant


# ---------------------------------------------------------------------------
# Deep Research - multi-year financials, Schedule I grantees, Part VII officers
# ---------------------------------------------------------------------------

from models.yearly_financial import YearlyFinancial
from models.foundation_grant import FoundationGrant
from models.foundation_officer import FoundationOfficer


GRANTEE_CATEGORY_KEYWORDS = {
    "food_hunger": [
        "food", "hunger", "meal", "nutrition", "feeding", "pantry", "food bank",
        "foodbank", "food shelf", "food security", "food insecurity", "soup kitchen",
        "gleaning", "harvest", "food access", "anti-hunger", "no kid hungry",
        "second harvest", "foodshare", "food rescue",
    ],
    "education": [
        "education", "school", "student", "scholarship", "learning", "college",
        "university", "literacy", "academic", "tutoring", "library", "stem",
        "curriculum", "classroom", "teacher", "mentor", "afterschool", "after school",
        "community college", "workforce development", "trade school",
    ],
    "health": [
        "health", "wellness", "medical", "hospital", "clinic", "mental health",
        "behavioral health", "substance", "addiction", "recovery", "disease",
        "cancer", "diabetes", "healthcare", "public health", "community health",
        "patient", "nursing", "pediatric", "maternal",
    ],
    "community": [
        "community", "neighborhood", "civic", "community development", "social services",
        "human services", "social impact", "safety net", "basic needs", "housing",
        "shelter", "homelessness", "affordable", "low-income", "poverty", "equity",
        "underserved", "disadvantaged", "inclusion", "diversity", "social justice",
    ],
    "youth": [
        "youth", "children", "child", "young people", "teen", "teenager", "juvenile",
        "after-school", "camp", "boys", "girls", "young adult", "foster", "mentoring",
        "boy scouts", "girl scouts", "big brothers", "ymca", "ywca",
    ],
    "environment": [
        "environment", "climate", "sustainability", "conservation", "green", "nature",
        "wildlife", "ocean", "forest", "park", "clean energy", "renewable", "carbon",
        "pollution", "land trust", "watershed",
    ],
    "arts": [
        "arts", "culture", "creative", "museum", "music", "theater", "theatre",
        "dance", "film", "symphony", "opera", "gallery", "artist", "humanities",
        "cultural", "heritage", "performing arts",
    ],
    "workforce": [
        "workforce", "employment", "job training", "vocational", "career", "skills",
        "apprenticeship", "internship", "economic mobility", "job placement",
        "reentry", "re-entry", "unemployment", "underemployed",
    ],
}

BAY_AREA_CITIES = {
    "san jose", "san francisco", "oakland", "cupertino", "sunnyvale",
    "mountain view", "palo alto", "menlo park", "redwood city", "santa clara",
    "fremont", "hayward", "los altos", "berkeley", "emeryville", "san mateo",
    "foster city", "milpitas", "union city", "newark", "pleasanton", "dublin",
    "livermore", "san ramon", "walnut creek", "concord", "alameda", "san leandro",
    "daly city", "south san francisco", "burlingame", "san carlos", "belmont",
    "san bruno", "half moon bay", "los gatos", "campbell", "saratoga",
    "woodside", "atherton", "portola valley", "los altos hills",
}

BAY_AREA_ZIP_PREFIXES = ("940", "941", "943", "944", "945", "946", "947", "948", "950", "951")


def fetch_multi_year_financials(foundation_data_id):
    """Fetch and store financial data for every year available in ProPublica.

    Reads filings_with_data from the stored raw_response (or re-fetches from
    ProPublica when not cached), then creates/updates a YearlyFinancial row for
    each filing year.  Updates the parent FoundationData record with
    years_of_data and giving_trend.

    Returns the number of years stored.
    """
    fd = db_session.query(FoundationData).get(foundation_data_id)
    if not fd:
        return 0

    # Try to get filings from cached raw_response first
    filings = []
    if fd.raw_response:
        try:
            cached = json.loads(fd.raw_response)
            # raw_response may hold {'organization': ..., 'latest_filing': ...}
            # OR the full ProPublica org response with filings_with_data
            if 'filings_with_data' in cached:
                filings = cached['filings_with_data']
        except Exception:
            pass

    # If no filings yet, re-fetch from ProPublica using the stored EIN
    if not filings and fd.ein:
        org_data = get_organization(fd.ein)
        if not (isinstance(org_data, dict) and 'error' in org_data):
            filings = org_data.get('filings_with_data', [])
            # Cache the full response for future calls
            try:
                fd.raw_response = json.dumps(org_data)
                db_session.flush()
            except Exception:
                pass

    if not filings:
        return 0

    years_stored = 0
    grants_by_year = []  # list of (tax_year, grants_paid) for trend calculation

    for filing in filings:
        try:
            tax_year = filing.get('tax_prd_yr')
            if not tax_year:
                continue
            tax_year = int(tax_year)

            total_assets = filing.get('totassetsend', 0) or 0
            total_revenue = filing.get('totrevenue', 0) or 0
            total_expenses = filing.get('totfuncexpns', 0) or 0
            contributions_received = filing.get('grscontrgifts', 0) or 0
            interest_income = filing.get('intrstrvnue', 0) or 0
            dividend_income = filing.get('dividndsamt', 0) or 0
            investment_income = interest_income + dividend_income
            capital_gains = filing.get('totexcapgn', 0) or 0
            other_income = filing.get('otherincamt', 0) or 0
            grants_to_orgs = filing.get('contrpdpbks', 0) or 0
            admin_expenses = filing.get('topradmnexpnsa', 0) or 0
            officer_compensation = (filing.get('topradmnexpnsb', 0) or
                                    filing.get('compofficers', 0) or 0)
            program_expenses = filing.get('totexpnsexempt', 0) or 0
            object_id = filing.get('object_id', '')
            pdf_url = filing.get('pdf_url', '')
            filing_type = _determine_filing_type(filing)

            # Upsert: find existing row or create new
            existing_yf = (
                db_session.query(YearlyFinancial)
                .filter_by(foundation_data_id=foundation_data_id, tax_year=tax_year)
                .first()
            )
            if existing_yf:
                yf = existing_yf
            else:
                yf = YearlyFinancial(
                    foundation_data_id=foundation_data_id,
                    tax_year=tax_year,
                )
                db_session.add(yf)

            yf.total_assets = total_assets
            yf.total_grants_paid = grants_to_orgs
            yf.total_revenue = total_revenue
            yf.total_expenses = total_expenses
            yf.contributions_received = contributions_received
            yf.investment_income = investment_income
            yf.capital_gains = capital_gains
            yf.other_income = other_income
            yf.grants_to_orgs = grants_to_orgs
            yf.admin_expenses = admin_expenses
            yf.officer_compensation = officer_compensation
            yf.program_expenses = program_expenses
            yf.object_id = object_id
            yf.pdf_url = pdf_url
            yf.filing_type = filing_type

            grants_by_year.append((tax_year, grants_to_orgs))
            years_stored += 1

        except Exception:
            continue

    db_session.flush()

    # Compute giving_trend from grant amounts across years
    if len(grants_by_year) >= 3:
        grants_by_year.sort(key=lambda x: x[0])  # sort ascending by year
        earliest_two = [g for _, g in grants_by_year[:2]]
        latest_two = [g for _, g in grants_by_year[-2:]]
        avg_early = sum(earliest_two) / len(earliest_two) if earliest_two else 0
        avg_late = sum(latest_two) / len(latest_two) if latest_two else 0
        if avg_early > 0:
            pct_change = (avg_late - avg_early) / avg_early
            if pct_change > 0.15:
                trend = 'growing'
            elif pct_change < -0.15:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        fd.giving_trend = trend

    fd.years_of_data = years_stored
    db_session.commit()

    return years_stored


def fetch_object_ids_from_html(ein):
    """Scrape ProPublica org HTML page to get object_ids for XML downloads.

    The ProPublica JSON API does not include object_ids, but the HTML page
    has download-xml links with the real IRS object_ids.

    Returns a dict mapping tax_year (int) -> object_id (str).
    """
    import re as _re
    clean_ein = str(ein).replace('-', '')
    url = f'https://projects.propublica.org/nonprofits/organizations/{clean_ein}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except Exception:
        return {}

    # ProPublica wraps each year in:
    #   <section class="single-filing-period" id='filing2024'>
    # followed later by:
    #   <a ... href="/nonprofits/download-xml?object_id=NNNN" ...>XML</a>
    result = {}
    current_year = None
    for line in html.split('\n'):
        # Match section with filing year in id attribute
        section_match = _re.search(r'single-filing-period["\']?\s+id=["\']?filing(\d{4})', line)
        if section_match:
            try:
                current_year = int(section_match.group(1))
            except ValueError:
                current_year = None

        # Match XML download link
        xml_match = _re.search(r'download-xml\?object_id=(\d+)', line)
        if xml_match and current_year:
            result[current_year] = xml_match.group(1)
            current_year = None  # consumed

    return result


def fetch_990_xml(object_id):
    """Download and parse the IRS 990 XML filing for the given object_id.

    Uses ProPublica's download-xml endpoint which provides a signed S3 URL.
    Falls back to the public IRS S3 bucket.  Returns the parsed XML root
    element on success, or None if the file is unavailable.
    """
    if not object_id:
        return None

    # Primary: ProPublica signed URL (works for all filings)
    pp_url = f'https://projects.propublica.org/nonprofits/download-xml?object_id={object_id}'
    try:
        req = urllib.request.Request(pp_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
        root = ET.fromstring(raw)
        return root
    except Exception:
        pass

    # Fallback: direct IRS S3 bucket (older filings only)
    s3_url = f'https://s3.amazonaws.com/irs-form-990/{object_id}_public.xml'
    try:
        req = urllib.request.Request(s3_url, headers={'User-Agent': 'WFM-CorporateGiving/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
        root = ET.fromstring(raw)
        return root
    except Exception:
        return None


def parse_schedule_i(xml_root, foundation_data_id, tax_year):
    """Extract Schedule I grantee records from a parsed 990 XML root.

    Handles both Form 990 (RecipientTable) and Form 990-PF
    (GrantOrContributionPdDurYrGrp) structures.  Saves each grantee as a
    FoundationGrant row and returns the total count inserted/updated.
    """
    if xml_root is None:
        return 0

    ns = 'http://www.irs.gov/efile'
    nsb = f'{{{ns}}}'

    # Candidate XPaths for grantee list elements -- 990 then 990-PF then fallbacks
    candidate_paths = [
        f'.//{nsb}RecipientTable',
        f'.//{nsb}GrantOrContributionPdDurYrGrp',
        './/RecipientTable',
        './/GrantOrContributionPdDurYrGrp',
    ]

    grantee_elements = []
    for path in candidate_paths:
        found = xml_root.findall(path)
        if found:
            grantee_elements = found
            break

    if not grantee_elements:
        return 0

    count = 0
    for elem in grantee_elements:
        try:
            def _txt(*tags):
                """Return first non-empty text from a list of tag names (with and without ns)."""
                for tag in tags:
                    node = elem.find(f'.//{nsb}{tag}')
                    if node is not None and node.text:
                        return node.text.strip()
                    node = elem.find(f'.//{tag}')
                    if node is not None and node.text:
                        return node.text.strip()
                return ''

            name = (
                _txt('BusinessNameLine1Txt', 'BusinessNameLine1') or
                _txt('RecipientPersonNm') or
                ''
            )
            # RecipientBusinessName wrapping element -- navigate into it
            if not name:
                for tag_wrapper in (f'{nsb}RecipientBusinessName', 'RecipientBusinessName'):
                    wrapper = elem.find(f'.//{tag_wrapper}')
                    if wrapper is not None:
                        for child_tag in (f'{nsb}BusinessNameLine1Txt',
                                          f'{nsb}BusinessNameLine1',
                                          'BusinessNameLine1Txt',
                                          'BusinessNameLine1'):
                            child = wrapper.find(child_tag)
                            if child is not None and child.text:
                                name = child.text.strip()
                                break
                    if name:
                        break

            if not name:
                continue  # skip rows without a grantee name

            # Skip placeholder entries (large foundations list grantees in PDF)
            if any(skip in name.upper() for skip in ['SEE ATTACHED', 'SEE SCHEDULE', 'VARIOUS', 'SEE STATEMENT']):
                continue

            ein_val = _txt('RecipientEIN', 'EINOfRecipient')
            amount_str = _txt('CashGrantAmt', 'Amt', 'Amount')
            try:
                amount = float(amount_str.replace(',', '')) if amount_str else 0.0
            except ValueError:
                amount = 0.0

            purpose = _txt('PurposeOfGrantTxt', 'GrantOrContributionPurposeTxt', 'PurposeOfGrant')
            city = _txt('CityNm', 'City')
            state = _txt('StateAbbreviationCd', 'State')
            zip_code = _txt('ZIPCd', 'ZIPCode')

            category, confidence = tag_grantee_category(name, purpose)
            is_bay_area = _is_bay_area_grantee(city, state, zip_code)

            # Upsert by (foundation_data_id, tax_year, grantee_name)
            existing_grant = (
                db_session.query(FoundationGrant)
                .filter_by(
                    foundation_data_id=foundation_data_id,
                    tax_year=tax_year,
                    grantee_name=name,
                )
                .first()
            )
            if existing_grant:
                fg = existing_grant
            else:
                fg = FoundationGrant(
                    foundation_data_id=foundation_data_id,
                    tax_year=tax_year,
                    grantee_name=name,
                )
                db_session.add(fg)

            fg.grantee_ein = ein_val
            fg.amount = amount
            fg.purpose = purpose
            fg.grantee_city = city
            fg.grantee_state = state
            fg.grantee_zip = zip_code
            fg.category = category
            fg.category_confidence = confidence
            fg.is_bay_area = is_bay_area

            count += 1

        except Exception:
            continue

    db_session.flush()
    return count


def parse_part_vii(xml_root, foundation_data_id, tax_year):
    """Extract Part VII officer/director compensation from a parsed 990 XML root.

    Handles both Form 990 (Form990PartVIISectionAGrp) and Form 990-PF
    (OfficerDirTrstKeyEmplGrp) structures.  Saves each person as a
    FoundationOfficer row and returns the total count inserted/updated.
    """
    if xml_root is None:
        return 0

    ns = 'http://www.irs.gov/efile'
    nsb = f'{{{ns}}}'

    candidate_paths = [
        f'.//{nsb}Form990PartVIISectionAGrp',
        f'.//{nsb}OfficerDirTrstKeyEmplGrp',
        './/Form990PartVIISectionAGrp',
        './/OfficerDirTrstKeyEmplGrp',
    ]

    officer_elements = []
    for path in candidate_paths:
        found = xml_root.findall(path)
        if found:
            officer_elements = found
            break

    if not officer_elements:
        return 0

    count = 0
    for elem in officer_elements:
        try:
            def _txt(*tags):
                for tag in tags:
                    node = elem.find(f'.//{nsb}{tag}')
                    if node is not None and node.text:
                        return node.text.strip()
                    node = elem.find(f'.//{tag}')
                    if node is not None and node.text:
                        return node.text.strip()
                return ''

            name = _txt('PersonNm', 'Name', 'BusinessNameLine1Txt')
            if not name:
                continue

            title = _txt('TitleTxt', 'PersonTitleTxt', 'Title')
            hours_str = _txt('AverageHoursPerWeekRt', 'AvgHrsPerWkDevotedToPosRt')
            comp_str = _txt('ReportableCompFromOrgAmt', 'CompensationAmt')

            try:
                hours_per_week = float(hours_str) if hours_str else 0.0
            except ValueError:
                hours_per_week = 0.0

            try:
                compensation = float(comp_str.replace(',', '')) if comp_str else 0.0
            except ValueError:
                compensation = 0.0

            title_lower = title.lower()
            is_officer = any(kw in title_lower for kw in ('officer', 'president', 'treasurer',
                                                            'secretary', 'ceo', 'cfo', 'coo',
                                                            'executive director', 'chair'))
            is_director = 'director' in title_lower
            is_trustee = 'trustee' in title_lower
            is_key_employee = ('key' in title_lower or 'vp' in title_lower
                               or 'vice president' in title_lower)

            # Upsert by (foundation_data_id, tax_year, name)
            existing_officer = (
                db_session.query(FoundationOfficer)
                .filter_by(
                    foundation_data_id=foundation_data_id,
                    tax_year=tax_year,
                    name=name,
                )
                .first()
            )
            if existing_officer:
                fo = existing_officer
            else:
                fo = FoundationOfficer(
                    foundation_data_id=foundation_data_id,
                    tax_year=tax_year,
                    name=name,
                )
                db_session.add(fo)

            fo.title = title
            fo.hours_per_week = hours_per_week
            fo.compensation = compensation
            fo.is_officer = is_officer
            fo.is_director = is_director
            fo.is_trustee = is_trustee
            fo.is_key_employee = is_key_employee

            count += 1

        except Exception:
            continue

    db_session.flush()
    return count


def tag_grantee_category(name, purpose):
    """Classify a grantee into a category based on name and purpose text.

    Checks the combined text against GRANTEE_CATEGORY_KEYWORDS.  Returns a
    tuple of (category, confidence) where confidence is 'high', 'medium', or
    'low'.
    """
    combined = f'{name} {purpose}'.lower()
    matches = {}  # category -> match_count

    for category, keywords in GRANTEE_CATEGORY_KEYWORDS.items():
        hit_count = sum(1 for kw in keywords if kw in combined)
        if hit_count > 0:
            matches[category] = hit_count

    if not matches:
        return ('other', 'low')

    # Pick the category with the most keyword hits
    best_category = max(matches, key=lambda c: matches[c])
    best_count = matches[best_category]
    total_categories_matched = len(matches)

    if best_count >= 2 or total_categories_matched == 1:
        confidence = 'high'
    else:
        confidence = 'medium'

    return (best_category, confidence)


def _is_bay_area_grantee(city, state, zip_code):
    """Return True if the grantee address is in the Bay Area.

    Checks both city name (against BAY_AREA_CITIES) and ZIP code prefix
    (against BAY_AREA_ZIP_PREFIXES).
    """
    if state and state.upper() == 'CA':
        if city and city.strip().lower() in BAY_AREA_CITIES:
            return True
    if zip_code:
        zip_str = str(zip_code).strip()
        if zip_str.startswith(BAY_AREA_ZIP_PREFIXES):
            return True
    return False


def compute_overlap_score(foundation_data_id):
    """Compute what percentage of grant dollars align with WFM's mission.

    Mission-aligned categories: food_hunger, education, community, youth, health.
    Updates foundation's mission_overlap_score and returns the percentage (0-100).
    """
    fd = db_session.query(FoundationData).get(foundation_data_id)
    if not fd:
        return 0.0

    grants = (
        db_session.query(FoundationGrant)
        .filter_by(foundation_data_id=foundation_data_id)
        .all()
    )

    if not grants:
        return 0.0

    mission_categories = {'food_hunger', 'education', 'community', 'youth', 'health'}
    total_amount = 0.0
    mission_amount = 0.0

    for grant in grants:
        amt = grant.amount or 0.0
        total_amount += amt
        if grant.category in mission_categories:
            mission_amount += amt

    if total_amount == 0:
        score = 0.0
    else:
        score = (mission_amount / total_amount) * 100.0

    fd.mission_overlap_score = score
    db_session.flush()
    return score


def compute_geographic_concentration(foundation_data_id):
    """Compute what percentage of grant dollars go to Bay Area grantees.

    Updates foundation's bay_area_grant_pct and returns the percentage (0-100).
    """
    fd = db_session.query(FoundationData).get(foundation_data_id)
    if not fd:
        return 0.0

    grants = (
        db_session.query(FoundationGrant)
        .filter_by(foundation_data_id=foundation_data_id)
        .all()
    )

    if not grants:
        return 0.0

    total_amount = 0.0
    bay_area_amount = 0.0

    for grant in grants:
        amt = grant.amount or 0.0
        total_amount += amt
        if grant.is_bay_area:
            bay_area_amount += amt

    if total_amount == 0:
        pct = 0.0
    else:
        pct = (bay_area_amount / total_amount) * 100.0

    fd.bay_area_grant_pct = pct
    db_session.flush()
    return pct


def deep_research(foundation_data_id):
    """Orchestrate full deep research for a foundation.

    Steps:
      1. Fetch multi-year financials from ProPublica.
      2. Download and parse 990 XML (Schedule I + Part VII) for the latest 3
         years that have an object_id.
      3. Compute mission overlap and Bay Area geographic concentration scores.
      4. Stamp deep_research_at and commit.

    Returns a summary dict with keys: years, grantee_count, officer_count,
    trend, overlap_score, bay_area_pct.  On unrecoverable error, returns a dict
    with an 'error' key.
    """
    from datetime import datetime

    try:
        fd = db_session.query(FoundationData).get(foundation_data_id)
        if not fd:
            return {'error': f'FoundationData id={foundation_data_id} not found'}

        # Step 1: Fetch/refresh all yearly financial rows
        years_stored = fetch_multi_year_financials(foundation_data_id)

        # Step 1b: Scrape object_ids from ProPublica HTML and backfill
        if fd.ein:
            obj_id_map = fetch_object_ids_from_html(fd.ein)
            if obj_id_map:
                all_yf = (
                    db_session.query(YearlyFinancial)
                    .filter_by(foundation_data_id=foundation_data_id)
                    .all()
                )
                for yf in all_yf:
                    if not yf.object_id and yf.tax_year in obj_id_map:
                        yf.object_id = obj_id_map[yf.tax_year]
                db_session.flush()

        # Step 2: Parse XML for up to the 3 most recent years that have object_ids
        yearly_financials = (
            db_session.query(YearlyFinancial)
            .filter_by(foundation_data_id=foundation_data_id)
            .filter(YearlyFinancial.object_id != None,
                    YearlyFinancial.object_id != '')
            .order_by(YearlyFinancial.tax_year.desc())
            .limit(3)
            .all()
        )

        total_grantee_count = 0
        total_officer_count = 0

        for i, yf in enumerate(yearly_financials):
            if i > 0:
                time.sleep(1)  # be polite to S3 / IRS servers

            xml_root = fetch_990_xml(yf.object_id)
            if xml_root is None:
                continue

            grantees_found = parse_schedule_i(xml_root, foundation_data_id, yf.tax_year)
            officers_found = parse_part_vii(xml_root, foundation_data_id, yf.tax_year)

            total_grantee_count += grantees_found
            total_officer_count += officers_found

        # Step 3: Compute analytical scores
        overlap_score = compute_overlap_score(foundation_data_id)
        bay_area_pct = compute_geographic_concentration(foundation_data_id)

        # Step 4: Stamp timestamp and persist
        fd.deep_research_at = datetime.utcnow()
        db_session.commit()

        return {
            'years': years_stored,
            'grantee_count': total_grantee_count,
            'officer_count': total_officer_count,
            'trend': fd.giving_trend or 'stable',
            'overlap_score': round(overlap_score, 1),
            'bay_area_pct': round(bay_area_pct, 1),
        }

    except Exception as e:
        try:
            db_session.rollback()
        except Exception:
            pass
        return {'error': str(e)}
