import pandas as pd

df = pd.read_csv("nau_calibrate.csv")
raw_estimates = df['Weight'] / df['Ratio']
offsets = df['Offset']
residuals = raw_estimates - offsets
optimal_offset = int(round((raw_estimates - residuals).mean()))

optimal_ratio = (df['Weight'] / (raw_estimates - optimal_offset)).mean()
print("\n--- Recalculated Optimal Calibration ---")
print(f"Offset: {optimal_offset}")
print(f"Ratio: {optimal_ratio}")
