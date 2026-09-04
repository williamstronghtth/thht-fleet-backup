#!/usr/bin/env node
/**
 * Trading News Digest for Oliver Kensington
 * Runs hourly during market hours
 * 
 * Focus: Company news, market movers, sector trends, macro headlines
 */

import { Query, QueryExecutor, createRegistry } from '/root/.openclaw/shared/opentypebb/dist/index.js';

const registry = createRegistry();
const executor = new QueryExecutor(registry);

// Watchlist - can be updated
const WATCHLIST = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'META', 'GOOGL', 'AMZN', 'SPY', 'QQQ'];

async function getMarketMovers() {
  const results = { gainers: [], losers: [], active: [] };
  
  try {
    // Top gainers
    const gainers = new Query(executor, {
      provider: 'yfinance',
      model: 'EquityGainers',
      params: {},
      credentials: null
    });
    const gainersResult = await gainers.execute();
    results.gainers = (gainersResult.results || []).slice(0, 5);
    
    // Top losers
    const losers = new Query(executor, {
      provider: 'yfinance',
      model: 'EquityLosers',
      params: {},
      credentials: null
    });
    const losersResult = await losers.execute();
    results.losers = (losersResult.results || []).slice(0, 5);
    
    // Most active
    const active = new Query(executor, {
      provider: 'yfinance',
      model: 'EquityActive',
      params: {},
      credentials: null
    });
    const activeResult = await active.execute();
    results.active = (activeResult.results || []).slice(0, 5);
  } catch (e) {
    console.error('Market movers error:', e.message);
  }
  
  return results;
}

async function getWatchlistNews() {
  const allNews = [];
  
  for (const symbol of WATCHLIST.slice(0, 5)) { // Limit API calls
    try {
      const query = new Query(executor, {
        provider: 'yfinance',
        model: 'CompanyNews',
        params: { symbol },
        credentials: null
      });
      const result = await query.execute();
      if (result.results) {
        allNews.push(...result.results.slice(0, 3).map(n => ({ ...n, symbol })));
      }
    } catch (e) {
      // Skip failures
    }
  }
  
  // Sort by date (most recent first) and dedupe
  const seen = new Set();
  return allNews
    .filter(n => {
      const key = n.title?.slice(0, 40);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .slice(0, 10);
}

async function getIndexPrices() {
  const indices = [
    { symbol: 'SPY', name: 'S&P 500' },
    { symbol: 'QQQ', name: 'Nasdaq' },
    { symbol: 'DIA', name: 'Dow' },
    { symbol: 'IWM', name: 'Russell 2K' }
  ];
  
  const prices = [];
  
  for (const idx of indices) {
    try {
      const query = new Query(executor, {
        provider: 'yfinance',
        model: 'EquityQuote',
        params: { symbol: idx.symbol },
        credentials: null
      });
      const result = await query.execute();
      const data = result.results?.[0];
      if (data) {
        const change = ((data.last_price - data.prev_close) / data.prev_close) * 100;
        prices.push({
          name: idx.name,
          symbol: idx.symbol,
          price: data.last_price,
          change: change
        });
      }
    } catch (e) {
      // Skip
    }
  }
  
  return prices;
}

function formatDigest(indices, movers, news, timestamp) {
  const lines = [];
  
  lines.push(`📈 **TRADING NEWS DIGEST**`);
  lines.push(`🕐 ${timestamp}`);
  lines.push('');
  
  // Market indices
  lines.push(`📊 **MARKET SNAPSHOT** _(indicative)_`);
  indices.forEach(idx => {
    const arrow = idx.change >= 0 ? '🟢' : '🔴';
    const sign = idx.change >= 0 ? '+' : '';
    lines.push(`${arrow} ${idx.name}: $${idx.price?.toFixed(2)} (${sign}${idx.change?.toFixed(2)}%)`);
  });
  lines.push('');
  
  // Market movers
  lines.push(`🚀 **TOP GAINERS**`);
  movers.gainers.slice(0, 3).forEach(s => {
    lines.push(`• ${s.symbol}: +${(s.percent_change * 100)?.toFixed(1)}% ($${s.price?.toFixed(2)})`);
  });
  lines.push('');
  
  lines.push(`📉 **TOP LOSERS**`);
  movers.losers.slice(0, 3).forEach(s => {
    lines.push(`• ${s.symbol}: ${(s.percent_change * 100)?.toFixed(1)}% ($${s.price?.toFixed(2)})`);
  });
  lines.push('');
  
  lines.push(`🔥 **MOST ACTIVE**`);
  movers.active.slice(0, 3).forEach(s => {
    const vol = (s.volume / 1000000).toFixed(1);
    lines.push(`• ${s.symbol}: ${vol}M vol ($${s.price?.toFixed(2)})`);
  });
  lines.push('');
  
  // Company news
  lines.push(`📰 **WATCHLIST NEWS**`);
  if (news.length === 0) {
    lines.push('• No major news for watched tickers');
  } else {
    news.slice(0, 5).forEach((item, i) => {
      const ticker = item.symbol ? `[${item.symbol}]` : '';
      lines.push(`${i + 1}. ${ticker} ${item.title}`);
    });
  }
  lines.push('');
  
  // Trading reminders
  lines.push(`⚡ **REMEMBER**`);
  lines.push(`• Verify prices before executing`);
  lines.push(`• Check volume on any trade`);
  
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
  
  console.log(`Fetching trading digest at ${timestamp}...`);
  
  // Fetch all data in parallel
  const [indices, movers, news] = await Promise.all([
    getIndexPrices(),
    getMarketMovers(),
    getWatchlistNews()
  ]);
  
  // Format and output
  const digest = formatDigest(indices, movers, news, timestamp);
  console.log('\n' + digest);
  
  return digest;
}

main().catch(console.error);
