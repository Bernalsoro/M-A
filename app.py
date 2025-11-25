import streamlit as st
import pandas as pd
import numpy as np
import os
from pathlib import Path

# ---------- CONFIGURACIÓN DE LA PÁGINA ----------
st.set_page_config(
    page_title="M&A Analyst Hub",
    page_icon="💼",
    layout="wide"
)

# ---------- FUNCIONES AUXILIARES ----------

def build_dcf(
    revenue_0,
    growth_rates,
    ebit_margin,
    tax_rate,
    capex_pct,
    nwc_pct,
    wacc,
    g
):
    years = list(range(1, 6))
    revenues = []
    ebits = []
    taxes = []
    nopat = []
    capex = []
    delta_nwc = []
    fcf = []

    rev_prev = revenue_0
    nwc_prev = revenue_0 * nwc_pct

    for i, year in enumerate(years):
        rev = rev_prev * (1 + growth_rates[i])
        ebit = rev * ebit_margin
        tax = -ebit * tax_rate
        nop = ebit + tax
        cap = -rev * capex_pct  # salida de caja
        nwc_curr = rev * nwc_pct
        d_nwc = -(nwc_curr - nwc_prev)  # si sube NWC, resta FCF

        f = nop + cap + d_nwc

        revenues.append(rev)
        ebits.append(ebit)
        taxes.append(tax)
        nopat.append(nop)
        capex.append(cap)
        delta_nwc.append(d_nwc)
        fcf.append(f)

        rev_prev = rev
        nwc_prev = nwc_curr

    df = pd.DataFrame({
        "Year": years,
        "Revenue": revenues,
        "EBIT": ebits,
        "Taxes": taxes,
        "NOPAT": nopat,
        "Capex": capex,
        "ΔNWC": delta_nwc,
        "FCF": fcf
    })

    # Descuento de FCF
    discount_factors = [(1 / ((1 + wacc) ** t)) for t in years]
    df["Discount Factor"] = discount_factors
    df["FCF PV"] = df["FCF"] * df["Discount Factor"]

    # Terminal value usando crecimiento perpetuo
    fcf_5 = df.loc[df["Year"] == 5, "FCF"].values[0]
    terminal_value = fcf_5 * (1 + g) / (wacc - g)
    terminal_pv = terminal_value * discount_factors[-1]

    enterprise_value = df["FCF PV"].sum() + terminal_pv

    return df, enterprise_value, terminal_value, terminal_pv


def sample_comps():
    data = {
        "Company": ["Comp A", "Comp B", "Comp C", "Comp D", "Comp E"],
        "Sector": ["Education", "Education", "Education", "EdTech", "Education"],
        "EV (€m)": [800, 1200, 950, 600, 1500],
        "Sales (€m)": [200, 260, 210, 150, 320],
        "EBITDA (€m)": [40, 62, 50, 30, 72]
    }
    df = pd.DataFrame(data)
    df["EV/Sales"] = df["EV (€m)"] / df["Sales (€m)"]
    df["EV/EBITDA"] = df["EV (€m)"] / df["EBITDA (€m)"]
    return df


def get_case_files(case_folder):
    """Get all Excel, PDF, and PowerPoint files from a case study folder."""
    case_path = Path("case_studies") / case_folder
    files = {"excel": [], "pdf": [], "powerpoint": []}

    if case_path.exists():
        # Get Excel files
        for ext in ["*.xlsx", "*.xls"]:
            files["excel"].extend(list(case_path.glob(ext)))
        # Get PDF files
        files["pdf"].extend(list(case_path.glob("*.pdf")))
        # Get PowerPoint files
        for ext in ["*.pptx", "*.ppt"]:
            files["powerpoint"].extend(list(case_path.glob(ext)))

    return files


