import streamlit as st
import io

st.set_page_config(page_title="Config.py Generator", layout="wide")
st.title("🛠️ Config.py Generator")

st.markdown(
    """
    <div style='font-size:18px'>
    Use this tool to define expected variables, columns to check for existence,
    columns to display types, and simple unique() / nunique() reports.
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar: Configuration Inputs ---
st.sidebar.header("Configuration Settings")

if st.sidebar.button("🔁 Reset Form"):
    for k in list(st.session_state.keys()):
        if k.startswith(("name", "columns_", "showtypes_", "unique_enable_", "unique_cols_", "num_dfs")):
            del st.session_state[k]
    st.rerun()

num_dfs = st.sidebar.number_input(
    "🔢 Number of DataFrames to configure",
    min_value=1, max_value=10,
    value=1, step=1, key="num_dfs"
)

defaults = {
    "df1": {"columns": "year, region", "show_types": "region"},
    "df2": {"columns": "country_code, region", "show_types": "country_code"}
}

configs = []
for i in range(num_dfs):
    with st.sidebar.expander(f"📑 DataFrame {i+1}", expanded=True):
        name = st.text_input(f"Name of DataFrame {i+1}", value=f"df{i+1}", key=f"name{i}")
        default_columns = defaults.get(name, {}).get("columns", "")
        default_show_types = defaults.get(name, {}).get("show_types", "")

        columns = st.text_input(
            f"Expected columns in `{name}` (comma-separated)",
            value=default_columns, key=f"columns_{i}"
        )
        show_types = st.text_input(
            f"Columns to show types in `{name}` (comma-separated)",
            value=default_show_types, key=f"showtypes_{i}"
        )

        # NEW: per-DF unique checks (sidebar)
        st.checkbox("Add unique checks for this DataFrame", value=False, key=f"unique_enable_{i}")
        st.text_input("Columns for unique values (comma-separated)", value="", key=f"unique_cols_{i}")

        configs.append({
            "name": name,
            "columns": [c.strip() for c in columns.split(",") if c.strip()],
            "show_types": [c.strip() for c in show_types.split(",") if c.strip()]
        })

# Build UNIQUE_CHECKS from sidebar inputs
unique_checks = []
for i in range(num_dfs):
    if st.session_state.get(f"unique_enable_{i}", False):
        df_name = st.session_state.get(f"name{i}", f"df{i+1}")
        cols_raw = st.session_state.get(f"unique_cols_{i}", "")
        cols = [c.strip() for c in cols_raw.split(",") if c.strip()]
        for c in cols:
            unique_checks.append({"df_var": df_name, "column": c})

# --- Main panel: Display result and download ---
st.markdown("---")
st.subheader("📝 Preview")

expected_vars = [cfg["name"] for cfg in configs]
expected_columns = {cfg["name"]: cfg["columns"] for cfg in configs}
show_types = {cfg["name"]: cfg["show_types"] for cfg in configs}

config_code = f"""
# Auto-generated config.py

EXPECTED_VARIABLES = {repr(expected_vars)}

EXPECTED_COLUMNS = {repr(expected_columns)}

COLUMN_TYPE_CHECKS = {repr(show_types)}

UNIQUE_CHECKS = {repr(unique_checks)}
"""

st.code(config_code, language="python")

if st.button("✅ Generate config.py"):
    st.success("config.py generated successfully!")
    config_bytes = io.BytesIO(config_code.encode("utf-8"))
    st.download_button(
        label="📥 Download config.py",
        data=config_bytes,
        file_name="config.py",
        mime="text/x-python"
    )