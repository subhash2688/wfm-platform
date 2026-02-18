"""Intelligence route — foundation data, top targets, cause heatmap."""
import json
from flask import Blueprint, render_template, jsonify
from models.database import db_session
from models.prospect import Prospect
from models.foundation import FoundationData
from models.contact import Contact
from services.propublica import fetch_foundation_data
from models.yearly_financial import YearlyFinancial
from models.foundation_grant import FoundationGrant
from models.foundation_officer import FoundationOfficer
from models.research_note import ResearchNote

intelligence_bp = Blueprint('intelligence', __name__)


def fmt_m(value):
    """Format large numbers into M/K shorthand."""
    if not value:
        return '$0'
    if value >= 1_000_000_000:
        return f'${value / 1_000_000_000:.1f}B'
    elif value >= 1_000_000:
        return f'${value / 1_000_000:.1f}M'
    elif value >= 1_000:
        return f'${value / 1_000:.0f}K'
    return f'${value:,.0f}'


def fmt_currency(value):
    if not value:
        return '$0'
    return f'${value:,.0f}'


@intelligence_bp.route('/intelligence')
def intelligence():
    foundations = db_session.query(FoundationData).all()
    all_prospects = db_session.query(Prospect).all()
    all_contacts = db_session.query(Contact).all()

    # Build contact lookup by prospect_id
    contact_map = {}
    for c in all_contacts:
        if c.prospect_id not in contact_map:
            contact_map[c.prospect_id] = c

    # Build foundation lookup by prospect_id
    foundation_map = {f.prospect_id: f for f in foundations}

    # Parse program_areas for each foundation
    for f in foundations:
        f._parsed_areas = json.loads(f.program_areas) if f.program_areas else []
        f._parsed_keywords = json.loads(f.focus_keywords) if f.focus_keywords else []

    # ─── Aggregate stats ───
    total_assets = sum(f.total_assets or 0 for f in foundations)
    total_grants = sum(f.total_grants_paid or 0 for f in foundations)
    avg_grant = (total_grants / len(foundations)) if foundations else 0

    # ─── Top 5 priority targets ───
    scored = sorted(all_prospects, key=lambda p: p.total_score or 0, reverse=True)
    top5 = []
    for p in scored[:5]:
        fd = foundation_map.get(p.id)
        ct = contact_map.get(p.id)
        top5.append({
            'prospect': p,
            'foundation': fd,
            'contact': ct,
            'grants_paid': fmt_m(fd.total_grants_paid) if fd else 'N/A',
            'focus': p.focus_areas or 'Not researched',
        })

    # ─── Key insights ─── (auto-generated from data)
    insights = []

    # Find foundations that explicitly fund food/hunger
    food_foundations = []
    for f in foundations:
        areas = f._parsed_areas
        keywords = f._parsed_keywords
        all_terms = [a.lower() for a in areas] + [k.lower() for k in keywords]
        if any(t in ' '.join(all_terms) for t in ['food', 'hunger', 'meal', 'nutrition', 'feeding']):
            p = next((pr for pr in all_prospects if pr.id == f.prospect_id), None)
            if p:
                food_foundations.append((p.company_name, f))

    if food_foundations:
        names = ', '.join(name for name, _ in food_foundations[:3])
        insights.append(f'<strong>{len(food_foundations)} foundations</strong> fund food & hunger programs directly, including {names}.')

    # Find largest grant maker
    if foundations:
        top_fdn = max(foundations, key=lambda f: f.total_grants_paid or 0)
        top_prospect = next((p for p in all_prospects if p.id == top_fdn.prospect_id), None)
        if top_prospect and top_fdn.total_grants_paid:
            insights.append(
                f'<strong>{top_prospect.company_name}</strong> is the largest funder at '
                f'{fmt_m(top_fdn.total_grants_paid)} in grants paid.'
            )

    # Alignment 5 prospects
    high_align = [p for p in all_prospects if (p.alignment_score or 0) == 5]
    if high_align:
        names = ', '.join(p.company_name for p in high_align[:4])
        insights.append(
            f'<strong>{len(high_align)} prospects</strong> have perfect alignment (score 5): {names}.'
        )

    # Proximity 5 prospects
    local = [p for p in all_prospects if (p.proximity_score or 0) == 5]
    if local:
        insights.append(
            f'<strong>{len(local)} companies</strong> are headquartered in a campus city '
            f'(Cupertino, Los Altos Hills, or Hayward).'
        )

    # ─── Cause heatmap ───
    area_counts = {}
    for f in foundations:
        for area in f._parsed_areas:
            area_counts[area] = area_counts.get(area, 0) + 1
    sorted_areas = sorted(area_counts.items(), key=lambda x: -x[1])[:12]
    max_count = sorted_areas[0][1] if sorted_areas else 1

    # ─── Fit counts ───
    fit_counts = {}
    for f in foundations:
        fit = f.fit_assessment or 'Unknown'
        fit_counts[fit] = fit_counts.get(fit, 0) + 1

    # Sort foundations by grants paid
    foundations_sorted = sorted(foundations, key=lambda f: f.total_grants_paid or 0, reverse=True)

    # Prospects without foundation data
    ids_with_data = {f.prospect_id for f in foundations}
    missing = [p for p in all_prospects if p.id not in ids_with_data]

    # ─── Deep research stats ───
    deep_done = sum(1 for f in foundations if f.deep_research_at)
    deep_pending = len(foundations) - deep_done

    # ─── Giving trends ───
    trend_growing = sum(1 for f in foundations if f.giving_trend == 'growing')
    trend_stable = sum(1 for f in foundations if f.giving_trend == 'stable')
    trend_declining = sum(1 for f in foundations if f.giving_trend == 'declining')

    # ─── Cross-foundation grantee category distribution ───
    all_grants = db_session.query(FoundationGrant).all()
    category_totals = {}
    for g in all_grants:
        cat = g.category or 'other'
        category_totals[cat] = category_totals.get(cat, 0) + (g.amount or 0)
    sorted_categories = sorted(category_totals.items(), key=lambda x: -x[1])
    max_cat_amount = sorted_categories[0][1] if sorted_categories else 1

    return render_template('pages/intelligence.html',
                           active_page='intelligence',
                           foundations=foundations_sorted,
                           missing_foundations=missing,
                           all_prospects=all_prospects,
                           top5=top5,
                           insights=insights,
                           sorted_areas=sorted_areas,
                           max_area_count=max_count,
                           fit_counts=fit_counts,
                           total_assets=total_assets,
                           total_grants=total_grants,
                           avg_grant=avg_grant,
                           foundation_count=len(foundations),
                           fmt_m=fmt_m,
                           fmt_currency=fmt_currency,
                           deep_done=deep_done,
                           deep_pending=deep_pending,
                           trend_growing=trend_growing,
                           trend_stable=trend_stable,
                           trend_declining=trend_declining,
                           sorted_categories=sorted_categories,
                           max_cat_amount=max_cat_amount)


