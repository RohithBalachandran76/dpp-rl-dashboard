import pandas as pd

LABOR_RATE = 25  # €/hour
ENERGY_COST = 0.30  # €/kWh (simplified)
PROCESSING_ENERGY = 5  # kWh per unit (average)

def calculate_kpis(df):
    df = df.copy()

    # Convert disassembly time to hours
    df["disassembly_hours"] = df["disassembly_time_min"] / 60

    # Disassembly cost
    df["disassembly_cost"] = df["disassembly_hours"] * LABOR_RATE

    # Processing cost
    df["processing_cost"] = PROCESSING_ENERGY * ENERGY_COST

    # Example: Reman net value
    df["net_value_reman"] = (
        df["market_value_reman"]
        - df["disassembly_cost"]
        - df["processing_cost"]
    )

    # Avoided CO2 (reman replaces new production approx 80%)
    df["avoided_co2"] = df["co2_mfg_kg"] * 0.8

    return df
