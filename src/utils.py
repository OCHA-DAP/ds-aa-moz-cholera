import re
import pandas as pd
from unidecode import unidecode

def clean_week(week):
    if pd.isna(week):
        return None

    week_str = str(week).strip().lower()

    try:
        val = int(float(week_str))
        if 1 <= val <= 53:
            return val
    except:
        pass

    match = re.search(r"[wW][^\d]*?(\d{1,2})", week_str)
    if match:
        val = int(match.group(1))
        return val if 1 <= val <= 53 else None

    match = re.search(r"(\d{1,2})$", week_str)
    if match:
        val = int(match.group(1))
        return val if 1 <= val <= 53 else None

    return None




def infer_province_from_filename(filename):
    provinces = [
        "Cabo Delgado",
        "Gaza",
        "Inhambane",
        "Manica",
        "Maputo Provincia",
        "Maputo Cidade",
        "Nampula",
        "Niassa",
        "Sofala",
        "Tete",
        "Zambezia",
    ]
    filename_lower = filename.lower()

    for province in provinces:
        if province.lower().replace(" ", "") in filename_lower.replace(
            " ", ""
        ):
            return province
    return None

def parse_generalized_sheet(sheet_df, province, district):
    if district.strip().lower() in {
        "provincia de gaza",
        "sheet 1",
        "sheet1",
        "folha1",
        "folha2",
        "mprovincia",
        "distritos de mc e mp",
        "2025",
        "mprovincia",
        "provincia",
        "2",
        "distritos maputo provincia",
        "sofala",
        "tete",
    }:
        print(f"⚠️ Skipping invalid district: {district}")
        return

    sheet_df = sheet_df.dropna(how="all").dropna(axis=1, how="all")
    sheet_df.columns = sheet_df.columns.astype(str).str.strip()

    long_format_provinces = {
        "gaza",
        "manica",
        "sofala",
        "inhambane",
        "nampula",
        "tete",
    }
    wide_format_provinces = {
        "maputo cidade",
        "maputo provincia",
        "zambezia",
        "niassa",
        "cabo delgado",
    }
    province_clean = province.strip().lower()
    if province_clean not in long_format_provinces | wide_format_provinces:
        print(f"⚠️ Skipping unknown format: {province}")
        return

    is_long = province_clean in long_format_provinces

    if is_long:
        # --- LONG FORMAT ---
        for col in sheet_df.columns[1:11]:  # columns B to K
            try:
                year = int(
                    float(str(sheet_df[col].iloc[0]).replace(",", "").strip())
                )
            except:
                continue
            for i in range(1, sheet_df.shape[0]):
                week = sheet_df.iloc[i, 0]
                value = sheet_df.iloc[i][col]
                if pd.notna(week):
                    yield {
                        "province": province,
                        "district": district.strip().title(),
                        "year": year,
                        "week": clean_week(week),
                        "cases": value,
                    }

    else:
        # --- WIDE FORMAT ---
        print(f"Processing {province} in wide format")
        week_start_col = None
        for row_idx in [0, 1]:
            for i, val in enumerate(sheet_df.iloc[row_idx]):
                label = str(val).strip().lower()
                if label.startswith("s1") or label.startswith("1"):
                    week_start_col = i
                    break
            if week_start_col is not None:
                break
        if week_start_col is None or week_start_col == 0:
            print(
                f"⚠️ No valid week structure found in {province} - {district}"
            )

        year_col = sheet_df.columns[week_start_col - 1]
        week_cols = sheet_df.columns[week_start_col:]

        for _, row in sheet_df.iterrows():
            try:
                year = int(float(str(row[year_col]).replace(",", "").strip()))
            except:
                continue
            week_labels = sheet_df.iloc[
                row_idx, week_start_col:
            ].values  # row with S1, S2...
            value_cols = sheet_df.columns[week_start_col:]

            for week, week_col in zip(week_labels, value_cols):
                value = row[week_col]
                if pd.notna(value):
                    yield {
                        "province": province,
                        "district": district.strip().title(),
                        "year": year,
                        "week": clean_week(week),
                        "cases": value,
                    }

def normalize(text):
    text = unidecode(str(text).lower().strip())
    #text = text.replace("cidade", "city")
    return text