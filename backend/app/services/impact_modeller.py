"""Template impact modeller: domain packs -> 3-level effect tree.

Administrative/descriptive wording only. All projections labelled
as speculative modelling.
"""

import os
import re
from collections import Counter

MAGNITUDES = ("high", "medium", "low", "unknown")
DIRECTIONS = ("positive", "negative", "mixed")
CONFIDENCES = ("high", "medium", "speculative")

_BANNED = [
    "corrupt", "stupid", "evil", "disaster", "tyranny", "fascist",
    "communist", "socialist", "radical", "extremist", "woke",
    "elite conspiracy", "steal", "destroy",
]

_STOP = {
    "the", "and", "with", "from", "that", "this", "have", "will",
    "should", "would", "could", "their", "there", "which", "about",
    "into", "over", "under", "policy", "proposed", "proposal",
    "city", "area", "areas", "annual", "urban", "rural", "national",
    "local", "general",
}

DOMAIN_PACKS = {
    "housing": {
        "firsts": [
            {
                "area": "rental supply",
                "title": "Rental supply adjustment",
                "detail_t": (
                    "Speculative modelling: the {mech} is administered in {jur}; "
                    "rental listings and permit applications adjust in recorded sequence."
                ),
                "groups": ["low-income households", "urban populations", "rental providers"],
                "magnitude": "medium",
                "direction": "mixed",
                "confidence": "medium",
                "analogy": "Metropolitan rent stabilisation precedent",
            },
            {
                "area": "permit processing",
                "title": "Permit processing timeline",
                "detail_t": (
                    "Speculative modelling: the {mech} is applied in {jur}; "
                    "permit review queues record revised timelines and filing volumes."
                ),
                "groups": ["high-income households", "youth", "rental providers"],
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
                "analogy": "Harborview permit review precedent",
            },
        ],
        "seconds": [
            {
                "title_t": "Administrative response in rental offices",
                "detail_t": (
                    "Speculative modelling: offices administering the {mech} in {jur} "
                    "record procedural responses and revised inspection schedules."
                ),
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
            },
            {
                "title_t": "Maintenance scheduling response",
                "detail_t": (
                    "Speculative modelling: maintenance scheduling linked to the {mech} "
                    "in {jur} records adjusted service intervals."
                ),
                "magnitude": "low",
                "direction": "negative",
                "confidence": "speculative",
            },
        ],
        "thirds": [
            {
                "title_t": "Settlement pattern observation",
                "detail_t": (
                    "Speculative modelling: settlement patterns following the {mech} "
                    "in {jur} are recorded through address and tenure statistics."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
            {
                "title_t": "Construction pipeline observation",
                "detail_t": (
                    "Speculative modelling: the construction pipeline related to the {mech} "
                    "in {jur} is described through starts and completions data."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
    },
    "healthcare": {
        "firsts": [
            {
                "area": "clinic capacity",
                "title": "Clinic capacity adjustment",
                "detail_t": (
                    "Speculative modelling: the {mech} is administered in {jur}; "
                    "clinic appointment capacity records revised throughput."
                ),
                "groups": ["low-income households", "elderly", "care providers"],
                "magnitude": "medium",
                "direction": "positive",
                "confidence": "medium",
                "analogy": "Northshire clinic access precedent",
            },
            {
                "area": "waiting times",
                "title": "Waiting time record",
                "detail_t": (
                    "Speculative modelling: the {mech} is applied in {jur}; "
                    "waiting time statistics record revised referral intervals."
                ),
                "groups": ["rural populations", "elderly", "care providers"],
                "magnitude": "medium",
                "direction": "mixed",
                "confidence": "medium",
                "analogy": "Eastvale triage scheduling precedent",
            },
        ],
        "seconds": [
            {
                "title_t": "Staffing roster response",
                "detail_t": (
                    "Speculative modelling: staffing rosters supporting the {mech} "
                    "in {jur} record revised shift allocation."
                ),
                "magnitude": "medium",
                "direction": "mixed",
                "confidence": "medium",
            },
            {
                "title_t": "Referral pathway response",
                "detail_t": (
                    "Speculative modelling: referral pathways linked to the {mech} "
                    "in {jur} record adjusted routing between care levels."
                ),
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
        "thirds": [
            {
                "title_t": "Preventive visit observation",
                "detail_t": (
                    "Speculative modelling: preventive visit counts following the {mech} "
                    "in {jur} are described through attendance records."
                ),
                "magnitude": "unknown",
                "direction": "positive",
                "confidence": "speculative",
            },
            {
                "title_t": "Regional access observation",
                "detail_t": (
                    "Speculative modelling: regional access patterns related to the {mech} "
                    "in {jur} are recorded through facility usage data."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
    },
    "taxation": {
        "firsts": [
            {
                "area": "filing compliance",
                "title": "Filing compliance record",
                "detail_t": (
                    "Speculative modelling: the {mech} is administered in {jur}; "
                    "filing records show revised submission timing and completeness."
                ),
                "groups": ["low-income households", "high-income households", "small businesses"],
                "magnitude": "medium",
                "direction": "mixed",
                "confidence": "medium",
                "analogy": "Brookfield filing reform precedent",
            },
            {
                "area": "revenue collection",
                "title": "Revenue collection summary",
                "detail_t": (
                    "Speculative modelling: the {mech} is applied in {jur}; "
                    "collection summaries record revised receipt totals by quarter."
                ),
                "groups": ["urban populations", "elderly", "small businesses"],
                "magnitude": "high",
                "direction": "positive",
                "confidence": "medium",
                "analogy": "Dunmore revenue schedule precedent",
            },
        ],
        "seconds": [
            {
                "title_t": "Advisory service response",
                "detail_t": (
                    "Speculative modelling: advisory services describing the {mech} "
                    "in {jur} record revised inquiry volumes."
                ),
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
            },
            {
                "title_t": "Budget planning response",
                "detail_t": (
                    "Speculative modelling: budget planning linked to the {mech} "
                    "in {jur} records adjusted allocation schedules."
                ),
                "magnitude": "medium",
                "direction": "mixed",
                "confidence": "medium",
            },
        ],
        "thirds": [
            {
                "title_t": "Investment timing observation",
                "detail_t": (
                    "Speculative modelling: investment timing following the {mech} "
                    "in {jur} is described through recorded filing and ledger data."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
            {
                "title_t": "Consumption pattern observation",
                "detail_t": (
                    "Speculative modelling: consumption patterns related to the {mech} "
                    "in {jur} are recorded through retail receipt summaries."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
    },
    "environment": {
        "firsts": [
            {
                "area": "emission levels",
                "title": "Emission level record",
                "detail_t": (
                    "Speculative modelling: the {mech} is administered in {jur}; "
                    "monitored emission readings record revised concentration levels."
                ),
                "groups": ["rural populations", "urban populations", "energy operators"],
                "magnitude": "medium",
                "direction": "positive",
                "confidence": "medium",
                "analogy": "Clearwater emission standard precedent",
            },
            {
                "area": "waste collection",
                "title": "Waste collection summary",
                "detail_t": (
                    "Speculative modelling: the {mech} is applied in {jur}; "
                    "collection logs record revised sorting and diversion volumes."
                ),
                "groups": ["urban populations", "youth", "energy operators"],
                "magnitude": "low",
                "direction": "positive",
                "confidence": "medium",
                "analogy": "Greenfield sorting program precedent",
            },
        ],
        "seconds": [
            {
                "title_t": "Inspection routine response",
                "detail_t": (
                    "Speculative modelling: inspection routines supporting the {mech} "
                    "in {jur} record revised visit frequency."
                ),
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
            },
            {
                "title_t": "Recycling market response",
                "detail_t": (
                    "Speculative modelling: material recovery markets linked to the {mech} "
                    "in {jur} record adjusted throughput volumes."
                ),
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
        "thirds": [
            {
                "title_t": "Air quality observation",
                "detail_t": (
                    "Speculative modelling: air quality readings following the {mech} "
                    "in {jur} are described through monitoring station data."
                ),
                "magnitude": "unknown",
                "direction": "positive",
                "confidence": "speculative",
            },
            {
                "title_t": "Habitat indicator observation",
                "detail_t": (
                    "Speculative modelling: habitat indicators related to the {mech} "
                    "in {jur} are recorded through survey counts."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
    },
    "education": {
        "firsts": [
            {
                "area": "enrolment levels",
                "title": "Enrolment level record",
                "detail_t": (
                    "Speculative modelling: the {mech} is administered in {jur}; "
                    "enrolment registers record revised intake counts."
                ),
                "groups": ["low-income households", "youth", "education providers"],
                "magnitude": "medium",
                "direction": "positive",
                "confidence": "medium",
                "analogy": "Milltown enrolment program precedent",
            },
            {
                "area": "tutoring provision",
                "title": "Tutoring provision summary",
                "detail_t": (
                    "Speculative modelling: the {mech} is applied in {jur}; "
                    "tutoring session logs record revised delivery hours."
                ),
                "groups": ["rural populations", "youth", "education providers"],
                "magnitude": "low",
                "direction": "positive",
                "confidence": "medium",
                "analogy": "Lakeside tutoring grant precedent",
            },
        ],
        "seconds": [
            {
                "title_t": "Teacher allocation response",
                "detail_t": (
                    "Speculative modelling: teacher allocation supporting the {mech} "
                    "in {jur} records revised class assignments."
                ),
                "magnitude": "medium",
                "direction": "mixed",
                "confidence": "medium",
            },
            {
                "title_t": "Curriculum scheduling response",
                "detail_t": (
                    "Speculative modelling: curriculum scheduling linked to the {mech} "
                    "in {jur} records adjusted timetable entries."
                ),
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
        "thirds": [
            {
                "title_t": "Completion rate observation",
                "detail_t": (
                    "Speculative modelling: completion rates following the {mech} "
                    "in {jur} are described through graduation records."
                ),
                "magnitude": "unknown",
                "direction": "positive",
                "confidence": "speculative",
            },
            {
                "title_t": "Literacy indicator observation",
                "detail_t": (
                    "Speculative modelling: literacy indicators related to the {mech} "
                    "in {jur} are recorded through assessment summaries."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
    },
    "labour": {
        "firsts": [
            {
                "area": "hiring activity",
                "title": "Hiring activity record",
                "detail_t": (
                    "Speculative modelling: the {mech} is administered in {jur}; "
                    "hiring announcements record revised vacancy postings."
                ),
                "groups": ["low-income households", "youth", "employers"],
                "magnitude": "medium",
                "direction": "mixed",
                "confidence": "medium",
                "analogy": "Ironbridge hiring code precedent",
            },
            {
                "area": "wage records",
                "title": "Wage record summary",
                "detail_t": (
                    "Speculative modelling: the {mech} is applied in {jur}; "
                    "payroll summaries record revised wage entries."
                ),
                "groups": ["low-income households", "urban populations", "employers"],
                "magnitude": "medium",
                "direction": "positive",
                "confidence": "medium",
                "analogy": "Portwell wage schedule precedent",
            },
        ],
        "seconds": [
            {
                "title_t": "Training enrolment response",
                "detail_t": (
                    "Speculative modelling: training enrolment linked to the {mech} "
                    "in {jur} records revised course registrations."
                ),
                "magnitude": "low",
                "direction": "positive",
                "confidence": "speculative",
            },
            {
                "title_t": "Shift planning response",
                "detail_t": (
                    "Speculative modelling: shift planning related to the {mech} "
                    "in {jur} records adjusted roster entries."
                ),
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
        "thirds": [
            {
                "title_t": "Participation rate observation",
                "detail_t": (
                    "Speculative modelling: participation rates following the {mech} "
                    "in {jur} are described through labour survey records."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
            {
                "title_t": "Retention indicator observation",
                "detail_t": (
                    "Speculative modelling: retention indicators related to the {mech} "
                    "in {jur} are recorded through tenure summaries."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
    },
    "trade": {
        "firsts": [
            {
                "area": "import volumes",
                "title": "Import volume record",
                "detail_t": (
                    "Speculative modelling: the {mech} is administered in {jur}; "
                    "customs logs record revised import declarations."
                ),
                "groups": ["urban populations", "high-income households", "trading firms"],
                "magnitude": "medium",
                "direction": "mixed",
                "confidence": "medium",
                "analogy": "Seagate tariff schedule precedent",
            },
            {
                "area": "export documentation",
                "title": "Export documentation summary",
                "detail_t": (
                    "Speculative modelling: the {mech} is applied in {jur}; "
                    "export documentation records revised certificate counts."
                ),
                "groups": ["rural populations", "low-income households", "trading firms"],
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
                "analogy": "Northport export procedure precedent",
            },
        ],
        "seconds": [
            {
                "title_t": "Logistics scheduling response",
                "detail_t": (
                    "Speculative modelling: logistics scheduling linked to the {mech} "
                    "in {jur} records revised freight bookings."
                ),
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
            },
            {
                "title_t": "Customs staffing response",
                "detail_t": (
                    "Speculative modelling: customs staffing supporting the {mech} "
                    "in {jur} records revised desk assignments."
                ),
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
        "thirds": [
            {
                "title_t": "Price level observation",
                "detail_t": (
                    "Speculative modelling: price levels following the {mech} "
                    "in {jur} are described through recorded retail indices."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
            {
                "title_t": "Supply continuity observation",
                "detail_t": (
                    "Speculative modelling: supply continuity related to the {mech} "
                    "in {jur} is recorded through delivery completion data."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
    },
    "general": {
        "firsts": [
            {
                "area": "service uptake",
                "title": "Service uptake record",
                "detail_t": (
                    "Speculative modelling: the {mech} is administered in {jur}; "
                    "service uptake logs record revised application counts."
                ),
                "groups": ["low-income households", "urban populations", "community organisations"],
                "magnitude": "medium",
                "direction": "mixed",
                "confidence": "medium",
                "analogy": "Civic service pilot precedent",
            },
            {
                "area": "information requests",
                "title": "Information request summary",
                "detail_t": (
                    "Speculative modelling: the {mech} is applied in {jur}; "
                    "information request records show revised inquiry volumes."
                ),
                "groups": ["rural populations", "elderly", "community organisations"],
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
                "analogy": "Civic information desk precedent",
            },
        ],
        "seconds": [
            {
                "title_t": "Office procedure response",
                "detail_t": (
                    "Speculative modelling: office procedures supporting the {mech} "
                    "in {jur} record revised case handling steps."
                ),
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
            },
            {
                "title_t": "Outreach activity response",
                "detail_t": (
                    "Speculative modelling: outreach activity linked to the {mech} "
                    "in {jur} records revised event schedules."
                ),
                "magnitude": "low",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
        "thirds": [
            {
                "title_t": "Participation observation",
                "detail_t": (
                    "Speculative modelling: participation counts following the {mech} "
                    "in {jur} are described through attendance summaries."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
            {
                "title_t": "Administrative load observation",
                "detail_t": (
                    "Speculative modelling: administrative load related to the {mech} "
                    "in {jur} is recorded through caseload statistics."
                ),
                "magnitude": "unknown",
                "direction": "mixed",
                "confidence": "speculative",
            },
        ],
    },
}


def _extract_mech(policy_text: str, domain: str) -> str:
    words = re.findall(r"[A-Za-z]{4,}", policy_text or "")
    freq = Counter(
        w.lower() for w in words if w.lower() not in _STOP
    )
    if freq:
        top, _ = freq.most_common(1)[0]
        if any(b in top for b in _BANNED):
            return f"{domain} measure"
        return f"{top} measure"
    return f"{domain} measure"


def _resolve_jur(jurisdiction: str) -> str:
    j = (jurisdiction or "").strip()
    return j if j else "the jurisdiction"


def model(policy_text: str, jurisdiction: str, domain: str) -> list:
    """Build 3-level template tree; flat list with parent_idx + children."""
    key = (domain or "").lower().strip() or "general"
    if key not in DOMAIN_PACKS:
        key = "general"
    pack = DOMAIN_PACKS[key]
    if os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
        # LLM hook: v1 keeps template output for determinism.
        pass
    mech = _extract_mech(policy_text or "", key)
    jur = _resolve_jur(jurisdiction or "")
    nodes: list = []
    for i, first in enumerate(pack["firsts"]):
        second = pack["seconds"][i]
        third = pack["thirds"][i]
        first_idx = len(nodes)
        nodes.append(
            {
                "order": 1,
                "title": first["title"].format(mech=mech, jur=jur),
                "detail": first["detail_t"].format(mech=mech, jur=jur),
                "domain_area": first["area"],
                "magnitude": first["magnitude"],
                "direction": first["direction"],
                "confidence": first["confidence"],
                "analogy": first["analogy"],
                "parent_idx": None,
                "children": [],
                "groups": list(first["groups"]),
            }
        )
        second_idx = len(nodes)
        nodes.append(
            {
                "order": 2,
                "title": second["title_t"].format(mech=mech, jur=jur),
                "detail": second["detail_t"].format(mech=mech, jur=jur),
                "domain_area": first["area"],
                "magnitude": second["magnitude"],
                "direction": second["direction"],
                "confidence": second["confidence"],
                "analogy": "",
                "parent_idx": first_idx,
                "children": [],
                "groups": [],
            }
        )
        third_idx = len(nodes)
        nodes.append(
            {
                "order": 3,
                "title": third["title_t"].format(mech=mech, jur=jur),
                "detail": third["detail_t"].format(mech=mech, jur=jur),
                "domain_area": first["area"],
                "magnitude": third["magnitude"],
                "direction": third["direction"],
                "confidence": third["confidence"],
                "analogy": "",
                "parent_idx": second_idx,
                "children": [],
                "groups": [],
            }
        )
        nodes[first_idx]["children"] = [second_idx]
        nodes[second_idx]["children"] = [third_idx]
    return nodes
