"""Stakeholder map derived from first-order direction + magnitude."""

_DIR_TO_STANCE = {
    "positive": "benefit",
    "negative": "harm",
    "mixed": "mixed",
}

_BASE_RATING = {
    "benefit": 4,
    "harm": 2,
    "mixed": 3,
}


def map(firsts: list) -> list:  # noqa: A003 - brief-specified name
    out: list = []
    for f in firsts or []:
        direction = str(f.get("direction", "mixed")).lower()
        stance = _DIR_TO_STANCE.get(direction, "mixed")
        magnitude = f.get("magnitude", "unknown")
        rating = _BASE_RATING[stance]
        if magnitude == "high":
            rating += 1
        elif magnitude == "low":
            rating -= 1
        rating = max(1, min(5, rating))
        title = f.get("title", "recorded effect")
        for group in f.get("groups", []) or []:
            out.append(
                {
                    "group_name": group,
                    "stance": stance,
                    "rating": rating,
                    "explanation": (
                        "Speculative modelling: "
                        f"{group} records {stance} position linked to {title}; "
                        f"administrative record notes {magnitude} magnitude."
                    ),
                }
            )
    return out