def display_case_files(case_folder, case_name):
    """Display and provide download buttons for case study files."""
    files = get_case_files(case_folder)

    if not files["excel"] and not files["pdf"] and not files["powerpoint"]:
        st.info(f"📂 No files uploaded yet for {case_name}. Add Excel/PDF/PowerPoint files to `case_studies/{case_folder}/`")
        return

    st.markdown("---")
    st.markdown("### 📎 Case Materials")

    # Display Excel files
    if files["excel"]:
        st.markdown("**📊 Excel Models**")
        for file_path in files["excel"]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"- `{file_path.name}`")
            with col2:
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download",
                        data=f.read(),
                        file_name=file_path.name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_{file_path.name}"
                    )

            # Optional: Preview first sheet
            with st.expander(f"👁️ Preview: {file_path.name}"):
                try:
                    df_preview = pd.read_excel(file_path, nrows=20)
                    st.dataframe(df_preview, use_container_width=True)
                except Exception as e:
                    st.warning(f"Cannot preview this file: {str(e)}")

    # Display PowerPoint files
    if files["powerpoint"]:
        st.markdown("**📊 PowerPoint Presentations**")
        for file_path in files["powerpoint"]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"- `{file_path.name}`")
            with col2:
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download",
                        data=f.read(),
                        file_name=file_path.name,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        key=f"download_{file_path.name}"
                    )

    # Display PDF files
    if files["pdf"]:
        st.markdown("**📄 PDF Documents**")
        for file_path in files["pdf"]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"- `{file_path.name}`")
            with col2:
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download",
                        data=f.read(),
                        file_name=file_path.name,
                        mime="application/pdf",
                        key=f"download_{file_path.name}"
                    )


# ---------- SIDEBAR / NAVEGACIÓN ----------
with st.sidebar:
    st.title("💼 M&A Analyst Hub")
    st.write("Built with Python & Streamlit")
    page = st.radio(
        "Navigate",
        ["🏠 Home",
         "📊 DCF Valuation Playground",
         "📈 Comps & Multiples",
         "📁 Deal Case Studies",
         "👤 About Me / Contact"]
    )
    st.markdown("---")
    st.caption("Designed to showcase technical & analytical skills in M&A.")


# ---------- PÁGINAS ----------

# --- HOME ---
if page == "🏠 Home":
    col1, col2 = st.columns([2, 1])

    with col1:
        st.title("M&A Analyst Hub")
        st.subheader("Technical toolkit for Investment Banking / M&A interviews")

        st.markdown(
            """
            This mini web app is built in **Python + Streamlit** to showcase:

            - 📊 **Valuation modelling** (DCF with flexible assumptions)
            - 📈 **Trading comps & multiples analysis**
            - 📁 **Deal & case study summaries** with clear investment theses
            - 🧠 A **data-driven mindset** applied to Corporate Finance & M&A

            Use the navigation on the left to explore each section.
            """
        )

        st.markdown("### Why this exists")
        st.markdown(
            """
            In M&A you need to:
            - Understand **business models** and value drivers
            - Translate them into **financial models**
            - Communicate insights in a **clear, investor-friendly** way

            This app is my way of showing that I can do **all three**, using
            real tools that I also use for analysis: Python, pandas, and Streamlit.
            """
        )

    with col2:
        st.markdown("### Quick Profile")
        st.metric("Target role", "M&A Analyst – Madrid")
        st.metric("Background", "Data Analytics + Corporate Finance")
        st.metric("Focus", "Modelling, valuation & storytelling")


