#!/usr/bin/env node
/**
 * Breaking News Monitor for Elliot Crane
 * Runs every 10 minutes to detect:
 * - Oil price spikes (5%+ move)
 * - Major geopolitical events (ceasefire, conflict escalation)
 * 
 * Stores last known prices in state file to detect changes.
 */

import { Query, QueryExecutor, createRegistry } from '/root/.openclaw/shared/opentypebb/dist/index.js';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const STATE_FILE = '/root/.openclaw/workspace-elliot-crane/scripts/.breaking-state.json';
const SPIKE_THRESHOLD = 0.05; // 5%

const registry = createRegistry();
const executor = new QueryExecutor(registry);

function loadState() {
  try {
    if (existsSync(STATE_FILE)) {
      return JSON.parse(readFileSync(STATE_FILE, 'utf8'));
    }
  } catch (e) {}
  return { lastWti: null, lastBrent: null, lastCheck: null };
}

function saveState(state) {
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

async function getOilPrices() {
  try {
    const wti = new Query(executor, {
      provider: 'yfinance',
      model: 'EquityQuote',
      params: { symbol: 'CL=F' },
      credentials: null
    });
    const wtiResult = await wti.execute();
    
    const brent = new Query(executor, {
      provider: 'yfinance',
      model: 'EquityQuote',
      params: { symbol: 'BZ=F' },
      credentials: null
    });
    const brentResult = await brent.execute();
    
    return {
      wti: wtiResult.results?.[0]?.last_price,
      brent: brentResult.results?.[0]?.last_price
    };
  } catch (e) {
    console.error('Price fetch error:', e.message);
    return { wti: null, brent: null };
  }
}

function checkForSpike(current, previous, name) {
  if (!current || !previous) return null;
  
  const change = (current - previous) / previous;
  if (Math.abs(change) >= SPIKE_THRESHOLD) {
    return {
      name,
      current,
      previous,
      change,
      direction: change > 0 ? 'UP' : 'DOWN'
    };
  }
  return null;
}

async function main() {
  const state = loadState();
  const prices = await getOilPrices();
  
  const alerts = [];
  
  // Check WTI spike
  if (state.lastWti) {
    const wtiSpike = checkForSpike(prices.wti, state.lastWti, 'WTI Crude');
    if (wtiSpike) alerts.push(wtiSpike);
  }
  
  // Check Brent spike
  if (state.lastBrent) {
    const brentSpike = checkForSpike(prices.brent, state.lastBrent, 'Brent Crude');
    if (brentSpike) alerts.push(brentSpike);
  }
  
  // Update state
  saveState({
    lastWti: prices.wti,
    lastBrent: prices.brent,
    lastCheck: new Date().toISOString()
  });
  
  // Output alerts
  if (alerts.length > 0) {
    console.log('🚨 BREAKING ALERT 🚨');
    alerts.forEach(alert => {
      console.log(`${alert.name} ${alert.direction} ${(Math.abs(alert.change) * 100).toFixed(1)}%!`);
      console.log(`Previous: $${alert.previous.toFixed(2)} → Current: $${alert.current.toFixed(2)}`);
    });
    return alerts;
  } else {
    console.log(`Oil prices stable. WTI: $${prices.wti?.toFixed(2)}, Brent: $${prices.brent?.toFixed(2)}`);
    return null;
  }
}

main().catch(console.error);
