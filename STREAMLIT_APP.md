# M&A Analyst Hub - Streamlit Application

## Overview

Interactive web application built with Streamlit to showcase M&A analytical skills and valuation techniques.

## Features

- **DCF Valuation Playground**: Interactive 5-year DCF model with adjustable assumptions
- **Comps & Multiples**: Upload CSV files or use sample data to analyze trading comparables
- **Deal Case Studies**: Showcase of real case studies (ExxonMobil, Mondragón, etc.)
- **About Me / Contact**: Professional profile and contact information

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```

The app will open automatically in your default browser at `http://localhost:8501`

## Usage

### DCF Valuation Playground
- Adjust revenue growth rates, margins, WACC, and terminal growth
- See real-time updates to enterprise value and equity value
- Visualize cash flow build-up and FCF profile

### Comps & Multiples
- Upload a CSV with columns: Company, EV (€m), Sales (€m), EBITDA (€m)
- Or use the built-in sample dataset
- View calculated multiples and statistical summary

### Deal Case Studies
- Browse through structured case study summaries
- Review investment theses and key value drivers

## Customization

To personalize the app:
- Update contact information in the "About Me / Contact" section
- Add your own case studies in the "Deal Case Studies" section
- Modify the sample comps data in the `sample_comps()` function

## Requirements

- Python 3.7+
- streamlit>=1.28.0
- pandas>=1.3.0
- numpy>=1.21.0

## Deployment

You can deploy this app to:
- **Streamlit Cloud** (free): https://streamlit.io/cloud
- **Heroku**
- **AWS/GCP/Azure**

For Streamlit Cloud deployment, simply connect your GitHub repo and point to `app.py`.
