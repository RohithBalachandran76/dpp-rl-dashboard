import pandas as pd

LABOR_RATE = 25
ENERGY_COST = 0.30
PROCESSING_ENERGY = 5

# Conservative defaults (used when info missing)
DEFAULT_DISASSEMBLY_MIN = 75
DEFAULT_REPAIRABILITY = 4
DEFAULT_CO2_MFG = 320

def calculate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Fill missing values with conservative defaults
    df["disassembly_time_min"] = pd.to_numeric(
        df["disassembly_time_min"], errors="coerce"
    ).fillna(DEFAULT_DISASSEMBLY_MIN)

    df["repairability_score"] = pd.to_numeric(
        df["repairability_score"], errors="coerce"
    ).fillna(DEFAULT_REPAIRABILITY)

    df["co2_mfg_kg"] = pd.to_numeric(
        df["co2_mfg_kg"], errors="coerce"
    ).fillna(DEFAULT_CO2_MFG)

    # Convert time to hours
    df["disassembly_hours"] = df["disassembly_time_min"] / 60

    # Cost calculations
    df["disassembly_cost"] = df["disassembly_hours"] * LABOR_RATE
    df["processing_cost"] = PROCESSING_ENERGY * ENERGY_COST

    # Net value (remanufacturing case)
    df["net_value_reman"] = (
        df["market_value_reman"]
        - df["disassembly_cost"]
        - df["processing_cost"]
    )

    # Avoided CO2
    df["avoided_co2"] = df["co2_mfg_kg"] * 0.8

    return df
