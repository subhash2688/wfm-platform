"""990 Analysis route — GET /analysis."""
import json
from flask import Blueprint, render_template, jsonify
from models.database import db_session
from models.prospect import Prospect
from models.foundation import FoundationData
from services.propublica import fetch_foundation_data

analysis_bp = Blueprint('analysis', __name__)


def format_millions(value):
    """Format large numbers into M/K shorthand."""
    if not value:
        return '0'
    if value >= 1_000_000_000:
        return f'{value / 1_000_000_000:.1f}B'
    elif value >= 1_000_000:
        return f'{value / 1_000_000:.1f}M'
    elif value >= 1_000:
        return f'{value / 1_000:.0f}K'
    return f'{value:,.0f}'


def format_currency(value):
    """Format as full currency string."""
    if not value:
        return '$0'
    return f'${value:,.0f}'


def format_pct(part, whole):
    """Calculate percentage."""
    if not whole or not part:
        return '0%'
    return f'{(part / whole) * 100:.0f}%'


@analysis_bp.route('/analysis')
def analysis():
    foundations = db_session.query(FoundationData).all()
    all_prospects = db_session.query(Prospect).all()

    # Prospects with foundation data
    prospect_ids_with_data = {f.prospect_id for f in foundations}
    missing = [p for p in all_prospects if p.id not in prospect_ids_with_data]

    # Parse program_areas JSON for each foundation
    for f in foundations:
        f._parsed_areas = json.loads(f.program_areas) if f.program_areas else []
        f._parsed_keywords = json.loads(f.focus_keywords) if f.focus_keywords else []

    # Aggregate stats across all foundations
    total_foundation_assets = sum(f.total_assets or 0 for f in foundations)
    total_foundation_grants = sum(f.total_grants_paid or 0 for f in foundations)
    total_foundation_revenue = sum(f.total_revenue or 0 for f in foundations)
    avg_grant_across = (total_foundation_grants / len(foundations)) if foundations else 0

    # Count by fit assessment
    fit_counts = {}
    for f in foundations:
        fit = f.fit_assessment or 'Unknown'
        fit_counts[fit] = fit_counts.get(fit, 0) + 1

    # Aggregate all program areas
    area_counts = {}
    for f in foundations:
        for area in f._parsed_areas:
            area_counts[area] = area_counts.get(area, 0) + 1
    sorted_areas = sorted(area_counts.items(), key=lambda x: -x[1])

    # Campus presence cross-reference
    campus_companies = {
        'De Anza College (Cupertino)': [],
        'Foothill College (Los Altos Hills)': [],
        'Chabot College (Hayward)': [],
    }
    campus_map = {
        'De Anza College': 'De Anza College (Cupertino)',
        'Foothill College': 'Foothill College (Los Altos Hills)',
        'Chabot College': 'Chabot College (Hayward)',
        'All Campuses': None,  # add to all
    }
    for p in all_prospects:
        campus = p.nearest_campus or ''
        if campus == 'All Campuses':
            for key in campus_companies:
                campus_companies[key].append(p)
        elif campus in campus_map and campus_map[campus]:
            campus_companies[campus_map[campus]].append(p)

    # Sort foundations by grants paid (largest first)
    foundations_sorted = sorted(foundations, key=lambda f: f.total_grants_paid or 0, reverse=True)

    return render_template('pages/analysis.html',
                           active_page='analysis',
                           foundations=foundations_sorted,
                           missing_foundations=missing,
                           all_prospects=all_prospects,
                           total_foundation_assets=total_foundation_assets,
                           total_foundation_grants=total_foundation_grants,
                           total_foundation_revenue=total_foundation_revenue,
                           avg_grant_across=avg_grant_across,
                           fit_counts=fit_counts,
                           sorted_areas=sorted_areas,
                           campus_companies=campus_companies,
                           format_millions=format_millions,
                           format_currency=format_currency,
                           format_pct=format_pct)


@analysis_bp.route('/api/prospect/<int:prospect_id>/fetch-990', methods=['POST'])
def api_fetch_990(prospect_id):
    """Fetch 990 data for a single prospect."""
    result = fetch_foundation_data(prospect_id)
    return jsonify(result)


@analysis_bp.route('/api/prospect/<int:prospect_id>/refetch-990', methods=['POST'])
def api_refetch_990(prospect_id):
    """Re-fetch 990 data for a prospect (overwrites existing)."""
    existing = db_session.query(FoundationData).filter_by(prospect_id=prospect_id).first()
    if existing:
        db_session.delete(existing)
        db_session.commit()
    result = fetch_foundation_data(prospect_id)
    return jsonify(result)


@analysis_bp.route('/api/fetch-all-990', methods=['POST'])
def api_fetch_all_990():
    """Fetch 990 data for all prospects."""
    prospects = db_session.query(Prospect).all()
    fetched = 0
    errors = 0
    skipped = 0

    for p in prospects:
        existing = db_session.query(FoundationData).filter_by(prospect_id=p.id).first()
        if existing:
            skipped += 1
            continue

        result = fetch_foundation_data(p.id)
        if isinstance(result, dict) and 'error' in result:
            errors += 1
        else:
            fetched += 1

    return jsonify({
        'message': f'Fetched {fetched} foundations, {errors} errors, {skipped} already loaded',
        'fetched': fetched,
        'errors': errors,
        'skipped': skipped,
    })


@analysis_bp.route('/api/refetch-all-990', methods=['POST'])
def api_refetch_all_990():
    """Re-fetch all 990 data (overwrite existing)."""
    db_session.query(FoundationData).delete()
    db_session.commit()

    prospects = db_session.query(Prospect).all()
    fetched = 0
    errors = 0

    for p in prospects:
        result = fetch_foundation_data(p.id)
        if isinstance(result, dict) and 'error' in result:
            errors += 1
        else:
            fetched += 1

    return jsonify({
        'message': f'Re-fetched {fetched} foundations, {errors} errors',
        'fetched': fetched,
        'errors': errors,
    })
