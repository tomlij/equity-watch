<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Equity Watch v2 — Multi-Source Analyst Ratings</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=Syne:wght@700;800&display=swap" rel="stylesheet" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #080d14; }
  ::-webkit-scrollbar { width: 4px; background: #0d1520; }
  ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 2px; }
  .stock-btn { transition: all 0.18s; cursor: pointer; border: none; background: none; }
  .stock-btn:hover { background: rgba(110,231,247,0.07) !important; }
  .stock-btn.active { background: rgba(0,229,160,0.10) !important; border-left: 3px solid #00e5a0 !important; }
  .tab-btn { transition: all 0.15s; cursor: pointer; }
  .tab-btn:hover { opacity: 0.85; }
  .rating-pill { transition: transform 0.15s; display: inline-block; }
  .rating-pill:hover { transform: scale(1.05); }
  .source-row:hover { background: rgba(255,255,255,0.03); }
  .investor-card:hover { border-color: rgba(0,229,160,0.3) !important; background: rgba(0,229,160,0.05) !important; }
  @keyframes fadeIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform:translateY(0); } }
  .fade-in { animation: fadeIn 0.3s ease forwards; }
  @keyframes bar { from { width: 0; } to { width: var(--w); } }
  .bar-anim { animation: bar 0.7s cubic-bezier(.4,0,.2,1) forwards; }
  @keyframes scorePop { from { transform: scale(0.7); opacity:0; } to { transform: scale(1); opacity:1; } }
  .score-pop { animation: scorePop 0.4s cubic-bezier(.34,1.56,.64,1) forwards; }
  .indicator-card:hover { border-color: rgba(110,231,247,0.25) !important; }
  .ind-bar { transition: width 0.6s cubic-bezier(.4,0,.2,1); }
</style>
</head>
<body>
<div id="root"></div>
<script type="text/babel">
const { useState } = React;