# ─── 990 API endpoints (moved from old analysis route) ───

@intelligence_bp.route('/api/prospect/<int:prospect_id>/fetch-990', methods=['POST'])
def api_fetch_990(prospect_id):
    result = fetch_foundation_data(prospect_id)
    return jsonify(result)


@intelligence_bp.route('/api/prospect/<int:prospect_id>/refetch-990', methods=['POST'])
def api_refetch_990(prospect_id):
    existing = db_session.query(FoundationData).filter_by(prospect_id=prospect_id).first()
    if existing:
        db_session.delete(existing)
        db_session.commit()
    result = fetch_foundation_data(prospect_id)
    return jsonify(result)


@intelligence_bp.route('/api/fetch-all-990', methods=['POST'])
def api_fetch_all_990():
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
        'fetched': fetched, 'errors': errors, 'skipped': skipped,
    })


@intelligence_bp.route('/api/refetch-all-990', methods=['POST'])
def api_refetch_all_990():
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
        'fetched': fetched, 'errors': errors,
    })


@intelligence_bp.route('/api/prospect/<int:prospect_id>/deep-research', methods=['POST'])
def api_deep_research(prospect_id):
    """Trigger deep 990 research for one prospect."""
    from services.propublica import deep_research
    foundation = db_session.query(FoundationData).filter_by(prospect_id=prospect_id).first()
    if not foundation:
        return jsonify({'error': 'No foundation data. Fetch 990 first.'}), 400
    result = deep_research(foundation.id)
    return jsonify(result)


