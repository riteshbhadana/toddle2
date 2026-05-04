import streamlit as st
import pandas as pd
import sys, os

# src path add
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from enrichment_serp import find_linkedin
from detector import detect_change

st.set_page_config(page_title="School Change Detector", layout="wide")
st.title("🚀 School Change Detector (LinkedIn via SerpAPI)")

file = st.file_uploader("Upload Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.lower()

    # ---- NAME ----
    if "full name" in df.columns:
        df["name"] = df["full name"]
    elif "name" in df.columns:
        pass
    elif "first name" in df.columns and "last name" in df.columns:
        df["name"] = df["first name"].astype(str) + " " + df["last name"].astype(str)
    else:
        st.error("❌ Name column not found")
        st.stop()

    # ---- SCHOOL ----
    school_col = None
    for col in df.columns:
        if "school" in col or "company" in col or "organisation" in col:
            school_col = col
            break

    if not school_col:
        st.error("❌ School column not found")
        st.stop()

    df["school"] = df[school_col]

    results = []

    for _, row in df.iterrows():
        name = str(row["name"]).strip()
        school = str(row["school"]).split(";")[0].strip()

        profile = find_linkedin(name, school)
        new_school = profile["current_school"]  # अभी Unknown (enrichment बाद में)

        status = detect_change(school, new_school)

        results.append({
            "name": name,
            "input_school": school,
            "new_school": new_school,     # 🔥 नया column
            "status": status,
            "linkedin": profile["linkedin"]
        })

    out = pd.DataFrame(results)

    # ---- METRICS ----
    col1, col2 = st.columns(2)
    col1.metric("Total Records", len(out))
    col2.metric("Changed (detected)", len(out[out["status"] == "Changed"]))

    # ---- TABLE ----
    st.dataframe(out, use_container_width=True)

    # ---- DOWNLOAD ----
    st.download_button(
        "⬇️ Download CSV",
        out.to_csv(index=False),
        "results.csv"
    )

    st.markdown("---")
    st.info("ℹ️ Note: 'new_school' is 'Unknown' without enrichment. Integrate an enrichment API to fetch current organization from LinkedIn.")