const stocks = [
  {
    ticker: "MSFT", name: "Microsoft Corp.", sector: "Technology",
    marketCap: "$3.1T", price: "$415",
    description: "Global leader in cloud computing (Azure), productivity software (Office 365), and AI integration via OpenAI partnership. Consistent revenue growth, dominant enterprise moats, and accelerating AI monetization make it a premier large-cap holding.",
    indicators: {
      pe: { value: 34, sector_avg: 28, label: "P/E Ratio", note: "Premium to sector; justified by AI growth" },
      peg: { value: 1.8, sector_avg: 2.1, label: "PEG Ratio", note: "Below sector avg — growth not overpaying" },
      ps: { value: 12.4, sector_avg: 8.0, label: "P/S Ratio", note: "High but supported by margins" },
      roe: { value: 38, sector_avg: 22, label: "ROE %", note: "Exceptional capital efficiency" },
      debtEquity: { value: 0.35, sector_avg: 0.6, label: "Debt/Equity", note: "Very low leverage" },
      grossMargin: { value: 69, sector_avg: 55, label: "Gross Margin %", note: "Best-in-class software margins" },
      revenueGrowth: { value: 16, sector_avg: 10, label: "Rev Growth YoY %", note: "Accelerating with AI" },
      fcfYield: { value: 2.8, sector_avg: 2.1, label: "FCF Yield %", note: "Strong free cash flow" },
    },
    ratings: {
      CFRA: { rating: "Strong Buy", score: 5 }, Argus: { rating: "Buy", score: 4 },
      Morningstar: { rating: "Buy", score: 4 }, LSEG: { rating: "Buy", score: 4 },
      Schwab: { rating: "A", score: 5 }, SeekingAlpha: { rating: "Strong Buy", score: 5 },
      "SA Wall St.": { rating: "Strong Buy", score: 5 }, "Market Edge": { rating: "Long", score: 4 },
    },
    bigInvestors: [
      { name: "Bill Ackman", firm: "Pershing Square", stance: "Core Hold", note: "Long-term AI infrastructure play; one of his largest positions" },
      { name: "Warren Buffett", firm: "Berkshire Hathaway", stance: "Watching", note: "Not a position but frequently praised by Munger for its moat" },
      { name: "Cathie Wood", firm: "ARK Invest", stance: "Trimmed", note: "Reduced position citing valuation; still AI-bullish broadly" },
      { name: "Ken Griffin", firm: "Citadel", stance: "Strong Buy", note: "Significant position; top 5 holding as of latest 13F" },
    ],
    consensus: "Strong Buy", upside: "+18%", pe: 34, beta: 0.90,
  },
  {
    ticker: "GOOGL", name: "Alphabet Inc.", sector: "Technology",
    marketCap: "$2.2T", price: "$178",
    description: "Parent of Google Search, YouTube, and Google Cloud. Dominates digital advertising with 90%+ search share. Cloud growing 28% YoY. Deep AI via Gemini. Trading at discount to peers on P/E.",
    indicators: {
      pe: { value: 22, sector_avg: 28, label: "P/E Ratio", note: "Discount to sector — compelling value" },
      peg: { value: 1.2, sector_avg: 2.1, label: "PEG Ratio", note: "Among the best value in mega-cap tech" },
      ps: { value: 6.1, sector_avg: 8.0, label: "P/S Ratio", note: "Cheap relative to revenue quality" },
      roe: { value: 29, sector_avg: 22, label: "ROE %", note: "Strong returns despite capex cycle" },
      debtEquity: { value: 0.08, sector_avg: 0.6, label: "Debt/Equity", note: "Essentially debt-free" },
      grossMargin: { value: 57, sector_avg: 55, label: "Gross Margin %", note: "Improving as Cloud scales" },
      revenueGrowth: { value: 13, sector_avg: 10, label: "Rev Growth YoY %", note: "Reaccelerating post-slowdown" },
      fcfYield: { value: 4.5, sector_avg: 2.1, label: "FCF Yield %", note: "Exceptional cash generation" },
    },
    ratings: {
      CFRA: { rating: "Buy", score: 4 }, Argus: { rating: "Buy", score: 4 },
      Morningstar: { rating: "Buy", score: 4 }, LSEG: { rating: "Buy", score: 4 },
      Schwab: { rating: "A", score: 5 }, SeekingAlpha: { rating: "Strong Buy", score: 5 },
      "SA Wall St.": { rating: "Strong Buy", score: 5 }, "Market Edge": { rating: "Long", score: 4 },
    },
    bigInvestors: [
      { name: "Bill Ackman", firm: "Pershing Square", stance: "New Position", note: "Initiated large stake in 2024; calls it AI value play" },
      { name: "David Tepper", firm: "Appaloosa Mgmt", stance: "Top Holding", note: "Largest position; believes AI concerns are overblown" },
      { name: "Stan Druckenmiller", firm: "Duquesne Family", stance: "Bullish", note: "Added in Q3 2024; sees Search moat intact" },
      { name: "Terry Smith", firm: "Fundsmith", stance: "Core Hold", note: "Long-term holding; quality business at fair price" },
    ],
    consensus: "Buy", upside: "+22%", pe: 22, beta: 1.05,
  },
  {
    ticker: "V", name: "Visa Inc.", sector: "Financials",
    marketCap: "$550B", price: "$285",
    description: "World's largest payment network processing ~$15T annually. Asset-light model with 50%+ net margins. Benefits from e-commerce growth and secular shift from cash to digital payments.",
    indicators: {
      pe: { value: 30, sector_avg: 16, label: "P/E Ratio", note: "Premium warranted by asset-light model" },
      peg: { value: 1.9, sector_avg: 1.5, label: "PEG Ratio", note: "Slight premium; consistent grower" },
      ps: { value: 16.2, sector_avg: 4.0, label: "P/S Ratio", note: "High; reflects 50%+ net margins" },
      roe: { value: 44, sector_avg: 12, label: "ROE %", note: "Exceptional — best in financials" },
      debtEquity: { value: 0.55, sector_avg: 2.5, label: "Debt/Equity", note: "Very low vs. financial peers" },
      grossMargin: { value: 81, sector_avg: 45, label: "Gross Margin %", note: "Network effect drives margins" },
      revenueGrowth: { value: 10, sector_avg: 6, label: "Rev Growth YoY %", note: "Steady and predictable" },
      fcfYield: { value: 3.2, sector_avg: 3.0, label: "FCF Yield %", note: "Reliable cash returns" },
    },
    ratings: {
      CFRA: { rating: "Buy", score: 4 }, Argus: { rating: "Buy", score: 4 },
      Morningstar: { rating: "Buy", score: 4 }, LSEG: { rating: "Buy", score: 4 },
      Schwab: { rating: "A", score: 5 }, SeekingAlpha: { rating: "Buy", score: 4 },
      "SA Wall St.": { rating: "Strong Buy", score: 5 }, "Market Edge": { rating: "Long", score: 4 },
    },
    bigInvestors: [
      { name: "Warren Buffett", firm: "Berkshire Hathaway", stance: "Long-Term Hold", note: "Held for years; loves the tollbooth business model" },
      { name: "Terry Smith", firm: "Fundsmith", stance: "Top 3 Holding", note: "One of his highest-conviction picks globally" },
      { name: "Charlie Munger", firm: "Daily Journal Corp", stance: "Admired", note: "Frequently cited Visa as a great compounder" },
      { name: "Ken Fisher", firm: "Fisher Investments", stance: "Overweight", note: "Secular tailwinds from cashless economy transition" },
    ],
    consensus: "Buy", upside: "+14%", pe: 30, beta: 0.92,
  },
  {
    ticker: "LLY", name: "Eli Lilly & Co.", sector: "Healthcare",
    marketCap: "$740B", price: "$800",
    description: "Pharmaceutical giant behind Mounjaro and Zepbound (GLP-1 drugs), the fastest-selling drugs in history. Massive pipeline covering obesity, diabetes, and Alzheimer's treatments.",
    indicators: {
      pe: { value: 42, sector_avg: 20, label: "P/E Ratio", note: "High but GLP-1 growth pipeline justifies" },
      peg: { value: 1.4, sector_avg: 1.8, label: "PEG Ratio", note: "Growth-adjusted valuation is reasonable" },
      ps: { value: 18.0, sector_avg: 5.0, label: "P/S Ratio", note: "Revenue is ramping rapidly" },
      roe: { value: 62, sector_avg: 18, label: "ROE %", note: "Extraordinary — drug monopoly economics" },
      debtEquity: { value: 1.8, sector_avg: 0.8, label: "Debt/Equity", note: "Elevated but manageable given FCF" },
      grossMargin: { value: 80, sector_avg: 65, label: "Gross Margin %", note: "Patented drug economics" },
      revenueGrowth: { value: 36, sector_avg: 8, label: "Rev Growth YoY %", note: "Fastest-growing large pharma globally" },
      fcfYield: { value: 1.8, sector_avg: 3.5, label: "FCF Yield %", note: "Low yield; capital deployed for growth" },
    },
    ratings: {
      CFRA: { rating: "Strong Buy", score: 5 }, Argus: { rating: "Buy", score: 4 },
      Morningstar: { rating: "Hold", score: 3 }, LSEG: { rating: "Buy", score: 4 },
      Schwab: { rating: "B", score: 4 }, SeekingAlpha: { rating: "Buy", score: 4 },
      "SA Wall St.": { rating: "Strong Buy", score: 5 }, "Market Edge": { rating: "Long", score: 4 },
    },
    bigInvestors: [
      { name: "Cathie Wood", firm: "ARK Invest", stance: "Long", note: "GLP-1 obesity market could reach $100B; high conviction" },
      { name: "Dan Loeb", firm: "Third Point", stance: "Major Position", note: "Added aggressively in 2024 on GLP-1 demand thesis" },
      { name: "Andreas Halvorsen", firm: "Viking Global", stance: "Top Holding", note: "Healthcare sector high-conviction bet" },
      { name: "Steve Cohen", firm: "Point72", stance: "Bullish", note: "Significant healthcare weighting; Lilly is core" },
    ],
    consensus: "Buy", upside: "+20%", pe: 42, beta: 0.55,
  },
  {
    ticker: "JPM", name: "JPMorgan Chase", sector: "Financials",
    marketCap: "$740B", price: "$245",
    description: "America's largest bank by assets. Record profits driven by high interest rates, investment banking recovery, and disciplined expense management under CEO Jamie Dimon.",
    indicators: {
      pe: { value: 13, sector_avg: 12, label: "P/E Ratio", note: "Fairly valued vs. sector; quality premium" },
      peg: { value: 1.1, sector_avg: 1.3, label: "PEG Ratio", note: "Reasonable for earnings growth rate" },
      ps: { value: 3.8, sector_avg: 2.5, label: "P/S Ratio", note: "Moderate premium for best-in-class bank" },
      roe: { value: 17, sector_avg: 11, label: "ROE %", note: "Top of peer group consistently" },
      debtEquity: { value: 1.2, sector_avg: 1.5, label: "Debt/Equity", note: "Normal for large bank structure" },
      grossMargin: { value: 61, sector_avg: 48, label: "Net Interest Margin %", note: "Above-average NIMs benefit from rates" },
      revenueGrowth: { value: 9, sector_avg: 5, label: "Rev Growth YoY %", note: "Solid across all business lines" },
      fcfYield: { value: 5.5, sector_avg: 4.0, label: "FCF Yield %", note: "Returning capital via buybacks+dividends" },
    },
    ratings: {
      CFRA: { rating: "Buy", score: 4 }, Argus: { rating: "Buy", score: 4 },
      Morningstar: { rating: "Hold", score: 3 }, LSEG: { rating: "Buy", score: 4 },
      Schwab: { rating: "A", score: 5 }, SeekingAlpha: { rating: "Buy", score: 4 },
      "SA Wall St.": { rating: "Buy", score: 4 }, "Market Edge": { rating: "Long", score: 4 },
    },
    bigInvestors: [
      { name: "Warren Buffett", firm: "Berkshire Hathaway", stance: "Sold / Watching", note: "Exited position but Dimon cited as best banker in America" },
      { name: "Bill Ackman", firm: "Pershing Square", stance: "Watching", note: "Has praised JPM's risk mgmt; not a current position" },
      { name: "David Tepper", firm: "Appaloosa Mgmt", stance: "Hold", note: "Banks as rate cycle beneficiary; JPM top pick" },
      { name: "Michael Burry", firm: "Scion Asset Mgmt", stance: "Financials Bull", note: "Added bank exposure; JPM seen as safe haven" },
    ],
    consensus: "Buy", upside: "+12%", pe: 13, beta: 1.10,
  },
  {
    ticker: "AVGO", name: "Broadcom Inc.", sector: "Technology",
    marketCap: "$850B", price: "$195",
    description: "Semiconductor and infrastructure software giant. AI custom chip demand (XPUs) from hyperscalers is accelerating. VMware acquisition deepens enterprise software moat.",
    indicators: {
      pe: { value: 27, sector_avg: 28, label: "P/E Ratio", note: "In-line with sector; attractive given AI mix" },
      peg: { value: 1.0, sector_avg: 2.1, label: "PEG Ratio", note: "Exceptional — growth significantly underpriced" },
      ps: { value: 14.0, sector_avg: 8.0, label: "P/S Ratio", note: "Software mix elevates revenue quality" },
      roe: { value: 55, sector_avg: 22, label: "ROE %", note: "VMware synergies boosting returns" },
      debtEquity: { value: 1.7, sector_avg: 0.6, label: "Debt/Equity", note: "Higher post-VMware; de-leveraging underway" },
      grossMargin: { value: 74, sector_avg: 55, label: "Gross Margin %", note: "Software shift driving margin expansion" },
      revenueGrowth: { value: 44, sector_avg: 10, label: "Rev Growth YoY %", note: "VMware + AI driving explosive growth" },
      fcfYield: { value: 3.5, sector_avg: 2.1, label: "FCF Yield %", note: "Strong cash conversion" },
    },
    ratings: {
      CFRA: { rating: "Strong Buy", score: 5 }, Argus: { rating: "Buy", score: 4 },
      Morningstar: { rating: "Buy", score: 4 }, LSEG: { rating: "Buy", score: 4 },
      Schwab: { rating: "A", score: 5 }, SeekingAlpha: { rating: "Strong Buy", score: 5 },
      "SA Wall St.": { rating: "Strong Buy", score: 5 }, "Market Edge": { rating: "Long", score: 4 },
    },
    bigInvestors: [
      { name: "Stan Druckenmiller", firm: "Duquesne Family", stance: "High Conviction", note: "Top AI semiconductor pick; added significantly in 2024" },
      { name: "Ken Griffin", firm: "Citadel", stance: "Large Position", note: "AI infrastructure theme; AVGO is preferred over NVDA on value" },
      { name: "David Tepper", firm: "Appaloosa Mgmt", stance: "Bullish", note: "Sees custom AI chip market as multi-year tailwind" },
      { name: "Philippe Laffont", firm: "Coatue Mgmt", stance: "Top Holding", note: "AI picks-and-shovels; AVGO among top 5 positions" },
    ],
    consensus: "Strong Buy", upside: "+25%", pe: 27, beta: 1.15,
  },
  {
    ticker: "COST", name: "Costco Wholesale", sector: "Consumer Staples",
    marketCap: "$415B", price: "$935",
    description: "Membership-based warehouse retailer with 93% renewal rate. Recession-resilient with pricing power. International expansion and e-commerce add long-term runway.",
    indicators: {
      pe: { value: 55, sector_avg: 22, label: "P/E Ratio", note: "Significant premium; loyalty moat justifies" },
      peg: { value: 3.2, sector_avg: 1.8, label: "PEG Ratio", note: "Expensive on growth-adjusted basis" },
      ps: { value: 1.6, sector_avg: 0.9, label: "P/S Ratio", note: "Low margin retail; fair for quality" },
      roe: { value: 30, sector_avg: 15, label: "ROE %", note: "Best-in-class for retail" },
      debtEquity: { value: 0.38, sector_avg: 0.8, label: "Debt/Equity", note: "Clean balance sheet" },
      grossMargin: { value: 13, sector_avg: 25, label: "Gross Margin %", note: "Low intentionally — pass savings to members" },
      revenueGrowth: { value: 7, sector_avg: 4, label: "Rev Growth YoY %", note: "Consistent; membership fees drive profits" },
      fcfYield: { value: 1.5, sector_avg: 2.5, label: "FCF Yield %", note: "Low yield reflects premium multiple" },
    },
    ratings: {
      CFRA: { rating: "Buy", score: 4 }, Argus: { rating: "Buy", score: 4 },
      Morningstar: { rating: "Hold", score: 3 }, LSEG: { rating: "Hold", score: 3 },
      Schwab: { rating: "B", score: 4 }, SeekingAlpha: { rating: "Hold", score: 3 },
      "SA Wall St.": { rating: "Buy", score: 4 }, "Market Edge": { rating: "Long", score: 4 },
    },
    bigInvestors: [
      { name: "Charlie Munger", firm: "Daily Journal Corp", stance: "Longtime Admirer", note: "Called Costco one of the greatest retailers ever built" },
      { name: "Terry Smith", firm: "Fundsmith", stance: "Core Hold", note: "Quality compounder; resilient in all economic cycles" },
      { name: "Pat Dorsey", firm: "Dorsey Asset Mgmt", stance: "High Conviction", note: "Textbook wide moat via membership loyalty flywheel" },
      { name: "Bill Miller", firm: "Miller Value Partners", stance: "Long-Term Hold", note: "Structural winner in physical retail consolidation" },
    ],
    consensus: "Buy", upside: "+10%", pe: 55, beta: 0.70,
  },
  {
    ticker: "UNH", name: "UnitedHealth Group", sector: "Healthcare",
    marketCap: "$410B", price: "$440",
    description: "Largest U.S. health insurer. Dual engine of UnitedHealthcare (insurance) and Optum (health services/pharmacy) creates vertical integration advantages. 12–15% EPS growth target.",
    indicators: {
      pe: { value: 18, sector_avg: 20, label: "P/E Ratio", note: "Slight discount; creates entry opportunity" },
      peg: { value: 1.3, sector_avg: 1.8, label: "PEG Ratio", note: "Growth-adjusted: attractively priced" },
      ps: { value: 1.1, sector_avg: 1.5, label: "P/S Ratio", note: "Low margin insurance business; reasonable" },
      roe: { value: 26, sector_avg: 14, label: "ROE %", note: "Industry-leading capital returns" },
      debtEquity: { value: 0.75, sector_avg: 0.9, label: "Debt/Equity", note: "Modest; well within comfort zone" },
      grossMargin: { value: 24, sector_avg: 18, label: "Gross Margin %", note: "Optum segment driving margin mix up" },
      revenueGrowth: { value: 12, sector_avg: 6, label: "Rev Growth YoY %", note: "Consistent double-digit grower" },
      fcfYield: { value: 4.8, sector_avg: 3.5, label: "FCF Yield %", note: "Excellent cash flow; supports buybacks" },
    },
    ratings: {
      CFRA: { rating: "Strong Buy", score: 5 }, Argus: { rating: "Buy", score: 4 },
      Morningstar: { rating: "Buy", score: 4 }, LSEG: { rating: "Buy", score: 4 },
      Schwab: { rating: "A", score: 5 }, SeekingAlpha: { rating: "Buy", score: 4 },
      "SA Wall St.": { rating: "Strong Buy", score: 5 }, "Market Edge": { rating: "Long", score: 4 },
    },
    bigInvestors: [
      { name: "Warren Buffett", firm: "Berkshire Hathaway", stance: "Held Position", note: "Healthcare services scale moat; Berkshire has owned historically" },
      { name: "Bill Ackman", firm: "Pershing Square", stance: "Long", note: "Compounding healthcare services machine; long-term hold" },
      { name: "Chase Coleman", firm: "Tiger Global", stance: "Core Holding", note: "Managed care as defensive growth; UNH is top healthcare pick" },
      { name: "Larry Fink", firm: "BlackRock", stance: "Overweight", note: "Demographic tailwinds and Optum vertical make UNH irreplaceable" },
    ],
    consensus: "Strong Buy", upside: "+21%", pe: 18, beta: 0.62,
  },
];

