def recommend_option_with_explanation(row):
    """
    Returns:
      (recommended_option, score, reasons_list)
    """
    econ = row["net_value_reman"]
    eco = row["avoided_co2"]
    info = row["info_completeness"]

    score = (0.6 * econ) + (0.4 * eco) - ((1 - info) * 80)

    reasons = []
    # Reasons (simple, transparent, interview-friendly)
    if econ >= 80:
        reasons.append("High economic value (net value)")
    elif econ <= 20:
        reasons.append("Low economic value (net value)")

    if eco >= 200:
        reasons.append("High environmental benefit (avoided CO₂)")
    elif eco <= 80:
        reasons.append("Low environmental benefit (avoided CO₂)")

    if info >= 0.8:
        reasons.append("High information completeness (DPP-like)")
    elif info <= 0.5:
        reasons.append("Low information completeness → higher uncertainty")

    if score > 150:
        option = "Remanufacture"
        reasons.append("Overall score strongly favors remanufacturing")
    elif score > 80:
        option = "Reuse"
        reasons.append("Moderate score favors reuse")
    else:
        option = "Recycle"
        reasons.append("Low score → recycling is safer")

    # Keep reasons short for UI
    reasons = reasons[:3]
    return option, score, "; ".join(reasons)
