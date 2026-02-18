"""Configuration for Cultivate — WFM Corporate Fundraising App."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WFM_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'wfm.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'

# Path to the source Excel file (in docs/)
EXCEL_PATH = os.path.join(WFM_ROOT, 'docs', 'Corporate_Prospect_Tracker.xlsx')

# WFM Campus data
CAMPUSES = {
    'De Anza College': {'city': 'Cupertino', 'zip': '95014', 'region': 'South Bay'},
    'Foothill College': {'city': 'Los Altos Hills', 'zip': '94022', 'region': 'South Bay'},
    'Chabot College': {'city': 'Hayward', 'zip': '94545', 'region': 'East Bay'},
}

# Pipeline stages
PIPELINE_STAGES = [
    '1-Research',
    '2-Contact Identified',
    '3-Outreach Sent',
    '4-Meeting Scheduled',
    '5-Proposal Sent',
    '6-Under Review',
    '7-Funded',
    '8-Declined',
]

# Industry categories
INDUSTRIES = [
    'Technology',
    'Healthcare',
    'Financial Services',
    'Consumer Goods',
    'Food & Agriculture',
    'Retail',
    'Professional Services',
    'Energy & Utilities',
    'Other',
]

# Proximity scoring: city name → score
PROXIMITY_SCORES = {
    # Score 5: Same city as a campus
    'cupertino': 5, 'los altos hills': 5, 'hayward': 5,
    # Score 4: Within 10 miles
    'mountain view': 4, 'sunnyvale': 4, 'santa clara': 4, 'milpitas': 4,
    'fremont': 4, 'san jose': 4, 'palo alto': 4, 'union city': 4,
    'los altos': 4, 'campbell': 4, 'newark': 4, 'menlo park': 4, 'los gatos': 4,
    # Score 3: Within 25 miles
    'san francisco': 3, 'oakland': 3, 'redwood city': 3, 'san mateo': 3,
    'pleasanton': 3, 'foster city': 3, 'south san francisco': 3,
    'san carlos': 3, 'belmont': 3, 'san bruno': 3, 'dublin': 3,
    'livermore': 3, 'berkeley': 3, 'emeryville': 3, 'alameda': 3,
    'burlingame': 3, 'daly city': 3, 'san leandro': 3, 'san ramon': 3,
    'walnut creek': 3, 'half moon bay': 3, 'scotts valley': 3,
    # Score 2: Broader Bay Area
    'sacramento': 2, 'santa cruz': 2, 'napa': 2, 'san rafael': 2,
    'novato': 2, 'vallejo': 2, 'concord': 2, 'antioch': 2,
    'gilroy': 2, 'morgan hill': 2, 'petaluma': 2, 'santa rosa': 2,
}

# Alignment keywords → scores
ALIGNMENT_KEYWORDS = {
    5: ['food security', 'hunger', 'food insecurity', 'food bank', 'meal', 'student basic needs',
        'food access', 'food pantry', 'nutrition', 'feeding'],
    4: ['education', 'community college', 'higher education', 'student', 'workforce',
        'health', 'wellness', 'community development', 'equity', 'basic needs', 'youth'],
    3: ['community', 'social impact', 'nonprofit', 'philanthropy', 'civic', 'local',
        'diversity', 'inclusion', 'underserved', 'economic opportunity'],
    2: ['environment', 'arts', 'culture', 'climate', 'sustainability', 'stem',
        'innovation', 'research', 'global'],
}

# ProPublica API base URL
PROPUBLICA_API_BASE = 'https://projects.propublica.org/nonprofits/api/v2'
