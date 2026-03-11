"""
Equity Watch — Daily Email Sender
Fetches live stock data, compares to previous day, sends HTML email with changes.
"""

import os
import json
import smtplib
import urllib.request
import urllib.error
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── CONFIG ──────────────────────────────────────────────────────────────────
RECIPIENT     = os.environ["RECIPIENT_EMAIL"]   # set in GitHub Secrets
GMAIL_USER    = os.environ["GMAIL_USER"]        # your gmail address
GMAIL_PASS    = os.environ["GMAIL_APP_PASS"]    # Gmail App Password
PAGES_URL     = os.environ["PAGES_URL"]         # e.g. https://youruser.github.io/equity-watch/
PREV_DATA_FILE = "prev_data.json"               # stored as GitHub Actions artifact

TICKERS = ["MSFT","GOOGL","V","LLY","JPM","AVGO","COST","UNH"]

STOCK_META = {
    "MSFT": {"name":"Microsoft Corp.",     "sector":"Technology",       "consensus":"Strong Buy","upside":"+18%"},
    "GOOGL":{"name":"Alphabet Inc.",       "sector":"Technology",       "consensus":"Buy",       "upside":"+22%"},
    "V":    {"name":"Visa Inc.",           "sector":"Financials",       "consensus":"Buy",       "upside":"+14%"},
    "LLY":  {"name":"Eli Lilly & Co.",     "sector":"Healthcare",       "consensus":"Buy",       "upside":"+20%"},
    "JPM":  {"name":"JPMorgan Chase",      "sector":"Financials",       "consensus":"Buy",       "upside":"+12%"},
    "AVGO": {"name":"Broadcom Inc.",       "sector":"Technology",       "consensus":"Strong Buy","upside":"+25%"},
    "COST": {"name":"Costco Wholesale",    "sector":"Consumer Staples", "consensus":"Buy",       "upside":"+10%"},
    "UNH":  {"name":"UnitedHealth Group",  "sector":"Healthcare",       "consensus":"Strong Buy","upside":"+21%"},
}

