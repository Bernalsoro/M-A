"""
Script para generar PDFs de ejemplo para el DealRoom DD Agent.
Simula un data room real de una empresa ficticia: TechFlow Solutions SL

Uso:
    pip install reportlab
    python generate_sample_dataroom.py

Los PDFs se guardarán en: sample_dataroom/
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY
from pathlib import Path
import datetime


def create_dataroom_folder():
    """Crea la carpeta para el data room de ejemplo."""
    folder = Path("sample_dataroom")
    folder.mkdir(exist_ok=True)
    return folder


def generate_executive_summary(output_path):
    """Genera el Executive Summary del target."""
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    story.append(Paragraph("EXECUTIVE SUMMARY", title_style))
    story.append(Spacer(1, 0.3*inch))

    # Company info
    story.append(Paragraph("<b>Target:</b> TechFlow Solutions SL", styles['Heading2']))
    story.append(Paragraph("<b>Sector:</b> Software / SaaS", styles['Normal']))
    story.append(Paragraph("<b>Date:</b> " + datetime.date.today().strftime("%B %Y"), styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Business overview
    story.append(Paragraph("1. BUSINESS OVERVIEW", styles['Heading2']))
    text = """
    TechFlow Solutions SL es una empresa española de software B2B fundada en 2018, especializada en
    soluciones de automatización de procesos empresariales (BPA) y gestión de workflows para PYMES.
    La compañía ofrece una plataforma SaaS propietaria que permite a sus clientes digitalizar y
    optimizar procesos operativos sin necesidad de código (no-code).

    El modelo de negocio se basa en suscripciones recurrentes (ARR) con tres tiers: Basic (€99/mes),
    Professional (€299/mes) y Enterprise (precio personalizado). La empresa cuenta actualmente con
    850 clientes activos, principalmente en sectores de servicios profesionales, logística y retail.
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Market position
    story.append(Paragraph("2. COMPETITIVE POSITION", styles['Heading2']))
    text = """
    TechFlow compite en un mercado fragmentado con jugadores internacionales (Zapier, Monday.com) y
    locales. Su ventaja competitiva radica en:

    - Especialización en el mercado español con soporte local completo
    - Integración nativa con sistemas ERP españoles (Sage, A3)
    - Pricing 30-40% inferior a competidores internacionales
    - Tiempo de implementación reducido (2-4 semanas vs 3-6 meses)

    Sin embargo, enfrenta presión competitiva creciente de players internacionales que están
    localizando sus ofertas y expandiendo equipos comerciales en la península.
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Financial highlights
    story.append(Paragraph("3. FINANCIAL HIGHLIGHTS (2024)", styles['Heading2']))

    financial_data = [
        ['Metric', 'Value'],
        ['ARR (Annual Recurring Revenue)', '€2.8M'],
        ['Revenue Growth YoY', '+42%'],
        ['Gross Margin', '78%'],
        ['EBITDA Margin', '12%'],
        ['Cash Burn (monthly)', '-€35K'],
        ['Cash Position', '€420K'],
        ['CAC Payback Period', '18 months'],
        ['Net Revenue Retention', '108%']
    ]

    table = Table(financial_data, colWidths=[3.5*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))

    story.append(table)
    story.append(Spacer(1, 0.2*inch))

    # Growth strategy
    story.append(Paragraph("4. GROWTH STRATEGY", styles['Heading2']))
    text = """
    El management planea acelerar crecimiento mediante:

    1. Expansión geográfica a Portugal e Italia (Q2 2025)
    2. Lanzamiento de módulo de IA para automatización predictiva (en desarrollo)
    3. Programa de partners/resellers para escalar canales de distribución
    4. Upselling a clientes existentes (actualmente 65% están en tier Basic)

    La inversión requerida estimada es de €1.2M en 18 meses, principalmente en equipo comercial
    (4 sales reps) y desarrollo de producto (2 engineers + 1 product manager).
    """
    story.append(Paragraph(text, styles['BodyText']))

    # Build PDF
    doc.build(story)
    print(f"✅ Generated: {output_path.name}")


def generate_financial_statements(output_path):
    """Genera estados financieros del target."""
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    story.append(Paragraph("FINANCIAL STATEMENTS", title_style))
    story.append(Paragraph("TechFlow Solutions SL", styles['Heading2']))
    story.append(Paragraph("Fiscal Years 2022-2024", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # P&L
    story.append(Paragraph("PROFIT & LOSS STATEMENT (€000s)", styles['Heading2']))

    pl_data = [
        ['', '2022', '2023', '2024'],
        ['Revenue', '1,250', '1,980', '2,810'],
        ['  - Subscription Revenue', '1,150', '1,850', '2,650'],
        ['  - Professional Services', '100', '130', '160'],
        ['', '', '', ''],
        ['Cost of Sales', '-280', '-410', '-620'],
        ['  - Hosting & Infrastructure', '-180', '-260', '-380'],
        ['  - Support Staff', '-100', '-150', '-240'],
        ['', '', '', ''],
        ['Gross Profit', '970', '1,570', '2,190'],
        ['Gross Margin %', '77.6%', '79.3%', '77.9%'],
        ['', '', '', ''],
        ['Operating Expenses', '-890', '-1,340', '-1,850'],
        ['  - Sales & Marketing', '-350', '-580', '-820'],
        ['  - R&D', '-320', '-480', '-650'],
        ['  - G&A', '-220', '-280', '-380'],
        ['', '', '', ''],
        ['EBITDA', '80', '230', '340'],
        ['EBITDA Margin %', '6.4%', '11.6%', '12.1%'],
        ['', '', '', ''],
        ['Depreciation & Amortization', '-45', '-65', '-85'],
        ['', '', '', ''],
        ['EBIT', '35', '165', '255'],
        ['', '', '', ''],
        ['Interest & Financial', '-15', '-20', '-12'],
        ['Tax', '-8', '-42', '-73'],
        ['', '', '', ''],
        ['Net Income', '12', '103', '170']
    ]

    table = Table(pl_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEABOVE', (0, 4), (-1, 4), 1, colors.grey),
        ('LINEABOVE', (0, 8), (-1, 8), 1, colors.grey),
        ('LINEABOVE', (0, 12), (-1, 12), 1, colors.grey),
        ('LINEABOVE', (0, 16), (-1, 16), 1, colors.grey),
        ('LINEABOVE', (0, 20), (-1, 20), 2, colors.black),
        ('FONTNAME', (0, 9), (-1, 9), 'Helvetica-Bold'),
        ('FONTNAME', (0, 16), (-1, 16), 'Helvetica-Bold'),
        ('FONTNAME', (0, 26), (-1, 26), 'Helvetica-Bold'),
    ]))

    story.append(table)
    story.append(PageBreak())

    # Balance Sheet
    story.append(Paragraph("BALANCE SHEET (€000s)", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    bs_data = [
        ['ASSETS', '2023', '2024'],
        ['Current Assets', '', ''],
        ['  Cash & Cash Equivalents', '380', '420'],
        ['  Accounts Receivable', '165', '280'],
        ['  Prepaid Expenses', '45', '60'],
        ['Total Current Assets', '590', '760'],
        ['', '', ''],
        ['Non-Current Assets', '', ''],
        ['  Property & Equipment', '85', '110'],
        ['  Intangible Assets (Software)', '240', '320'],
        ['  Other Assets', '35', '45'],
        ['Total Non-Current Assets', '360', '475'],
        ['', '', ''],
        ['TOTAL ASSETS', '950', '1,235'],
        ['', '', ''],
        ['LIABILITIES & EQUITY', '2023', '2024'],
        ['Current Liabilities', '', ''],
        ['  Accounts Payable', '145', '195'],
        ['  Accrued Expenses', '85', '110'],
        ['  Deferred Revenue', '280', '390'],
        ['  Short-term Debt', '50', '30'],
        ['Total Current Liabilities', '560', '725'],
        ['', '', ''],
        ['Non-Current Liabilities', '', ''],
        ['  Long-term Debt', '180', '150'],
        ['Total Liabilities', '740', '875'],
        ['', '', ''],
        ['Shareholders Equity', '', ''],
        ['  Share Capital', '100', '100'],
        ['  Retained Earnings', '110', '260'],
        ['Total Equity', '210', '360'],
        ['', '', ''],
        ['TOTAL LIABILITIES & EQUITY', '950', '1,235']
    ]

    table2 = Table(bs_data, colWidths=[3.2*inch, 1.3*inch, 1.3*inch])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEABOVE', (0, 5), (-1, 5), 1, colors.black),
        ('LINEABOVE', (0, 12), (-1, 12), 1, colors.black),
        ('LINEABOVE', (0, 14), (-1, 14), 2, colors.black),
        ('LINEABOVE', (0, 21), (-1, 21), 1, colors.black),
        ('LINEABOVE', (0, 24), (-1, 24), 1, colors.black),
        ('LINEABOVE', (0, 29), (-1, 29), 1, colors.black),
        ('LINEABOVE', (0, 31), (-1, 31), 2, colors.black),
        ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
        ('FONTNAME', (0, 12), (-1, 12), 'Helvetica-Bold'),
        ('FONTNAME', (0, 14), (-1, 14), 'Helvetica-Bold'),
    ]))

    story.append(table2)
    story.append(Spacer(1, 0.3*inch))

    # Notes
    story.append(Paragraph("KEY NOTES", styles['Heading3']))
    text = """
    1. <b>Revenue Recognition:</b> Subscription revenue is recognized ratably over the contract term.
    Average contract length is 12 months with monthly billing for Basic/Professional and annual
    prepayment for Enterprise.

    2. <b>Cash Position:</b> Current cash of €420K provides approximately 12 months of runway at
    current burn rate (€35K/month). The company has been EBITDA positive since Q3 2023.

    3. <b>Debt Structure:</b> €150K long-term debt consists of an ICO loan (Spanish government-backed)
    at 3.2% fixed rate, maturing in December 2026. €30K short-term debt is a revolving credit line.

    4. <b>Deferred Revenue:</b> High deferred revenue (€390K) reflects annual prepayments from
    Enterprise clients and is a positive indicator of customer commitment. This represents
    approximately 3.5 months of forward revenue.

    5. <b>Accounts Receivable:</b> Days Sales Outstanding (DSO) increased from 30 to 36 days in 2024,
    reflecting slower collections from some mid-market accounts. Management is implementing automated
    dunning processes to address this.
    """
    story.append(Paragraph(text, styles['BodyText']))

    doc.build(story)
    print(f"✅ Generated: {output_path.name}")


def generate_legal_report(output_path):
    """Genera reporte legal del target."""
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    story.append(Paragraph("LEGAL DUE DILIGENCE REPORT", title_style))
    story.append(Paragraph("TechFlow Solutions SL", styles['Heading2']))
    story.append(Paragraph("Prepared by: Martínez & Asociados Abogados", styles['Normal']))
    story.append(Paragraph("Date: " + datetime.date.today().strftime("%B %d, %Y"), styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Corporate structure
    story.append(Paragraph("1. CORPORATE STRUCTURE", styles['Heading2']))
    text = """
    TechFlow Solutions SL es una Sociedad Limitada constituida en Madrid el 15 de marzo de 2018,
    con CIF B-88234567. Capital social: €100,000 dividido en 1,000 participaciones de €100 cada una.

    <b>Estructura accionarial actual:</b>
    - Carlos Ruiz Martínez (CEO/Founder): 45% (450 participaciones)
    - Ana Gómez Torres (CTO/Co-founder): 35% (350 participaciones)
    - Innvierte Capital SGCR (Venture Capital): 20% (200 participaciones)

    <b>Estatutos sociales:</b> Los estatutos contienen cláusulas de drag-along y tag-along estándar.
    También incluyen derechos de veto para Innvierte Capital en decisiones estratégicas (fusiones,
    adquisiciones, endeudamiento >€200K, emisión de nuevas participaciones).
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # IP
    story.append(Paragraph("2. INTELLECTUAL PROPERTY", styles['Heading2']))
    text = """
    <b>Software y Código Fuente:</b> La plataforma TechFlow es propiedad 100% de la compañía.
    Todo el código fue desarrollado internamente por empleados bajo contratos que asignan IP a la empresa.
    Se identificaron dos módulos menores (representando ~3% del código total) que utilizan librerías
    open-source bajo licencia MIT, sin restricciones comerciales.

    <b>Marcas:</b> "TechFlow" y el logo están registrados en la OEPM (Oficina Española de Patentes y Marcas)
    desde 2018, clases 9 y 42. No se identificaron conflictos de marca en búsquedas preliminares.

    <b>RED FLAG:</b> La compañía no ha registrado patentes sobre su tecnología core. Aunque el sector
    SaaS típicamente no depende de patentes, esto podría representar riesgo si competidores desarrollan
    soluciones similares. Recomendación: evaluar patentabilidad de algoritmos propietarios de
    automatización.
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Employment
    story.append(Paragraph("3. EMPLOYMENT & LABOR", styles['Heading2']))
    text = """
    <b>Plantilla actual:</b> 28 empleados, todos con contratos indefinidos excepto 2 becarios.
    Todos los contratos fueron revisados y están en conformidad con legislación laboral española.

    <b>Key personnel contracts:</b> El CEO y CTO tienen contratos específicos con cláusulas de
    no-competencia (2 años post-salida) y non-solicit (1 año). Bonus structure vinculada a métricas
    de ARR y customer retention.

    <b>POTENCIAL PROBLEMA:</b> Se identificaron 3 empleados clave (2 senior engineers, 1 sales director)
    sin cláusulas de permanencia ni retención. Existe riesgo de salida post-adquisición. Recomendación:
    implementar programa de retention equity o earnout para empleados críticos.

    <b>Contingencias laborales:</b> No existen demandas laborales activas. Se identificó un procedimiento
    de conciliación de 2022 (despido improcedente) que fue resuelto con indemnización de €18K, sin
    impacto material.
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Contracts
    story.append(Paragraph("4. MATERIAL CONTRACTS", styles['Heading2']))
    text = """
    <b>Customer Contracts:</b> Se revisaron los 25 contratos más grandes (representan 60% del ARR).
    Todos incluyen términos estándar SaaS:
    - Autorenovación automática con 30 días de preaviso
    - SLA de 99.5% uptime (penalización: créditos proporcionales, no reembolsos)
    - Limitación de responsabilidad a 12 meses de fees pagados

    <b>RED FLAG MODERADO:</b> El segundo cliente más grande (Logística del Sur SA, €180K ARR) tiene
    cláusula de terminación sin causa con 60 días de aviso. Este cliente ha estado en conversaciones
    para renegociar pricing (solicitan descuento 20%). Riesgo de churn material.

    <b>Supplier Contracts:</b> Principales proveedores son AWS (hosting) y Twilio (comunicaciones).
    Contratos estándar sin compromisos mínimos, con pricing escalado por volumen. No hay dependencias
    críticas de único proveedor.

    <b>Partnership Agreements:</b> Existen acuerdos comerciales con 3 integradores (Sage, A3 Software, Holded)
    que permiten integración técnica. No hay exclusividades ni revenue-sharing, solo acuerdos de
    co-marketing sin obligaciones vinculantes.
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(PageBreak())

    # Compliance
    story.append(Paragraph("5. REGULATORY COMPLIANCE", styles['Heading2']))
    text = """
    <b>GDPR:</b> La compañía procesadatos personales de usuarios finales (nombre, email, datos de uso).
    Se verificó:
    - Política de privacidad actualizada y conforme a GDPR
    - DPO externo designado (required dado volumen >10,000 data subjects)
    - Contratos DPA (Data Processing Agreements) con subprocesadores (AWS, Twilio)
    - Registro de actividades de tratamiento completo

    <b>POTENCIAL ISSUE:</b> En auditoría de sistemas se detectaron logs de acceso con retención >2 años,
    excediendo lo necesario según principio de minimización GDPR. Management indica que implementarán
    política de borrado automático Q1 2025. Riesgo sancionador bajo pero requiere seguimiento.

    <b>Ciberseguridad:</b> La empresa completó audit ISO 27001 en marzo 2024 y está en proceso de
    certificación (esperada Q2 2025). Se implementaron controles técnicos estándar (encriptación,
    2FA, penetration tests anuales). No se han reportado brechas de seguridad materiales.

    <b>Licenses & Permits:</b> No se requieren licencias especiales para operar el negocio SaaS.
    Todos los registros mercantiles y fiscales están al día.
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Litigation
    story.append(Paragraph("6. LITIGATION & DISPUTES", styles['Heading2']))
    text = """
    <b>Current Litigation:</b> No existen litigios activos contra la compañía.

    <b>Historical:</b>
    - 2022: Procedimiento laboral por despido improcedente (resuelto, €18K)
    - 2023: Reclamación de cliente insatisfecho por €12K (desestimada por tribunal mercantil)

    <b>Contingent Liabilities:</b> Management reporta que no tienen conocimiento de amenazas de
    demanda o disputas materiales pendientes.
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(Spacer(1, 0.3*inch))

    # Conclusion
    story.append(Paragraph("7. SUMMARY & RECOMMENDATIONS", styles['Heading2']))
    text = """
    <b>Overall Assessment:</b> La revisión legal no revela impedimentos materiales para la transacción.
    Los principales riesgos identificados son:

    <b>HIGH PRIORITY:</b>
    1. Cláusula de terminación sin causa del 2° cliente más grande - requiere mitigation plan
    2. Ausencia de retention agreements para key employees - recomendar earnout structure

    <b>MEDIUM PRIORITY:</b>
    3. Falta de protección de IP vía patentes - evaluar estrategia de protección
    4. Logs GDPR con retención excesiva - requiere remediation antes de closing

    <b>Recommended next steps:</b>
    - Negociar extensión de contrato con Logística del Sur SA con términos mejorados
    - Implementar equity retention plan para los 3 empleados clave identificados
    - Completar auditoría GDPR completa con externo especializado
    - Considerar solicitud de patente provisional para algoritmos core
    """
    story.append(Paragraph(text, styles['BodyText']))

    doc.build(story)
    print(f"✅ Generated: {output_path.name}")


def generate_commercial_report(output_path):
    """Genera reporte comercial del target."""
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    story.append(Paragraph("COMMERCIAL DUE DILIGENCE", title_style))
    story.append(Paragraph("TechFlow Solutions SL", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))

    # Customer base
    story.append(Paragraph("1. CUSTOMER BASE ANALYSIS", styles['Heading2']))
    text = """
    <b>Total Customers:</b> 850 activos (defined as: con suscripción activa y uso en últimos 30 días)

    <b>Customer Segmentation:</b>
    - Basic tier (€99/mo): 552 customers (65%) → €655K ARR (23% of total)
    - Professional tier (€299/mo): 248 customers (29%) → €888K ARR (32% of total)
    - Enterprise tier (custom): 50 customers (6%) → €1,250K ARR (45% of total)

    <b>Concentration Risk:</b> Top 10 customers represent 35% of ARR. El top customer (Banco Popular Digital)
    representa 8% del ARR (€224K). Concentración moderada-alta para empresa de este tamaño.

    <b>Geographic Distribution:</b>
    - Madrid: 38%
    - Barcelona: 24%
    - Valencia: 12%
    - Andalucía: 15%
    - Otras regiones: 11%

    Fuerte sesgo hacia grandes ciudades, oportunidad de expansión en regiones infrapenetradas.
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Cohort analysis
    story.append(Paragraph("2. COHORT & RETENTION ANALYSIS", styles['Heading2']))
    text = """
    <b>Net Revenue Retention (NRR):</b> 108% en 2024, descompuesto en:
    - Gross Revenue Retention: 88% (12% churn anual)
    - Expansion revenue: +20% (upsells from Basic → Professional → Enterprise)

    <b>Churn Analysis:</b>
    - Logo churn: 12% anual (industry benchmark SaaS B2B: 10-15%)
    - Churn es más alto en Basic tier (18% anual) vs Professional (8%) y Enterprise (4%)
    - Principales razones de churn (customer survey):
      1. Precio (32%) - sensibilidad en micro-empresas
      2. Complejidad de uso (28%) - onboarding insuficiente
      3. Falta de features (22%) - principalmente integraciones con sistemas legacy
      4. Competidor (18%) - principalmente losses a Monday.com y Asana

    <b>Expansion Motions:</b>
    - 38% de clientes Basic han hecho upgrade a Professional en algún momento (median: 8 meses)
    - 22% de clientes Professional han hecho upgrade a Enterprise (median: 14 meses)
    - Cross-sell de módulos adicionales representa €180K ARR incremental (6% del total)

    <b>RED FLAG:</b> Churn en Basic tier es alto y creciente (era 14% en 2023, ahora 18%).
    Management atribuye esto a entrada de competidores con free tiers agresivos. Requiere estrategia
    de valor añadido o ajuste de pricing/packaging.
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Sales & marketing
    story.append(Paragraph("3. SALES & MARKETING EFFICIENCY", styles['Heading2']))
    text = """
    <b>Customer Acquisition Cost (CAC):</b> €1,350 blended (2024)
    - Basic: €580
    - Professional: €1,200
    - Enterprise: €5,400

    <b>CAC Payback Period:</b> 18 months blended
    - Basic: 16 months (mejorado desde 20 en 2023 con automatización)
    - Professional: 12 months
    - Enterprise: 22 months (subiendo desde 18 en 2023 - preocupante)

    <b>LTV:CAC Ratio:</b> 3.2x (healthy benchmark: >3.0x)
    - Calculation: LTV = €4,320 (ARPA €360 × Gross Margin 78% × 1/Churn 12%)

    <b>Sales Channels:</b>
    - Direct sales (inside sales team): 58% de new logos
    - Inbound marketing (SEO, content): 28% de new logos
    - Partnerships/referrals: 14% de new logos

    <b>Marketing Spend Efficiency:</b>
    - Total marketing budget 2024: €820K (29% of revenue)
    - PPC (Google Ads, LinkedIn): €280K → 210 SQLs → 68 customers (32% conversion)
    - Content marketing: €180K → 3,200 MQLs → 420 SQLs → 95 customers (23% conversion)
    - Events & sponsorships: €120K → ROI difícil de trackear, brand awareness
    - Team salaries: €240K

    <b>CONCERN:</b> CAC ha subido 22% YoY (€1,350 vs €1,106 en 2023) mientras ARPA solo creció 8%.
    Esto refleja saturación de canales bottom-funnel (PPC cada vez más caro) y mayor competencia.
    Management debe demostrar plan creíble para revertir esta tendencia.
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(PageBreak())

    # Competitive position
    story.append(Paragraph("4. COMPETITIVE LANDSCAPE", styles['Heading2']))
    text = """
    <b>Main Competitors:</b>

    1. <b>Monday.com</b> (Internacional)
       - Ventaja: Brand recognition, feature richness, funding masivo
       - Desventaja: Precio 2-3x más alto, menos soporte local
       - Overlap: Alto en Professional/Enterprise, bajo en Basic

    2. <b>Asana</b> (Internacional)
       - Similar a Monday.com
       - Menos presencia en mercado español que Monday

    3. <b>Zapier</b> (Internacional)
       - Foco en integraciones, no workflow management completo
       - Complementario más que competidor directo

    4. <b>Holded</b> (Local - España)
       - Foco en gestión financiera + workflows
       - Overlap creciente, precio similar
       - Ventaja: Integración nativa con su ERP

    <b>Competitive Differentiation:</b>
    Según entrevistas con 15 customers y 8 churned customers:
    - 72% eligieron TechFlow por "precio competitivo + soporte español"
    - 56% valoran "rapidez de implementación" vs competidores
    - 43% destacan "integración con sistemas españoles (A3, Sage)"

    <b>Win/Loss Analysis:</b>
    - Win rate en deals competidos: 38% (vs Monday 32%, Asana 18%, otros 12%)
    - Main win reasons: Precio (65%), soporte local (52%), time-to-value (45%)
    - Main loss reasons: "Quieren marca reconocida" (38%), "Necesitan features avanzadas" (35%)

    <b>STRATEGIC RISK:</b> TechFlow compite principalmente en precio y servicio local. Si players
    internacionales invierten en localización (ya empezando: Monday abrió oficina Madrid en 2024),
    la ventaja competitiva se erosiona. Requiere diferenciación basada en producto, no solo en GTM.
    """
    story.append(Paragraph(text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Market opportunity
    story.append(Paragraph("5. MARKET SIZING & OPPORTUNITY", styles['Heading2']))
    text = """
    <b>TAM (Total Addressable Market):</b>
    - Workflow automation software en España: €850M (2024, creciendo 18% CAGR)
    - Subsegmento PYME (10-250 empleados): €420M
    - TechFlow current penetration: 0.67% del TAM PYME

    <b>SAM (Serviceable Available Market):</b>
    - Empresas españolas 10-250 empleados con procesos digitalizables: ~145,000
    - Target specific sectors (servicios, logística, retail): ~58,000 empresas
    - Average ARPA €3,300 → SAM = €191M
    - Current penetration: 1.5% del SAM

    <b>Growth Vectors:</b>
    1. <b>Market penetration</b> (España): Massive runway (1.5% penetrated)
    2. <b>Geographic expansion</b>: Portugal, Italia (markets 60% y 180% del tamaño español)
    3. <b>Product expansion</b>: IA/ML module (management estimates +€150K ARR in year 1)
    4. <b>Move upmarket</b>: Target 250-1,000 employee companies (higher ARPA, lower churn)

    <b>Base / Upside Scenarios:</b>
    - <b>Base case</b> (management plan): €2.8M → €6.5M ARR in 3 years (32% CAGR)
      Assumes: España growth + Portugal launch + product expansion
    - <b>Upside case</b> (w/ acquirer resources): €2.8M → €9.2M ARR in 3 years (48% CAGR)
      Assumes: Above + sales team scaling + Italy launch + move upmarket

    Management plan es ambicioso pero creíble dado TAM. Upside case requiere capital + expertise
    que acquirer puede aportar.
    """
    story.append(Paragraph(text, styles['BodyText']))

    doc.build(story)
    print(f"✅ Generated: {output_path.name}")


def main():
    """Genera todos los PDFs del data room."""
    print("📁 Generando Data Room de ejemplo para TechFlow Solutions SL...")
    print()

    # Create folder
    folder = create_dataroom_folder()

    # Generate documents
    generate_executive_summary(folder / "01_Executive_Summary.pdf")
    generate_financial_statements(folder / "02_Financial_Statements_2022-2024.pdf")
    generate_legal_report(folder / "03_Legal_Due_Diligence_Report.pdf")
    generate_commercial_report(folder / "04_Commercial_Due_Diligence.pdf")

    print()
    print("✅ Data Room generado exitosamente!")
    print(f"📂 Ubicación: {folder.absolute()}")
    print()
    print("📋 Documentos creados:")
    print("   1. Executive Summary")
    print("   2. Financial Statements (P&L + Balance Sheet)")
    print("   3. Legal Due Diligence Report")
    print("   4. Commercial Due Diligence")
    print()
    print("🤖 Ahora puedes probar el DD Agent subiendo estos PDFs!")


if __name__ == "__main__":
    main()
