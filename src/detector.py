def detect_change(input_school, current_school):
    if not current_school or current_school == "Unknown":
        return "Not Found"

    if str(input_school).lower() != str(current_school).lower():
        return "Changed"

    return "Same"