const ratingColor = (score) => {
  if (score >= 5) return "#00e5a0";
  if (score >= 4) return "#6ee7f7";
  if (score === 3) return "#f5c842";
  return "#ff6b6b";
};
const ratingBg = (score) => {
  if (score >= 5) return "rgba(0,229,160,0.13)";
  if (score >= 4) return "rgba(110,231,247,0.10)";
  if (score === 3) return "rgba(245,200,66,0.12)";
  return "rgba(255,107,107,0.12)";
};

const sources = ["CFRA","Argus","Morningstar","LSEG","Schwab","SeekingAlpha","SA Wall St.","Market Edge"];
const sourceNotes = {
  CFRA: "Earnings quality, risk factors, fundamental analysis",
  Argus: "Independent; focuses on earnings growth & valuation",
  Morningstar: "Fair value estimate with moat & uncertainty rating",
  LSEG: "Aggregated analyst consensus via Thomson Reuters",
  Schwab: "Proprietary A–F rating; fundamentals & technicals",
  SeekingAlpha: "Quant factor model: growth, value, profitability, momentum",
  "SA Wall St.": "Average of Wall Street analyst price targets",
  "Market Edge": "Technical + fundamental; Long/Avoid/Neutral signals",
};

const stanceColor = (stance) => {
  if (stance.includes("Strong Buy") || stance.includes("High Conviction") || stance.includes("Top") || stance.includes("Core") || stance.includes("Long") || stance.includes("New Position") || stance.includes("Major")) return "#00e5a0";
  if (stance.includes("Bull") || stance.includes("Bullish") || stance.includes("Overweight") || stance.includes("Hold")) return "#6ee7f7";
  if (stance.includes("Watching") || stance.includes("Trimmed") || stance.includes("Sold") || stance.includes("Admired")) return "#f5c842";
  return "#6ee7f7";
};