@intelligence_bp.route('/api/deep-research-all', methods=['POST'])
def api_deep_research_all():
    """Batch deep research for all foundations."""
    from services.propublica import deep_research
    foundations = db_session.query(FoundationData).all()
    done = 0
    errors = 0
    skipped = 0
    for f in foundations:
        if f.deep_research_at:
            skipped += 1
            continue
        try:
            result = deep_research(f.id)
            if isinstance(result, dict) and 'error' in result:
                errors += 1
            else:
                done += 1
        except Exception:
            errors += 1
    return jsonify({
        'message': f'Deep research: {done} done, {errors} errors, {skipped} skipped',
        'done': done, 'errors': errors, 'skipped': skipped,
    })


@intelligence_bp.route('/api/prospect/<int:prospect_id>/yearly-financials')
def api_yearly_financials(prospect_id):
    """Get multi-year financial data for charts."""
    foundation = db_session.query(FoundationData).filter_by(prospect_id=prospect_id).first()
    if not foundation:
        return jsonify([])
    years = (db_session.query(YearlyFinancial)
             .filter_by(foundation_data_id=foundation.id)
             .order_by(YearlyFinancial.tax_year)
             .all())
    return jsonify([y.to_dict() for y in years])


@intelligence_bp.route('/api/prospect/<int:prospect_id>/grantees')
def api_grantees(prospect_id):
    """Get Schedule I grantee list."""
    foundation = db_session.query(FoundationData).filter_by(prospect_id=prospect_id).first()
    if not foundation:
        return jsonify([])
    grants = (db_session.query(FoundationGrant)
              .filter_by(foundation_data_id=foundation.id)
              .order_by(FoundationGrant.amount.desc())
              .all())
    return jsonify([g.to_dict() for g in grants])


@intelligence_bp.route('/api/prospect/<int:prospect_id>/officers')
def api_officers(prospect_id):
    """Get Part VII officer list."""
    foundation = db_session.query(FoundationData).filter_by(prospect_id=prospect_id).first()
    if not foundation:
        return jsonify([])
    officers = (db_session.query(FoundationOfficer)
                .filter_by(foundation_data_id=foundation.id)
                .order_by(FoundationOfficer.compensation.desc())
                .all())
    return jsonify([o.to_dict() for o in officers])


@intelligence_bp.route('/api/prospect/<int:prospect_id>/research-note', methods=['POST'])
def api_add_research_note(prospect_id):
    """Add a research note."""
    from flask import request
    from services.news_research import add_research_note
    data = request.get_json()
    result = add_research_note(
        prospect_id=prospect_id,
        note_type=data.get('note_type', 'insight'),
        title=data.get('title', ''),
        content=data.get('content', ''),
        source_url=data.get('source_url'),
        published_date=data.get('published_date'),
    )
    return jsonify(result)


@intelligence_bp.route('/api/research-note/<int:note_id>', methods=['DELETE'])
def api_delete_research_note(note_id):
    """Delete a research note."""
    from services.news_research import delete_research_note
    result = delete_research_note(note_id)
    return jsonify(result)
