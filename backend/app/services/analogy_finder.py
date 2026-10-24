"""Historical analogy pool + keyword match."""

import re

ANALOGIES = {
    "housing": [
        {
            "title": "Metropolitan rent stabilisation",
            "jurisdiction": "Harborview",
            "year": 1998,
            "outcome": "Rents held steady while permits slowed; evidence mixed.",
        },
        {
            "title": "Harborview permit review update",
            "jurisdiction": "Harborview",
            "year": 2005,
            "outcome": "Review timelines recorded revised queues; outcomes varied by district.",
        },
    ],
    "healthcare": [
        {
            "title": "Northshire clinic access program",
            "jurisdiction": "Northshire",
            "year": 2003,
            "outcome": "Appointment throughput recorded revised levels; follow-up visits varied.",
        },
        {
            "title": "Eastvale triage scheduling reform",
            "jurisdiction": "Eastvale",
            "year": 2011,
            "outcome": "Waiting time statistics recorded revised intervals; evidence mixed.",
        },
    ],
    "taxation": [
        {
            "title": "Brookfield filing reform",
            "jurisdiction": "Brookfield",
            "year": 2001,
            "outcome": "Filing completeness recorded revised timing; receipts varied by quarter.",
        },
        {
            "title": "Dunmore revenue schedule update",
            "jurisdiction": "Dunmore",
            "year": 2009,
            "outcome": "Collection summaries recorded revised totals; compliance varied.",
        },
    ],
    "environment": [
        {
            "title": "Clearwater emission standard",
            "jurisdiction": "Clearwater",
            "year": 1995,
            "outcome": "Monitored readings recorded revised levels; sector outcomes varied.",
        },
        {
            "title": "Greenfield sorting program",
            "jurisdiction": "Greenfield",
            "year": 2007,
            "outcome": "Diversion volumes recorded revised totals; participation varied.",
        },
    ],
    "education": [
        {
            "title": "Milltown enrolment program",
            "jurisdiction": "Milltown",
            "year": 2000,
            "outcome": "Intake counts recorded revised levels; completion varied by cohort.",
        },
        {
            "title": "Lakeside tutoring grant",
            "jurisdiction": "Lakeside",
            "year": 2012,
            "outcome": "Session hours recorded revised delivery; attendance varied.",
        },
    ],
    "labour": [
        {
            "title": "Ironbridge hiring code",
            "jurisdiction": "Ironbridge",
            "year": 2002,
            "outcome": "Vacancy postings recorded revised counts; retention varied.",
        },
        {
            "title": "Portwell wage schedule",
            "jurisdiction": "Portwell",
            "year": 2010,
            "outcome": "Payroll entries recorded revised levels; hiring varied by sector.",
        },
    ],
    "trade": [
        {
            "title": "Seagate tariff schedule",
            "jurisdiction": "Seagate",
            "year": 1999,
            "outcome": "Import declarations recorded revised volumes; prices varied.",
        },
        {
            "title": "Northport export procedure",
            "jurisdiction": "Northport",
            "year": 2008,
            "outcome": "Certificate counts recorded revised totals; delivery varied.",
        },
    ],
    "general": [
        {
            "title": "Civic service pilot",
            "jurisdiction": "Civic County",
            "year": 2004,
            "outcome": "Application counts recorded revised levels; uptake varied.",
        },
        {
            "title": "Civic information desk program",
            "jurisdiction": "Civic County",
            "year": 2013,
            "outcome": "Inquiry volumes recorded revised totals; outcomes varied.",
        },
    ],
}


def find(domain: str, area: str) -> dict:
    key = (domain or "").lower().strip()
    if key not in ANALOGIES:
        key = "general"
    pool = ANALOGIES[key]
    words = [w for w in re.findall(r"[A-Za-z]{4,}", area or "") if len(w) >= 4]
    lowered = [w.lower() for w in words]
    for entry in pool:
        title_low = entry["title"].lower()
        if any(w in title_low for w in lowered):
            return {**entry, "similarity": "high"}
    return {**pool[0], "similarity": "medium"}