// Indicator scoring: compare value to sector_avg
const indicatorScore = (ind, key) => {
  const { value, sector_avg } = ind;
  // Higher is better: roe, grossMargin, revenueGrowth, fcfYield
  // Lower is better: pe, peg, ps, debtEquity
  const higherBetter = ["roe", "grossMargin", "revenueGrowth", "fcfYield"];
  if (higherBetter.includes(key)) {
    return value >= sector_avg ? "good" : "weak";
  } else {
    return value <= sector_avg ? "good" : "weak";
  }
};

const indicatorBarPct = (ind, key) => {
  const higherBetter = ["roe","grossMargin","revenueGrowth","fcfYield"];
  // Normalize to 0–100 for bar display
  const max = { pe:60, peg:3.5, ps:25, roe:70, debtEquity:3, grossMargin:100, revenueGrowth:50, fcfYield:8 };
  return Math.min(100, (ind.value / (max[key] || 100)) * 100);
};

function App() {
  const [selected, setSelected] = useState(stocks[0].ticker);
  const [view, setView] = useState("overview");

  const stock = stocks.find(s => s.ticker === selected);

  const avgScore = (s) => {
    const vals = Object.values(s.ratings).map(r => r.score);
    return (vals.reduce((a,b) => a+b, 0) / vals.length).toFixed(1);
  };

  // Composite indicator score (how many are "good")
  const indicatorComposite = (s) => {
    const keys = Object.keys(s.indicators);
    const good = keys.filter(k => indicatorScore(s.indicators[k], k) === "good").length;
    return `${good}/${keys.length}`;
  };

  return (
    <div style={{ minHeight:"100vh", background:"#080d14", fontFamily:"'IBM Plex Mono',monospace", color:"#d6e4f0" }}>
      {/* Header */}
      <div style={{ background:"linear-gradient(90deg,#0d1a2e,#0a1628)", borderBottom:"1px solid #1a2e4a", padding:"16px 28px", display:"flex", alignItems:"center", gap:14 }}>
        <div style={{ width:34, height:34, background:"linear-gradient(135deg,#00e5a0,#6ee7f7)", borderRadius:8, display:"flex", alignItems:"center", justifyContent:"center", fontSize:16, flexShrink:0 }}>📈</div>
        <div>
          <div style={{ fontFamily:"'Syne',sans-serif", fontSize:17, fontWeight:800, letterSpacing:1, color:"#fff" }}>EQUITY WATCH</div>
          <div style={{ fontSize:9, color:"#4a7a9b", letterSpacing:2 }}>MULTI-SOURCE RATINGS · INDICATORS · SMART MONEY · 6–24 MO</div>
        </div>
        <div style={{ marginLeft:"auto", fontSize:9, color:"#1e3a5a", letterSpacing:1 }}>DATA AS OF Q1 2025 · NOT FINANCIAL ADVICE</div>
      </div>

      <div style={{ display:"flex", height:"calc(100vh - 69px)" }}>

        {/* LEFT SIDEBAR */}
        <div style={{ width:186, background:"#0a1220", borderRight:"1px solid #1a2e4a", overflowY:"auto", flexShrink:0 }}>
          <div style={{ padding:"10px 12px 6px", fontSize:9, color:"#2a5070", letterSpacing:2, fontWeight:600 }}>WATCHLIST</div>
          {stocks.map(s => (
            <button key={s.ticker} className={`stock-btn ${selected===s.ticker?"active":""}`} onClick={() => { setSelected(s.ticker); setView("overview"); }}
              style={{ width:"100%", textAlign:"left", padding:"10px 12px", borderLeft:"3px solid transparent", borderBottom:"1px solid #0f1e30", display:"flex", flexDirection:"column", gap:3 }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                <span style={{ fontFamily:"'Syne',sans-serif", fontWeight:800, fontSize:13, color:selected===s.ticker?"#00e5a0":"#a0c4d8" }}>{s.ticker}</span>
                <span style={{ fontSize:9, padding:"1px 5px", borderRadius:3, background:ratingBg(parseFloat(avgScore(s))), color:ratingColor(parseFloat(avgScore(s))), fontWeight:600 }}>{avgScore(s)}</span>
              </div>
              <div style={{ display:"flex", justifyContent:"space-between" }}>
                <span style={{ fontSize:9, color:"#3a6080" }}>{s.sector}</span>
                <span style={{ fontSize:9, color:"#00e5a0", fontWeight:600 }}>{s.upside}</span>
              </div>
            </button>
          ))}
        </div>

        {/* MAIN CONTENT */}
        <div style={{ flex:1, overflowY:"auto", padding:"20px 24px" }}>
          {stock && (
            <div className="fade-in" key={stock.ticker}>

              {/* Stock header */}
              <div style={{ display:"flex", alignItems:"flex-start", gap:18, marginBottom:18 }}>
                <div style={{ flex:1 }}>
                  <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:4, flexWrap:"wrap" }}>
                    <span style={{ fontFamily:"'Syne',sans-serif", fontSize:28, fontWeight:800, color:"#fff", letterSpacing:-1 }}>{stock.ticker}</span>
                    <span style={{ fontSize:9, padding:"3px 8px", borderRadius:4, background:"rgba(110,231,247,0.10)", color:"#6ee7f7", letterSpacing:1 }}>{stock.sector.toUpperCase()}</span>
                    <span style={{ fontSize:10, padding:"3px 8px", borderRadius:4, background:ratingBg(5), color:ratingColor(5), fontWeight:700 }}>{stock.consensus.toUpperCase()}</span>
                    <span style={{ fontSize:9, padding:"3px 8px", borderRadius:4, background:"rgba(255,255,255,0.04)", color:"#5a8aaa" }}>β {stock.beta}</span>
                  </div>
                  <div style={{ fontSize:11, color:"#5a8aaa", marginBottom:8 }}>{stock.name}</div>
                  <div style={{ fontSize:10.5, color:"#6a9cbc", lineHeight:1.7, maxWidth:600 }}>{stock.description}</div>
                </div>
                {/* Key stats grid */}
                <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:1, background:"#1a2e4a", borderRadius:10, overflow:"hidden", flexShrink:0, minWidth:210 }}>
                  {[["PRICE",stock.price,"#c8dff0"],["MKT CAP",stock.marketCap,"#c8dff0"],["FWD P/E",stock.pe+"x","#6ee7f7"],["UPSIDE",stock.upside,"#00e5a0"],["INDICATORS",indicatorComposite(stock)+" ✓","#f5c842"],["AVG RATING",avgScore(stock)+" / 5","#00e5a0"]].map(([label,val,col]) => (
                    <div key={label} style={{ background:"#0d1828", padding:"9px 12px" }}>
                      <div style={{ fontSize:7, color:"#2a5070", letterSpacing:2, marginBottom:2 }}>{label}</div>
                      <div style={{ fontSize:13, fontWeight:600, color:col }}>{val}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Tabs */}
              <div style={{ display:"flex", gap:1, marginBottom:16, borderBottom:"1px solid #1a2e4a", paddingBottom:0 }}>
                {["overview","indicators","investors","table"].map(t => (
                  <button key={t} className="tab-btn" onClick={() => setView(t)}
                    style={{ background:"none", border:"none", cursor:"pointer", padding:"7px 14px", fontSize:9, letterSpacing:2, fontFamily:"inherit",
                      color:view===t?"#00e5a0":"#3a6080", borderBottom:view===t?"2px solid #00e5a0":"2px solid transparent", fontWeight:view===t?600:400 }}>
                    {t==="overview"?"RATINGS":t==="indicators"?"INDICATORS":t==="investors"?"SMART MONEY":"SOURCE TABLE"}
                  </button>
                ))}
              </div>

              {/* RATINGS TAB */}
              {view==="overview" && (
                <div>
                  <div style={{ background:"#0d1828", borderRadius:10, padding:"18px 20px", border:"1px solid #1a2e4a", marginBottom:14 }}>
                    <div style={{ fontSize:9, color:"#2a5070", letterSpacing:2, marginBottom:14 }}>ANALYST CONSENSUS BY SOURCE</div>
                    <div style={{ display:"flex", flexDirection:"column", gap:9 }}>
                      {sources.map(src => {
                        const r = stock.ratings[src];
                        const pct = (r.score/5)*100;
                        return (
                          <div key={src} style={{ display:"flex", alignItems:"center", gap:10 }}>
                            <div style={{ width:90, fontSize:9, color:"#5a8aaa", textAlign:"right", flexShrink:0 }}>{src}</div>
                            <div style={{ flex:1, height:20, background:"#0a1420", borderRadius:4, overflow:"hidden", position:"relative" }}>
                              <div className="bar-anim" style={{ "--w":pct+"%", height:"100%", background:`linear-gradient(90deg,${ratingColor(r.score)}22,${ratingColor(r.score)}88)`, borderRadius:4, width:pct+"%" }}></div>
                              <div style={{ position:"absolute", left:8, top:0, height:"100%", display:"flex", alignItems:"center", fontSize:8.5, color:ratingColor(r.score), fontWeight:600, letterSpacing:0.5 }}>{r.rating}</div>
                            </div>
                            <div style={{ width:22, height:22, borderRadius:4, display:"flex", alignItems:"center", justifyContent:"center", fontSize:10, fontWeight:700, background:ratingBg(r.score), color:ratingColor(r.score) }}>{r.score}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:8 }}>
                    {[{label:"Strong Buy",count:Object.values(stock.ratings).filter(r=>r.score===5).length,color:"#00e5a0"},{label:"Buy",count:Object.values(stock.ratings).filter(r=>r.score===4).length,color:"#6ee7f7"},{label:"Hold",count:Object.values(stock.ratings).filter(r=>r.score===3).length,color:"#f5c842"},{label:"Sell",count:Object.values(stock.ratings).filter(r=>r.score<=2).length,color:"#ff6b6b"}].map(item => (
                      <div key={item.label} style={{ background:"#0d1828", border:"1px solid #1a2e4a", borderRadius:10, padding:"14px 12px", textAlign:"center" }}>
                        <div className="score-pop" style={{ fontSize:26, fontFamily:"'Syne',sans-serif", fontWeight:800, color:item.color }}>{item.count}</div>
                        <div style={{ fontSize:8, color:"#3a6080", letterSpacing:2, marginTop:4 }}>{item.label.toUpperCase()}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* INDICATORS TAB */}
              {view==="indicators" && (
                <div>
                  <div style={{ fontSize:9, color:"#2a5070", letterSpacing:2, marginBottom:12 }}>
                    KEY FINANCIAL INDICATORS — COMPARED TO SECTOR AVERAGE
                  </div>
                  <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>
                    {Object.entries(stock.indicators).map(([key, ind]) => {
                      const score = indicatorScore(ind, key);
                      const barPct = indicatorBarPct(ind, key);
                      const sectorBarPct = indicatorBarPct({ value: ind.sector_avg }, key);
                      const good = score === "good";
                      return (
                        <div key={key} className="indicator-card" style={{
                          background:"#0d1828", borderRadius:10, padding:"14px 16px",
                          border:`1px solid ${good?"rgba(0,229,160,0.15)":"rgba(245,200,66,0.12)"}`,
                          transition:"border-color 0.2s",
                        }}>
                          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:8 }}>
                            <div style={{ fontSize:9, color:"#4a7a9b", letterSpacing:1 }}>{ind.label.toUpperCase()}</div>
                            <div style={{ fontSize:8, padding:"2px 6px", borderRadius:3, background:good?"rgba(0,229,160,0.12)":"rgba(245,200,66,0.12)", color:good?"#00e5a0":"#f5c842", fontWeight:600 }}>
                              {good ? "▲ ABOVE AVG" : "▼ BELOW AVG"}
                            </div>
                          </div>
                          <div style={{ display:"flex", alignItems:"baseline", gap:8, marginBottom:8 }}>
                            <span style={{ fontSize:22, fontFamily:"'Syne',sans-serif", fontWeight:800, color:good?"#00e5a0":"#f5c842" }}>{ind.value}{key==="roe"||key==="grossMargin"||key==="revenueGrowth"?"%":""}</span>
                            <span style={{ fontSize:9, color:"#2a5070" }}>vs {ind.sector_avg}{key==="roe"||key==="grossMargin"||key==="revenueGrowth"?"%":""} sector</span>
                          </div>
                          {/* Dual bar: value vs sector */}
                          <div style={{ display:"flex", flexDirection:"column", gap:3, marginBottom:8 }}>
                            <div style={{ display:"flex", alignItems:"center", gap:6 }}>
                              <div style={{ width:38, fontSize:8, color:"#4a7a9b", textAlign:"right" }}>{stock.ticker}</div>
                              <div style={{ flex:1, height:6, background:"#0a1420", borderRadius:3, overflow:"hidden" }}>
                                <div style={{ width:barPct+"%", height:"100%", background:good?"#00e5a0":"#f5c842", borderRadius:3, transition:"width 0.6s" }}></div>
                              </div>
                            </div>
                            <div style={{ display:"flex", alignItems:"center", gap:6 }}>
                              <div style={{ width:38, fontSize:8, color:"#2a5070", textAlign:"right" }}>Sector</div>
                              <div style={{ flex:1, height:6, background:"#0a1420", borderRadius:3, overflow:"hidden" }}>
                                <div style={{ width:sectorBarPct+"%", height:"100%", background:"rgba(110,231,247,0.3)", borderRadius:3 }}></div>
                              </div>
                            </div>
                          </div>
                          <div style={{ fontSize:9, color:"#3a6080", lineHeight:1.5 }}>{ind.note}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* SMART MONEY / INVESTORS TAB */}
              {view==="investors" && (
                <div>
                  <div style={{ fontSize:9, color:"#2a5070", letterSpacing:2, marginBottom:12 }}>
                    NOTABLE INVESTORS & INSTITUTIONAL POSITIONS
                  </div>
                  <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>
                    {stock.bigInvestors.map((inv, i) => (
                      <div key={i} className="investor-card" style={{
                        background:"#0d1828", borderRadius:10, padding:"16px 18px",
                        border:"1px solid #1a2e4a", transition:"all 0.2s", cursor:"default",
                      }}>
                        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:8 }}>
                          <div>
                            <div style={{ fontFamily:"'Syne',sans-serif", fontWeight:800, fontSize:14, color:"#c8dff0", marginBottom:2 }}>{inv.name}</div>
                            <div style={{ fontSize:9, color:"#3a6080", letterSpacing:1 }}>{inv.firm}</div>
                          </div>
                          <div style={{ fontSize:9, padding:"3px 8px", borderRadius:4, background:"rgba(0,229,160,0.08)", color:stanceColor(inv.stance), fontWeight:600, textAlign:"right", maxWidth:100, lineHeight:1.3 }}>
                            {inv.stance.toUpperCase()}
                          </div>
                        </div>
                        <div style={{ fontSize:10, color:"#5a8aaa", lineHeight:1.6, borderTop:"1px solid #111e2e", paddingTop:10 }}>
                          {inv.note}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div style={{ marginTop:12, padding:"12px 14px", background:"#0a1220", borderRadius:8, border:"1px solid #0f1e30" }}>
                    <div style={{ fontSize:8, color:"#1e3a5a", lineHeight:1.8 }}>
                      ℹ Position data derived from 13F filings, public statements, and fund disclosures as of Q1 2025. Positions may have changed. This does not constitute investment advice.
                    </div>
                  </div>
                </div>
              )}

              {/* SOURCE TABLE TAB */}
              {view==="table" && (
                <div style={{ background:"#0d1828", borderRadius:10, border:"1px solid #1a2e4a", overflow:"hidden" }}>
                  <table style={{ width:"100%", borderCollapse:"collapse", fontSize:10.5 }}>
                    <thead>
                      <tr style={{ background:"#091220", borderBottom:"2px solid #1a2e4a" }}>
                        <th style={{ padding:"11px 14px", textAlign:"left", color:"#2a5070", fontSize:8, letterSpacing:2 }}>SOURCE</th>
                        <th style={{ padding:"11px 14px", textAlign:"center", color:"#2a5070", fontSize:8, letterSpacing:2 }}>RATING</th>
                        <th style={{ padding:"11px 14px", textAlign:"center", color:"#2a5070", fontSize:8, letterSpacing:2 }}>SCORE</th>
                        <th style={{ padding:"11px 14px", textAlign:"left", color:"#2a5070", fontSize:8, letterSpacing:2 }}>METHODOLOGY</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sources.map(src => {
                        const r = stock.ratings[src];
                        return (
                          <tr key={src} className="source-row" style={{ borderBottom:"1px solid #111e2e" }}>
                            <td style={{ padding:"12px 14px", color:"#7aaac0", fontWeight:500 }}>{src}</td>
                            <td style={{ padding:"12px 14px", textAlign:"center" }}>
                              <span className="rating-pill" style={{ padding:"3px 9px", borderRadius:4, background:ratingBg(r.score), color:ratingColor(r.score), fontWeight:600, fontSize:9 }}>{r.rating}</span>
                            </td>
                            <td style={{ padding:"12px 14px", textAlign:"center" }}>
                              <span style={{ color:ratingColor(r.score), fontWeight:700, fontSize:14 }}>{r.score}</span>
                              <span style={{ color:"#2a5070", fontSize:9 }}>/5</span>
                            </td>
                            <td style={{ padding:"12px 14px", color:"#3a6080", fontSize:9, lineHeight:1.5 }}>{sourceNotes[src]}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}

            </div>
          )}
        </div>

        {/* RIGHT PANEL */}
        <div style={{ width:206, background:"#0a1220", borderLeft:"1px solid #1a2e4a", overflowY:"auto", flexShrink:0, padding:"12px 0" }}>
          <div style={{ padding:"0 12px 8px", fontSize:9, color:"#2a5070", letterSpacing:2, fontWeight:600 }}>ALL STOCKS</div>
          {stocks.map(s => (
            <div key={s.ticker} onClick={() => { setSelected(s.ticker); setView("overview"); }}
              style={{ padding:"9px 12px", borderBottom:"1px solid #0f1e30", cursor:"pointer", background:selected===s.ticker?"rgba(0,229,160,0.06)":"transparent", transition:"background 0.15s" }}>
              <div style={{ display:"flex", justifyContent:"space-between", marginBottom:5 }}>
                <span style={{ fontFamily:"'Syne',sans-serif", fontWeight:800, fontSize:12, color:selected===s.ticker?"#00e5a0":"#8ab0c8" }}>{s.ticker}</span>
                <span style={{ fontSize:9, color:"#00e5a0", fontWeight:700 }}>{s.upside}</span>
              </div>
              <div style={{ display:"flex", gap:2, flexWrap:"wrap", marginBottom:4 }}>
                {sources.map(src => (
                  <div key={src} title={`${src}: ${s.ratings[src].rating}`}
                    style={{ width:15, height:15, borderRadius:2, background:ratingColor(s.ratings[src].score)+"44", border:`1px solid ${ratingColor(s.ratings[src].score)}33`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:7, color:ratingColor(s.ratings[src].score) }}>
                    {s.ratings[src].score}
                  </div>
                ))}
              </div>
              <div style={{ display:"flex", gap:8 }}>
                <span style={{ fontSize:8, color:"#2a4a6a" }}>P/E {s.pe}x</span>
                <span style={{ fontSize:8, color:"#2a4a6a" }}>β {s.beta}</span>
                <span style={{ fontSize:8, color:"#1a3a5a" }}>{indicatorComposite(s)} ind✓</span>
              </div>
            </div>
          ))}
          <div style={{ padding:"12px", marginTop:6 }}>
            <div style={{ fontSize:7.5, color:"#1a3a5a", lineHeight:1.7 }}>
              ⚠ Not financial advice. Ratings & indicators as of Q1 2025. Verify all data before making investment decisions.
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
</script>
</body>
</html>