# --- DCF VALUATION PLAYGROUND ---
elif page == "📊 DCF Valuation Playground":
    st.title("📊 DCF Valuation Playground")

    st.markdown(
        """
        Simple 5-year **unlevered DCF** to play with key assumptions:
        - Revenue growth
        - Margins
        - Capex & Working Capital
        - WACC and terminal growth

        This is not meant to be a full banking model, but a **clean,
        interview-friendly sandbox** to discuss valuation logic.
        """
    )

    # Inputs en columnas
    col1, col2, col3 = st.columns(3)

    with col1:
        revenue_0 = st.number_input(
            "Revenue Year 0 (€m)",
            min_value=0.0,
            value=100.0,
            step=5.0
        )
        ebit_margin = st.slider(
            "EBIT margin (%)",
            min_value=0.0,
            max_value=50.0,
            value=20.0,
            step=1.0
        ) / 100
        tax_rate = st.slider(
            "Tax rate (%)",
            min_value=0.0,
            max_value=40.0,
            value=25.0,
            step=1.0
        ) / 100

    with col2:
        capex_pct = st.slider(
            "Capex (% of Sales)",
            min_value=0.0,
            max_value=30.0,
            value=8.0,
            step=1.0
        ) / 100
        nwc_pct = st.slider(
            "Working capital (% of Sales)",
            min_value=0.0,
            max_value=40.0,
            value=10.0,
            step=1.0
        ) / 100

        wacc = st.slider(
            "WACC (%)",
            min_value=4.0,
            max_value=15.0,
            value=9.0,
            step=0.5
        ) / 100

    with col3:
        g = st.slider(
            "Terminal growth g (%)",
            min_value=0.0,
            max_value=5.0,
            value=2.0,
            step=0.25
        ) / 100
        net_debt = st.number_input(
            "Net Debt (€m)",
            value=0.0,
            step=5.0
        )
        shares_out = st.number_input(
            "Shares outstanding (m)",
            value=50.0,
            step=1.0
        )

    st.markdown("---")

    # Growth por años
    st.subheader("Revenue growth assumptions")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        g1 = st.number_input("Year 1 (%)", value=8.0, step=0.5) / 100
    with c2:
        g2 = st.number_input("Year 2 (%)", value=7.0, step=0.5) / 100
    with c3:
        g3 = st.number_input("Year 3 (%)", value=6.0, step=0.5) / 100
    with c4:
        g4 = st.number_input("Year 4 (%)", value=5.0, step=0.5) / 100
    with c5:
        g5 = st.number_input("Year 5 (%)", value=4.0, step=0.5) / 100

    growth_rates = [g1, g2, g3, g4, g5]

    # Cálculo DCF
    df_dcf, ev, tv, tv_pv = build_dcf(
        revenue_0,
        growth_rates,
        ebit_margin,
        tax_rate,
        capex_pct,
        nwc_pct,
        wacc,
        g
    )

    equity_value = ev - net_debt
    price_per_share = equity_value / shares_out if shares_out > 0 else np.nan
    tv_weight = tv_pv / ev if ev != 0 else np.nan

    # KPIs
    st.markdown("### Valuation summary")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Enterprise Value (EV, €m)", f"{ev:,.1f}")
    with kpi2:
        st.metric("Equity Value (EqV, €m)", f"{equity_value:,.1f}")
    with kpi3:
        st.metric("Implied Price per Share (€)", f"{price_per_share:,.2f}")
    with kpi4:
        st.metric("TV as % of EV", f"{tv_weight*100:,.1f}%")

    st.markdown("### Cash flow build-up")
    st.dataframe(df_dcf.style.format({
        "Revenue": "{:,.1f}",
        "EBIT": "{:,.1f}",
        "Taxes": "{:,.1f}",
        "NOPAT": "{:,.1f}",
        "Capex": "{:,.1f}",
        "ΔNWC": "{:,.1f}",
        "FCF": "{:,.1f}",
        "Discount Factor": "{:,.3f}",
        "FCF PV": "{:,.1f}"
    }))

    st.markdown("### FCF profile")
    st.line_chart(df_dcf.set_index("Year")[["FCF", "FCF PV"]])

    st.caption(
        "Use this page in interviews to discuss **sensitivity** of valuation "
        "to WACC, g, margins and capex/NWC assumptions."
    )


# --- COMPS & MULTIPLES ---
elif page == "📈 Comps & Multiples":
    st.title("📈 Trading Comps & Multiples")

    st.markdown(
        """
        Upload a simple **comps table** (CSV) or use the sample dataset.
        The app will calculate key valuation multiples and stats.
        """
    )

    uploaded = st.file_uploader("Upload comps CSV", type=["csv"])

    if uploaded is not None:
        df = pd.read_csv(uploaded)
    else:
        st.info("No file uploaded, using sample comps.")
        df = sample_comps()

    st.markdown("#### Raw comps")
    st.dataframe(df)

    required_cols = {"EV (€m)", "Sales (€m)", "EBITDA (€m)"}
    if required_cols.issubset(df.columns):
        if "EV/Sales" not in df.columns:
            df["EV/Sales"] = df["EV (€m)"] / df["Sales (€m)"]
        if "EV/EBITDA" not in df.columns:
            df["EV/EBITDA"] = df["EV (€m)"] / df["EBITDA (€m)"]

        st.markdown("#### Multiples summary")
        stats = df[["EV/Sales", "EV/EBITDA"]].agg(["min", "median", "mean", "max"]).T
        st.dataframe(stats.style.format("{:,.2f}"))

        st.markdown("#### Distribution of EV/EBITDA")
        st.bar_chart(df.set_index("Company")["EV/EBITDA"])

        st.caption(
            "You can use this section to explain how you select "
            "a **reasonable range of trading multiples** for valuation "
            "(e.g. low / median / high scenarios)."
        )
    else:
        st.warning(
            f"To compute multiples automatically, your CSV must contain: {required_cols}"
        )


