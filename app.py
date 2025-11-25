import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import matplotlib.pyplot as plt
import seaborn as sns
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

            # Optional: Preview with Google Docs Viewer
            with st.expander(f"👁️ Preview: {file_path.name}"):
                st.info("💡 Preview opens in Google Docs Viewer (may require public link). Download the file to view it locally.")
                # For local files, we can't use Google Docs Viewer directly
                # Show file info instead
                st.markdown(f"**File**: `{file_path.name}`")
                st.markdown(f"**Size**: {file_path.stat().st_size / 1024:.1f} KB")
                st.markdown("Click **Download** to view the presentation locally.")

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

            # Optional: Preview PDF with embedded viewer
            with st.expander(f"👁️ Preview: {file_path.name}"):
                try:
                    with open(file_path, "rb") as f:
                        pdf_bytes = f.read()
                        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

                    # Embed PDF using iframe
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Cannot preview this PDF: {str(e)}")
                    st.markdown("Click **Download** to view the PDF locally.")


def analyze_excel_and_plot(case_folder):
    """Automatically analyze Excel files and generate relevant charts."""
    case_path = Path("case_studies") / case_folder
    excel_files = []

    # Get all Excel files
    for ext in ["*.xlsx", "*.xls"]:
        excel_files.extend(list(case_path.glob(ext)))

    if not excel_files:
        return

    st.markdown("---")
    st.markdown("### 📊 Automated Data Analysis")

    for excel_file in excel_files[:2]:  # Limit to first 2 files to avoid clutter
        try:
            # Read all sheets
            xls = pd.ExcelFile(excel_file)

            # Try to find sheets with numerical data
            for sheet_name in xls.sheet_names[:3]:  # Analyze first 3 sheets
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)

                    # Skip if too small
                    if len(df) < 3 or len(df.columns) < 2:
                        continue

                    # Find numerical columns
                    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

                    if len(numeric_cols) >= 2:
                        st.markdown(f"**{excel_file.name}** - {sheet_name}")

                        # Create figure with subplots
                        fig, axes = plt.subplots(1, min(2, len(numeric_cols)), figsize=(12, 4))
                        if len(numeric_cols) == 1:
                            axes = [axes]

                        # Plot first few numeric columns
                        for idx, col in enumerate(numeric_cols[:2]):
                            if len(numeric_cols) > 1:
                                ax = axes[idx]
                            else:
                                ax = axes[0]

                            # Line chart if looks like time series, bar chart otherwise
                            if len(df) < 20:
                                df[col].plot(kind='bar', ax=ax, color='#003366')
                                ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
                            else:
                                df[col].plot(kind='line', ax=ax, color='#003366', linewidth=2)

                            ax.set_title(col, fontsize=10, fontweight='bold')
                            ax.grid(True, alpha=0.3)
                            ax.set_xlabel('')

                        plt.tight_layout()
                        st.pyplot(fig)
                        plt.close()

                        # Show summary stats
                        with st.expander("📈 Summary Statistics"):
                            st.dataframe(df[numeric_cols].describe().T.style.format("{:.2f}"))

                        break  # Only show one sheet per file

                except Exception as e:
                    continue

        except Exception as e:
            continue


# ---------- SIDEBAR / NAVEGACIÓN ----------
with st.sidebar:
    st.title("M&A ANALYST HUB")
    st.caption("Technical Valuation Platform")
    page = st.radio(
        "NAVIGATE",
        ["Home",
         "DCF Model",
         "Trading Comps",
         "Case Studies",
         "Contact"]
    )
    st.markdown("---")
    st.caption("Built with Python + Streamlit | Aitor Bernal")


# ---------- PÁGINAS ----------

# --- HOME ---
if page == "Home":
    st.title("M&A ANALYST HUB")
    st.subheader("Technical Valuation Platform for Investment Banking")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Platform Overview")
        st.markdown(
            """
            Interactive financial modeling platform demonstrating core M&A valuation capabilities:

            **Valuation Methodologies**
            - DCF (Discounted Cash Flow) with sensitivity analysis
            - Trading comparables and multiples analysis
            - Precedent transactions framework

            **Technical Skills**
            - Python-based financial modeling
            - Data-driven investment thesis development
            - Reproducible valuation frameworks
            """
        )

        st.markdown("##")
        st.header("Core Competencies")
        st.markdown(
            """
            **Financial Modeling**
            Build and stress-test DCF models with flexible assumptions.

            **Comparable Company Analysis**
            Analyze trading multiples and generate valuation ranges.

            **Transaction Execution**
            Structure and present M&A case studies with clear investment theses.
            """
        )

    with col2:
        st.header("Profile")
        st.markdown("**Target Position**")
        st.write("M&A Analyst – Madrid")

        st.markdown("**Background**")
        st.write("MSc Corporate Finance & Investment Banking")
        st.write("Data Analytics")

        st.markdown("**Focus Areas**")
        st.write("• Financial modeling")
        st.write("• Valuation")
        st.write("• Python automation")


