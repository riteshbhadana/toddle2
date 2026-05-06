def detect_change(input_school: str, current_school: str) -> str:
    """
    Compare the school from the uploaded file vs what was found on LinkedIn.

    Returns:
        "Not Found"  – LinkedIn profile or school info was not found
        "Changed"    – Person is now at a different school/org
        "Same"       – School matches
    """
    if not current_school or current_school.strip().lower() in ("unknown", "not found", ""):
        return "Not Found"

    # Normalise: lower-case, strip whitespace
    inp  = str(input_school).strip().lower()
    curr = str(current_school).strip().lower()

    if inp == curr:
        return "Same"

    # Partial-match guard: "IIT Delhi" vs "IIT Delhi (Indian Institute…)"
    if inp in curr or curr in inp:
        return "Same"

    return "Changed"
