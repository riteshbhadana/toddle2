def calculate_score(name, input_school, current_school):
    score = 0

    if current_school != "Unknown":
        score += 30

    if input_school.lower() in current_school.lower():
        score += 40

    if name.split()[0].lower() in name.lower():
        score += 30

    return score