import streamlit as st
import pandas as pd
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from enrichment_serp import find_linkedin
from detector import detect_change

st.set_page_config(page_title="School Change Detector", layout="wide")
st.title("🎓 School Change Detector — LinkedIn via SerpAPI")

# ── API key check ──────────────────────────────────────────────────────────────
if not os.getenv("SERPAPI_KEY"):
    st.error(
        "❌ SERPAPI_KEY not found. "
        "Add it in Streamlit Cloud → Settings → Secrets as:\n\n"
        "`SERPAPI_KEY = 'your_key_here'`"
    )
    st.stop()

# ── File upload ────────────────────────────────────────────────────────────────
file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])

if not file:
    st.info("👆 Upload an Excel file with columns: Name (or First/Last Name) + School/Company")
    st.stop()

df = pd.read_excel(file)
df.columns = df.columns.str.strip().str.lower()

# ── Resolve NAME column ────────────────────────────────────────────────────────
if "full name" in df.columns:
    df["name"] = df["full name"]
elif "name" in df.columns:
    df["name"] = df["name"]
elif "first name" in df.columns and "last name" in df.columns:
    df["name"] = df["first name"].astype(str).str.strip() + " " + df["last name"].astype(str).str.strip()
else:
    st.error("❌ Name column not found. Expected: 'Full Name', 'Name', or 'First Name' + 'Last Name'")
    st.stop()

# ── Resolve SCHOOL column ──────────────────────────────────────────────────────
school_col = next(
    (c for c in df.columns if any(k in c for k in ("school", "company", "organisation", "organization", "institution"))),
    None
)
if not school_col:
    st.error("❌ School/Company column not found. Expected a column containing 'school', 'company', or 'organisation'.")
    st.stop()

df["school"] = df[school_col]

st.success(f"✅ Loaded **{len(df)} records** — Name column: `{school_col}` | School column: `{school_col}`")

# ── Process ────────────────────────────────────────────────────────────────────
results = []
progress = st.progress(0, text="Starting…")

for i, (_, row) in enumerate(df.iterrows()):
    name   = str(row["name"]).strip()
    school = str(row["school"]).split(";")[0].strip()

    progress.progress((i + 1) / len(df), text=f"Processing {i+1}/{len(df)}: {name}")

    profile     = find_linkedin(name, school)
    new_school  = profile["current_school"]
    status      = detect_change(school, new_school)

    results.append({
        "Name":          name,
        "Input School":  school,
        "Current School (LinkedIn)": new_school,
        "Status":        status,
        "LinkedIn URL":  profile["linkedin"],
    })

progress.empty()
out = pd.DataFrame(results)

# ── Metrics ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total",     len(out))
c2.metric("✅ Same",    len(out[out["Status"] == "Same"]))
c3.metric("🔄 Changed", len(out[out["Status"] == "Changed"]))
c4.metric("❓ Not Found", len(out[out["Status"] == "Not Found"]))

# ── Colour-coded table ─────────────────────────────────────────────────────────
def colour_status(val):
    return {
        "Changed":   "background-color: #ffd6d6; color: #900",
        "Same":      "background-color: #d6f5d6; color: #060",
        "Not Found": "background-color: #f0f0f0; color: #555",
    }.get(val, "")

st.dataframe(
    out.style.map(colour_status, subset=["Status"]),
    use_container_width=True,
)

# ── Download ───────────────────────────────────────────────────────────────────
st.download_button(
    "⬇️ Download CSV",
    out.to_csv(index=False),
    "school_change_results.csv",
    mime="text/csv",
)
