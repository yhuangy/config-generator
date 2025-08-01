import streamlit as st
import io

st.set_page_config(page_title = "Config.py Generator",layout = "wide",)
st.title("🛠️ Config.py Generator")

st.markdown(
    """
    <div style='font-size:18px'>
    Use this tool to define expected variables, columns to check for existence,
    and columns to display tyepes.
    </div>
    """,
    unsafe_allow_html = True,
)

# --- Sidebar: Configuration Inputs ---
st.sidebar.header("Configuration Settings")

if st.sidebar.button("🔁 Reset Form"):
    st.experimental_rerun()

num_dfs = st.sidebar.number_input(
    "🔢 Number of DataFrames to configure",
    min_value = 1, max_value = 10,
    value = 1, step = 1,
    key = "num_dfs"
)

defaults = {
    "df1": {"columns": "year, region", 
            "show_types": "region"},
    "df2": {"columns": "country_code, region",
            "show_types": "country_code"}
}

configs = []

for i in range(num_dfs):
    with st.sidebar.expander(f"📑 DataFrame {i+1}", expanded = True):
        name = st.text_input(f"Name of DataFrame {i+1}", value = f"df{i+1}", key = f"name{i}")
        default_columns = defaults.get(name, {}).get("columns", "")
        default_show_types = defaults.get(name, {}).get("show_types", "")

        columns = st.text_input(
            f"Expected columns in `{name}` (comma-separated)",
            value = default_columns,
            key = f"columns_{i}"
        )
        show_types = st.text_input(
            f"Columns to show types in `{name}` (comma-separated)",
            value = default_show_types,
            key = f"showtypes_{i}"
        )
        configs.append({
            "name": name,
            "columns": [col.strip() for col in columns.split(",") if col.strip()],
            "show_types": [col.strip() for col in show_types.split(",") if col.strip()]
        })
        
# --- Main panel: Display result and download ---
st.markdown("---")
st.subheader("📝 Preview")

expected_vars = [cfg["name"] for cfg in configs]
expected_columns = {cfg["name"]: cfg["columns"] for cfg in configs}
show_types = {cfg["name"]: cfg["show_types"] for cfg in configs}

config_code = """
# Auto-generated config.py

EXPECTED_VARIABLES = {vars}

EXPECTED_COLUMNS = {columns}

COLUMN_TYPE_CHECKS = {types}
""".format(
    vars = repr(expected_vars),
    columns = repr(expected_columns),
    types = repr(show_types)
)

st.code(config_code, language = "python")

if st.button("✅ Generate config.py"):
    st.success("config.py generated successfully!")

    # Create a download button with the content
    config_bytes = io.BytesIO(config_code.encode("utf-8"))
    st.download_button(
        label = "📥 Download config.py",
        data = config_bytes,
        file_name = "config.py",
        mime = "text/x-python"
    )