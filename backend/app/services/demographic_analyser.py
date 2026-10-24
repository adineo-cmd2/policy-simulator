"""Demographic rows: one row per group per first-order effect."""

_DIR_TO_IMPACT = {
    "positive": "Benefit",
    "negative": "Harm",
    "mixed": "Mixed",
}


def rows(firsts: list) -> list:
    out: list = []
    for f in firsts or []:
        direction = str(f.get("direction", "mixed")).lower()
        impact_type = _DIR_TO_IMPACT.get(direction, "Mixed")
        magnitude = f.get("magnitude", "unknown")
        if magnitude not in ("high", "medium", "low", "unknown"):
            magnitude = "unknown"
        title = f.get("title", "recorded effect")
        area = f.get("domain_area", f.get("area", "service area"))
        for group in f.get("groups", []) or []:
            out.append(
                {
                    "group_name": group,
                    "impact_type": impact_type,
                    "magnitude": magnitude,
                    "explanation": (
                        "Speculative modelling: "
                        f"{group} records {impact_type.lower()} outcome "
                        f"linked to {title} in {area}."
                    ),
                }
            )
    return out
