#!/usr/bin/env node
/**
 * News Digest for Elliot Crane
 * Runs 15 min before each hourly scan (6:45am-9:45pm ET)
 * 
 * Topics: Oil, Middle East, Fed, CPI/GDP/Jobs, Tariffs, Geopolitics, Entertainment
 */

import { Query, QueryExecutor, createRegistry } from '/root/.openclaw/shared/opentypebb/dist/index.js';

const registry = createRegistry();
const executor = new QueryExecutor(registry);

// Elliot's current position to flag
const OPEN_POSITIONS = {
  'March CPI': { threshold: 0.7, direction: 'above' }
};

const TOPICS = [
  'oil price crude brent WTI',
  'Iran Middle East Hormuz',
  'Federal Reserve Fed rate FOMC',
  'CPI inflation GDP jobs employment',
  'tariff trade policy',
  'geopolitical war conflict',
  'Oscars Survivor entertainment awards'
];

async function getOilPrices() {
  try {
    // WTI Crude
    const wti = new Query(executor, {
      provider: 'yfinance',
      model: 'EquityQuote',
      params: { symbol: 'CL=F' },
      credentials: null
    });
    const wtiResult = await wti.execute();
    
    // Brent Crude  
    const brent = new Query(executor, {
      provider: 'yfinance',
      model: 'EquityQuote',
      params: { symbol: 'BZ=F' },
      credentials: null
    });
    const brentResult = await brent.execute();
    
    // Gas prices (RBOB Gasoline)
    const gas = new Query(executor, {
      provider: 'yfinance',
      model: 'EquityQuote',
      params: { symbol: 'RB=F' },
      credentials: null
    });
    const gasResult = await gas.execute();
    
    return {
      wti: wtiResult.results?.[0]?.last_price || 'N/A',
      wtiChange: wtiResult.results?.[0]?.change_percent || 0,
      brent: brentResult.results?.[0]?.last_price || 'N/A',
      brentChange: brentResult.results?.[0]?.change_percent || 0,
      gasoline: gasResult.results?.[0]?.last_price || 'N/A'
    };
  } catch (e) {
    console.error('Oil price fetch error:', e.message);
    return { wti: 'N/A', brent: 'N/A', gasoline: 'N/A', wtiChange: 0, brentChange: 0 };
  }
}

async function getMarketNews() {
  try {
    // Get general market news
    const newsSymbols = ['SPY', 'USO', 'XLE'];
    const allNews = [];
    
    for (const symbol of newsSymbols) {
      const query = new Query(executor, {
        provider: 'yfinance',
        model: 'CompanyNews',
        params: { symbol },
        credentials: null
      });
      const result = await query.execute();
      if (result.results) {
        allNews.push(...result.results);
      }
    }
    
    // Dedupe and sort by date
    const seen = new Set();
    const unique = allNews.filter(n => {
      const key = n.title?.slice(0, 50);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
    
    return unique.slice(0, 20);
  } catch (e) {
    console.error('News fetch error:', e.message);
    return [];
  }
}

function filterRelevantNews(news) {
  const keywords = [
    'oil', 'crude', 'brent', 'wti', 'opec', 'energy',
    'iran', 'middle east', 'hormuz', 'israel', 'gaza', 'saudi',
    'fed', 'federal reserve', 'rate', 'fomc', 'powell', 'inflation',
    'cpi', 'gdp', 'jobs', 'employment', 'labor', 'economic',
    'tariff', 'trade', 'china', 'import', 'export',
    'war', 'conflict', 'geopolitical', 'sanction',
    'oscar', 'survivor', 'emmy', 'grammy', 'award', 'entertainment'
  ];
  
  return news.filter(item => {
    const text = `${item.title || ''} ${item.text || ''}`.toLowerCase();
    return keywords.some(kw => text.includes(kw));
  });
}

function formatDigest(oilPrices, news, timestamp) {
  const lines = [];
  
  lines.push(`📰 **HOURLY NEWS DIGEST**`);
  lines.push(`🕐 ${timestamp}`);
  lines.push('');
  
  // Oil prices section
  lines.push(`⛽ **ENERGY PRICES** _(indicative, verify for trades)_`);
  lines.push(`• WTI Crude: ~$${oilPrices.wti?.toFixed(2) || 'N/A'} (${oilPrices.wtiChange > 0 ? '+' : ''}${(oilPrices.wtiChange * 100)?.toFixed(2) || 0}%)`);
  lines.push(`• Brent Crude: ~$${oilPrices.brent?.toFixed(2) || 'N/A'} (${oilPrices.brentChange > 0 ? '+' : ''}${(oilPrices.brentChange * 100)?.toFixed(2) || 0}%)`);
  lines.push(`• RBOB Gasoline: ~$${oilPrices.gasoline?.toFixed(2) || 'N/A'}/gal`);
  lines.push('');
  
  // Check for oil spike alert
  if (Math.abs(oilPrices.wtiChange) > 0.05 || Math.abs(oilPrices.brentChange) > 0.05) {
    lines.push(`🚨 **OIL SPIKE ALERT**: ${Math.abs(oilPrices.wtiChange) > 0.05 ? 'WTI' : 'Brent'} moved ${(Math.max(Math.abs(oilPrices.wtiChange), Math.abs(oilPrices.brentChange)) * 100).toFixed(1)}%!`);
    lines.push('');
  }
  
  // Top headlines
  lines.push(`📋 **TOP HEADLINES**`);
  const topNews = news.slice(0, 5);
  if (topNews.length === 0) {
    lines.push('• No major news in tracked topics this hour');
  } else {
    topNews.forEach((item, i) => {
      const title = item.title || 'Untitled';
      const summary = item.text?.slice(0, 100) || '';
      lines.push(`${i + 1}. ${title}`);
      if (summary) lines.push(`   ↳ ${summary}...`);
    });
  }
  lines.push('');
  
  // Position flags
  lines.push(`📊 **POSITION WATCH**`);
  lines.push(`• March CPI >0.7%: Watching for inflation data releases`);
  
  // Check if any news mentions CPI
  const cpiNews = news.filter(n => 
    (n.title + n.text).toLowerCase().includes('cpi') ||
    (n.title + n.text).toLowerCase().includes('inflation')
  );
  if (cpiNews.length > 0) {
    lines.push(`⚠️ CPI/Inflation mentioned in ${cpiNews.length} headline(s) - review above`);
  }
  
  return lines.join('\n');
}

async function main() {
  const now = new Date();
  const timestamp = now.toLocaleString('en-US', { 
    timeZone: 'America/New_York',
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
  
  console.log(`Fetching news digest at ${timestamp}...`);
  
  // Fetch data
  const [oilPrices, news] = await Promise.all([
    getOilPrices(),
    getMarketNews()
  ]);
  
  // Filter relevant news
  const relevantNews = filterRelevantNews(news);
  
  // Format digest
  const digest = formatDigest(oilPrices, relevantNews, timestamp);
  
  console.log('\n' + digest);
  
  // Return for cron to send
  return digest;
}

main().catch(console.error);
