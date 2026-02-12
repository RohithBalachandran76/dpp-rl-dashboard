def recommend_option(row):

    score = (
        0.6 * row["net_value_reman"]
        + 0.4 * row["avoided_co2"]
    )

    # Penalize missing information
    info_penalty = (1 - row["info_completeness"]) * 80
    score = score - info_penalty

    if score > 150:
        return "Remanufacture"
    elif score > 80:
        return "Reuse"
    else:
        return "Recycle"
