def recommend_option(row):
    score = (
        0.6 * row["net_value_reman"]
        + 0.4 * row["avoided_co2"]
        - (1 - row["info_completeness"]) * 50
    )

    if score > 150:
        return "Remanufacture"
    elif score > 80:
        return "Reuse"
    else:
        return "Recycle"