# --- DCF VALUATION MODEL ---
elif page == "DCF Model":
    st.title("DCF VALUATION MODEL")
    st.subheader("Unlevered Free Cash Flow Analysis")

    st.markdown("---")

    st.markdown(
        """
        **Model Specifications**
        - 5-year explicit forecast period
        - Unlevered free cash flow to firm (FCFF)
        - Terminal value using perpetuity growth method
        - Bridge to equity value via net debt adjustment

        **Key Assumptions**
        Adjust revenue growth, margins, capex, working capital, WACC, and terminal growth rate.
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

    st.markdown("---")
    st.caption("**Note**: Sensitivity analysis demonstrates valuation impact of assumption changes across WACC, terminal growth, margins, and working capital requirements.")


# --- TRADING COMPS ---
elif page == "Trading Comps":
    st.title("TRADING COMPARABLES ANALYSIS")
    st.subheader("Relative Valuation Methodology")

    st.markdown("---")

    st.markdown(
        """
        **Approach**
        - Upload comparable company data (CSV format)
        - Calculate EV/Sales and EV/EBITDA multiples
        - Generate valuation statistics (min, median, mean, max)

        **Use Case**
        Apply trading multiples to target company financials for relative valuation range.
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

        st.markdown("#### Multiple Distribution: EV/EBITDA")
        st.bar_chart(df.set_index("Company")["EV/EBITDA"])

        st.markdown("---")
        st.caption("**Valuation Range**: Select 25th percentile (bear case), median (base case), and 75th percentile (bull case) for target multiple application.")
    else:
        st.warning(f"Required columns for analysis: {required_cols}")


# --- CASE STUDIES ---
elif page == "Case Studies":
    st.title("TRANSACTION CASE STUDIES")
    st.subheader("M&A Analysis & Equity Stories")

    st.markdown("---")

    st.markdown(
        """
        **Format**
        - Investment thesis and strategic rationale
        - Key value drivers and risks
        - Valuation methodology and assumptions

        Structured for interview discussion and technical deep-dives.
        """
    )

    tab1, tab2, tab3, tab4 = st.tabs(["Energy & Commodities", "Private Education", "Nuclear Policy", "Other Transactions"])

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

        # Automated analysis and charts
        analyze_excel_and_plot("exxon")

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

        # Automated analysis and charts
        analyze_excel_and_plot("mondragon")

    with tab3:
        st.subheader("Nuclear Energy Policy Impact Analysis")
        st.markdown(
            """
            **Strategic Context**
            - Comparative policy analysis: Spanish nuclear phase-out vs French nuclear expansion strategy
            - Quantitative assessment of industrial electricity cost implications
            - Impact on Spanish metal sector international competitiveness

            **Sectoral Analysis**
            - Steel and aluminum production cost structure breakdown
            - Competitive positioning vs European peers (France, Germany)
            - Energy-intensive industry margin pressure analysis
            - Long-term investment flow implications for Spanish industrial base

            **Analytical Framework**
            - Energy cost modeling under divergent policy scenarios
            - Metal producer margin sensitivity to electricity price differentials
            - Industrial policy implications and strategic recommendations
            - Cross-border competitiveness gap quantification

            **Key Insights**
            - Nuclear phase-out creates structural cost disadvantage for energy-intensive sectors
            - French policy provides sustained competitive advantage in industrial production
            - Policy divergence drives potential industrial relocation pressures
            - Strategic implications for Spain's industrial manufacturing base
            """
        )

        st.markdown("---")
        display_case_files("nuclear_spain", "Nuclear Spain Analysis")

        # Automated analysis and charts
        analyze_excel_and_plot("nuclear_spain")

    with tab4:
        st.subheader("Additional Transaction Experience")
        st.markdown(
            """
            **Gaming & Leisure Sector**
            - IPO-style equity story and valuation analysis
            - Revenue model built on gaming operations and geographic expansion
            - Comparable company analysis across European gaming operators

            **Industrial Sector**
            - Internal analytics tools for operational efficiency
            - Working capital optimization frameworks
            - Capacity planning and backlog analysis

            **Technical Infrastructure**
            - Modular DCF valuation toolkit in Python
            - WACC calculation and cost of capital frameworks
            - Monte Carlo simulation for scenario analysis

            **Interview Discussion Points**
            - Model assumptions and sensitivities
            - Sector-specific value drivers
            - Communication of technical concepts to non-technical stakeholders
            """
        )

        # Display case files for Cirsa
        st.markdown("---")
        st.markdown("#### Cirsa - Gaming & Leisure Sector")
        display_case_files("cirsa", "Cirsa")

        # Automated analysis and charts
        analyze_excel_and_plot("cirsa")


# --- CONTACT ---
elif page == "Contact":
    st.title("CONTACT & PROFILE")
    st.subheader("Aitor Bernal")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Professional Background")
        st.markdown(
            """
            **Education**
            - MSc in Corporate Finance & Investment Banking
            - Business & Data Analytics

            **Technical Skills**
            - Financial modeling: DCF, LBO, trading comps, precedent transactions
            - Programming: Python (pandas, NumPy), SQL
            - Tools: Excel, Power BI, Streamlit

            **Focus Areas**
            - Valuation and financial analysis
            - Data-driven investment thesis development
            - Reproducible modeling frameworks
            """
        )

        st.markdown("##")
        st.header("Platform Capabilities")
        st.markdown(
            """
            **This Platform Demonstrates**
            - Translation of valuation theory into working code
            - Understanding of key value drivers and assumptions
            - Clear communication of complex financial concepts
            - Professional presentation standards
            """
        )

    with col2:
        st.header("Contact Information")
        st.markdown("**Email**")
        st.write("[bernalsoro@hotmail.es](mailto:bernalsoro@hotmail.es)")

        st.markdown("**LinkedIn**")
        st.write("[Aitor Bernal](https://www.linkedin.com/in/aitor-bernal-financial-modeling/)")

        st.markdown("**GitHub**")
        st.write("[github.com/Bernalsoro](https://github.com/Bernalsoro)")

        st.markdown("**Phone**")
        st.write("+34 606 986 980")

        st.markdown("##")
        st.markdown("**Target Position**")
        st.write("M&A Analyst")
        st.write("Madrid, Spain")

    # Footer
    st.markdown("---")
    st.caption("© 2025 Aitor Bernal | Built with Python + Streamlit | Full source code available on GitHub")