# --- DEAL CASE STUDIES ---
elif page == "📁 Deal Case Studies":
    st.title("📁 Deal & Case Studies")

    st.markdown(
        """
        Short, **bank-style case summaries** you can walk through in interviews.
        Keep it concise: thesis, key drivers, and valuation angle.
        """
    )

    tab1, tab2, tab3 = st.tabs(["Energy DCF", "Education / Sell-side", "Other Ideas"])

    with tab1:
        st.subheader("ExxonMobil – Fundamental DCF & Scenario Analysis")
        st.markdown(
            """
            **Context**
            - Built a full **bottom-up DCF** on ExxonMobil using Python & Excel
            - Integrated assumptions on oil & gas prices, production volumes and margins

            **What I did**
            - Collected historical financials and segment data
            - Modelled revenue by segment and margin normalization
            - Built a DCF with WACC, g and commodity price **sensitivity tables**
            - Compared intrinsic value vs market price and analyst targets

            **Key takeaways**
            - Highlighted which assumptions actually move the needle on EV
            - Showed how **macro (oil prices)** translates mechanically into cash flows
            - Used the model to communicate a clear **upside / downside** range
            """
        )

        # Display case files
        display_case_files("exxon", "ExxonMobil")

    with tab2:
        st.subheader("Mondragón University – Private Education Sell-Side Case")
        st.markdown(
            """
            **Context**
            - Academic case: **majority stake sale** in a private university in Spain
            - Objective: build a concise **equity story + valuation** for potential investors

            **What I did**
            - Analysed business model (on-campus, online, B2B corporate programs)
            - Built a 5-year **growth plan** focused on online & international students
            - Prepared a DCF and trading comps vs other education / EdTech players
            - Summarised the case in a **4-slide teaser-style deck**

            **Key messages to investors**
            - Resilient cash generation & asset-light model
            - Upside from online / international expansion
            - Attractive entry valuation vs sector multiples

            This case is perfect to discuss how I would structure a **sell-side process**
            and which KPIs really matter for **private education assets**.
            """
        )

        # Display case files
        display_case_files("mondragon", "Mondragón University")

    with tab3:
        st.subheader("Other projects & pipelines")
        st.markdown(
            """
            - 🎰 **Gaming / Leisure** – IPO-style equity story & valuation (Cirsa case)
            - 🏗 **Industrial** – internal analytics tools to improve backlog & capacity,
              directly linked to **working capital and margins**
            - 🧮 **Python valuation toolkit** – modular DCF class, WACC calculators,
              Monte Carlo simulations for valuation scenarios

            Each of these can be deep-dived in an interview, focusing either on:
            - Modelling & assumptions
            - Sector specifics
            - Or communication to non-technical stakeholders
            """
        )

        # Display case files for Cirsa
        st.markdown("---")
        st.markdown("#### 🎰 Cirsa - Gaming & Leisure Case")
        display_case_files("cirsa", "Cirsa")


# --- ABOUT / CONTACT ---
elif page == "👤 About Me / Contact":
    st.title("👤 About Me")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
            ### Profile

            - **Target role**: M&A Analyst (Madrid)
            - **Background**: Business & Data Analytics + MSc in Corporate Finance & Investment Banking
            - **Tools**: Python (pandas, NumPy), SQL, Excel, Power BI, basic modelling in Streamlit

            I am especially interested in:
            - Valuation (DCF, comps, LBO logic)
            - Cross-over between **data** and **corporate finance**
            - Using code to make analysis **reproducible and transparent**
            """
        )

        st.markdown("### What this app says about me")
        st.markdown(
            """
            - I can translate theory (DCF, multiples) into **working code**
            - I understand which **assumptions and KPIs** matter in valuation
            - I care about **clarity**: clean layouts, simple charts, concise wording
            """
        )

    with col2:
        st.markdown("### Contact")
        st.markdown(
            """
            - 📧 Email: *add your email here*
            - 🔗 LinkedIn: *add your LinkedIn URL*
            - 🐍 GitHub: *link to your valuation / modelling repos*
            """
        )

        st.markdown("---")
        st.caption(
            "Happy to walk you through any part of the code or models "
            "during the interview."
        )
