"""Load and normalize the Clean Data worksheet."""

from io import BytesIO

import pandas as pd
import requests
import streamlit as st

SHEET_ID = "1sqMBlw0EjRBMxgL1Fw9iGpzZ-JW5lVR5TQx5qiJW9-c"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=924561124"
EXPECTED = ("Harvest Date", "Farm", "Crop", "KG", "Group", "Incentive Per Crop")


def parse_numbers(values):
    text = values.astype("string").str.strip().str.replace(r"[,\s]", "", regex=True)
    text = text.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    text = text.str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(text, errors="coerce")


def parse_dates(values):
    text = values.astype("string").str.strip()
    serial = pd.to_numeric(text, errors="coerce")
    # Excel/Sheets serial dates; avoid interpreting arbitrary numeric strings as dates.
    is_serial = serial.between(1, 100000).fillna(False)
    result = pd.to_datetime(text.where(~is_serial), errors="coerce", format="mixed")
    result.loc[is_serial] = pd.to_datetime(serial[is_serial], unit="D", origin="1899-12-30", errors="coerce")
    return result


def clean_data(raw):
    # Use column names so inserted or reordered columns do not change the metrics.
    normalized = [str(name).strip().lstrip("\ufeff").casefold() for name in raw.columns]
    positions = []
    for expected in EXPECTED:
        matches = [i for i, name in enumerate(normalized) if name == expected.casefold()]
        if len(matches) != 1:
            raise ValueError(f"Clean Data must contain exactly one '{expected}' column.")
        positions.append(matches[0])
    df = raw.iloc[:, positions].copy()
    df.columns = ["Harvest Date", "Farm", "Crop", "Shipment", "Group", "Incentive"]
    # Exclude empty or non-numeric incentive values before building any filters or totals.
    df["Incentive"] = parse_numbers(df["Incentive"])
    df = df.loc[df["Incentive"].notna()].copy()
    df["Shipment"] = parse_numbers(df["Shipment"]).fillna(0)
    df["Harvest Date"] = parse_dates(df["Harvest Date"])
    for name in ("Farm", "Group", "Crop"):
        df[name] = df[name].astype("string").str.strip().fillna("").replace("", "(Blank)")
    return df


@st.cache_data(ttl=600)
def load_data():
    response = requests.get(CSV_URL, timeout=30)
    if response.status_code in (401, 403):
        try:
            credentials_info = dict(st.secrets["gcp_service_account"])
        except (KeyError, FileNotFoundError):
            raise PermissionError("CSV access was denied. Configure [gcp_service_account] in .streamlit/secrets.toml and share the sheet with its service account.") from None
        from google.auth.transport.requests import AuthorizedSession
        from google.oauth2 import service_account

        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        response = AuthorizedSession(credentials).get(CSV_URL, timeout=30)
    response.raise_for_status()
    return clean_data(pd.read_csv(BytesIO(response.content), dtype=str))