# ── FETCH PRICE + BASIC METRICS via Yahoo Finance (no API key needed) ────────
def fetch_quote(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        result = data["chart"]["result"][0]
        meta   = result["meta"]
        price       = round(meta.get("regularMarketPrice", 0), 2)
        prev_close  = round(meta.get("chartPreviousClose", price), 2)
        change      = round(price - prev_close, 2)
        change_pct  = round((change / prev_close) * 100, 2) if prev_close else 0
        mkt_cap_raw = meta.get("marketCap", 0)
        if mkt_cap_raw >= 1e12:
            mkt_cap = f"${mkt_cap_raw/1e12:.1f}T"
        elif mkt_cap_raw >= 1e9:
            mkt_cap = f"${mkt_cap_raw/1e9:.0f}B"
        else:
            mkt_cap = "N/A"
        return {
            "price":      price,
            "prev_close": prev_close,
            "change":     change,
            "change_pct": change_pct,
            "mkt_cap":    mkt_cap,
        }
    except Exception as e:
        print(f"  Warning: could not fetch {ticker}: {e}")
        return {"price":0,"prev_close":0,"change":0,"change_pct":0,"mkt_cap":"N/A"}

# ── LOAD PREVIOUS DAY DATA ────────────────────────────────────────────────────
def load_prev():
    if os.path.exists(PREV_DATA_FILE):
        with open(PREV_DATA_FILE) as f:
            return json.load(f)
    return {}

def save_current(data):
    with open(PREV_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── FORMAT HELPERS ────────────────────────────────────────────────────────────
def arrow(val):
    if val > 0:  return "▲"
    if val < 0:  return "▼"
    return "—"

def change_color(val):
    if val > 0:  return "#00e5a0"
    if val < 0:  return "#ff6b6b"
    return "#6ee7f7"

def consensus_color(c):
    if "Strong Buy" in c: return "#00e5a0"
    if "Buy" in c:        return "#6ee7f7"
    if "Hold" in c:       return "#f5c842"
    return "#ff6b6b"

# ── BUILD HTML EMAIL ──────────────────────────────────────────────────────────
def build_email(current, prev):
    today = datetime.now().strftime("%A, %B %d, %Y")

    # Build rows
    rows_html = ""
    for ticker in TICKERS:
        q    = current.get(ticker, {})
        pq   = prev.get(ticker, {})
        meta = STOCK_META[ticker]

        price      = q.get("price", 0)
        chg        = q.get("change", 0)
        chg_pct    = q.get("change_pct", 0)
        mkt_cap    = q.get("mkt_cap", "N/A")
        prev_price = pq.get("price", 0)
        price_diff = round(price - prev_price, 2) if prev_price else 0

        chg_color     = change_color(chg)
        day_chg_str   = f"{arrow(chg)} {abs(chg_pct):.2f}%"
        week_chg_str  = f"{arrow(price_diff)} ${abs(price_diff):.2f}" if prev_price else "—"
        week_color    = change_color(price_diff)
        cons_color    = consensus_color(meta["consensus"])

        # Highlight row if moved more than 1.5% today
        row_bg = "#0d1828" if abs(chg_pct) < 1.5 else "rgba(0,229,160,0.06)" if chg_pct > 0 else "rgba(255,107,107,0.06)"
        notable = ""
        if abs(chg_pct) >= 1.5:
            notable = f'<span style="font-size:9px;padding:2px 6px;border-radius:3px;background:{"rgba(0,229,160,0.15)" if chg_pct>0 else "rgba(255,107,107,0.15)"};color:{chg_color};margin-left:6px;">NOTABLE MOVE</span>'

        rows_html += f"""
        <tr style="border-bottom:1px solid #111e2e;background:{row_bg};">
          <td style="padding:12px 14px;white-space:nowrap;">
            <span style="font-family:Georgia,serif;font-weight:700;font-size:15px;color:#c8dff0;">{ticker}</span>{notable}
            <div style="font-size:10px;color:#3a6080;margin-top:2px;">{meta['name']}</div>
          </td>
          <td style="padding:12px 14px;text-align:right;font-size:15px;font-weight:600;color:#c8dff0;">${price:.2f}</td>
          <td style="padding:12px 14px;text-align:right;font-size:12px;font-weight:600;color:{chg_color};">{day_chg_str}</td>
          <td style="padding:12px 14px;text-align:right;font-size:12px;color:{week_color};">{week_chg_str}</td>
          <td style="padding:12px 14px;text-align:center;">
            <span style="font-size:10px;padding:3px 8px;border-radius:4px;background:{cons_color}22;color:{cons_color};font-weight:600;">{meta['consensus']}</span>
          </td>
          <td style="padding:12px 14px;text-align:center;font-size:11px;color:#00e5a0;font-weight:600;">{meta['upside']}</td>
          <td style="padding:12px 14px;text-align:right;font-size:11px;color:#3a6080;">{mkt_cap}</td>
          <td style="padding:12px 14px;text-align:center;font-size:10px;color:#3a6080;">{meta['sector']}</td>
        </tr>"""

    # Notable movers summary
    movers = [(t, current[t]["change_pct"]) for t in TICKERS if t in current and abs(current[t].get("change_pct",0)) >= 1.0]
    movers.sort(key=lambda x: abs(x[1]), reverse=True)
    movers_html = ""
    if movers:
        movers_html = '<div style="margin-bottom:20px;padding:14px 18px;background:#0a1828;border-radius:8px;border:1px solid #1a2e4a;">'
        movers_html += '<div style="font-size:9px;letter-spacing:2px;color:#2a5070;margin-bottom:10px;">TODAY\'S NOTABLE MOVES</div>'
        movers_html += '<div style="display:flex;flex-wrap:wrap;gap:8px;">'
        for tk, pct in movers:
            col = "#00e5a0" if pct > 0 else "#ff6b6b"
            movers_html += f'<span style="padding:4px 10px;border-radius:4px;background:{col}18;color:{col};font-size:12px;font-weight:600;">{tk} {arrow(pct)}{abs(pct):.2f}%</span>'
        movers_html += "</div></div>"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Equity Watch — {today}</title>
</head>
<body style="margin:0;padding:0;background:#080d14;font-family:'Courier New',monospace;color:#d6e4f0;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#080d14;padding:20px 0;">
<tr><td align="center">
<table width="700" cellpadding="0" cellspacing="0" style="max-width:700px;width:100%;">

  <!-- HEADER -->
  <tr><td style="background:linear-gradient(90deg,#0d1a2e,#0a1628);border-bottom:2px solid #00e5a0;padding:22px 28px;border-radius:10px 10px 0 0;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td>
          <div style="font-family:Georgia,serif;font-size:22px;font-weight:700;color:#fff;letter-spacing:1px;">📈 EQUITY WATCH</div>
          <div style="font-size:10px;color:#4a7a9b;letter-spacing:2px;margin-top:3px;">DAILY BRIEFING · MULTI-SOURCE ANALYST RATINGS</div>
        </td>
        <td align="right">
          <div style="font-size:11px;color:#2a5070;">{today}</div>
          <div style="margin-top:6px;">
            <a href="{PAGES_URL}" style="display:inline-block;padding:7px 16px;background:linear-gradient(90deg,#00e5a0,#6ee7f7);color:#080d14;font-size:11px;font-weight:700;border-radius:5px;text-decoration:none;letter-spacing:1px;">OPEN FULL DASHBOARD →</a>
          </div>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- MOVERS -->
  <tr><td style="background:#0a1220;padding:16px 20px;">
    {movers_html if movers_html else '<div style="font-size:10px;color:#2a5070;padding:4px 0;">No moves ≥1% today — quiet session.</div>'}
  </td></tr>

  <!-- TABLE -->
  <tr><td style="background:#0a1220;padding:0 20px 20px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-radius:10px;overflow:hidden;border:1px solid #1a2e4a;">
      <thead>
        <tr style="background:#091220;border-bottom:2px solid #1a2e4a;">
          <th style="padding:10px 14px;text-align:left;font-size:8px;letter-spacing:2px;color:#2a5070;font-weight:600;">STOCK</th>
          <th style="padding:10px 14px;text-align:right;font-size:8px;letter-spacing:2px;color:#2a5070;font-weight:600;">PRICE</th>
          <th style="padding:10px 14px;text-align:right;font-size:8px;letter-spacing:2px;color:#2a5070;font-weight:600;">TODAY</th>
          <th style="padding:10px 14px;text-align:right;font-size:8px;letter-spacing:2px;color:#2a5070;font-weight:600;">vs YESTERDAY</th>
          <th style="padding:10px 14px;text-align:center;font-size:8px;letter-spacing:2px;color:#2a5070;font-weight:600;">CONSENSUS</th>
          <th style="padding:10px 14px;text-align:center;font-size:8px;letter-spacing:2px;color:#2a5070;font-weight:600;">UPSIDE</th>
          <th style="padding:10px 14px;text-align:right;font-size:8px;letter-spacing:2px;color:#2a5070;font-weight:600;">MKT CAP</th>
          <th style="padding:10px 14px;text-align:center;font-size:8px;letter-spacing:2px;color:#2a5070;font-weight:600;">SECTOR</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </td></tr>

  <!-- FOOTER -->
  <tr><td style="background:#091220;padding:16px 24px;border-radius:0 0 10px 10px;border-top:1px solid #1a2e4a;">
    <div style="font-size:9px;color:#1e3a5a;line-height:1.8;">
      ⚠ This digest is for informational purposes only and does not constitute financial advice. Analyst ratings as of Q1 2025. Price data is live from Yahoo Finance. Always conduct your own due diligence.
      <br/>To unsubscribe, remove your email from the GitHub Actions secret RECIPIENT_EMAIL.
    </div>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""
    return html


# ── SEND EMAIL ────────────────────────────────────────────────────────────────
def send_email(html_body, today_str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📈 Equity Watch — {today_str}"
    msg["From"]    = GMAIL_USER
    msg["To"]      = RECIPIENT
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, RECIPIENT, msg.as_string())
    print(f"✅ Email sent to {RECIPIENT}")


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    today_str = datetime.now().strftime("%B %d, %Y")
    print(f"🔍 Fetching quotes for {TICKERS}...")

    current = {}
    for ticker in TICKERS:
        print(f"  {ticker}...")
        current[ticker] = fetch_quote(ticker)

    prev = load_prev()
    print("📧 Building email...")
    html = build_email(current, prev)

    print("📤 Sending...")
    send_email(html, today_str)

    save_current(current)
    print("💾 Saved current data for tomorrow's comparison.")
