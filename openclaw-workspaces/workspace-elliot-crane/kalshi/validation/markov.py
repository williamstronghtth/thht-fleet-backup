"""
Markov Chain State Model
========================

Models how prediction market prices transition between states.

States:
- LOW: Price < 30%
- MID: 30% <= Price <= 70%
- HIGH: Price > 70%
- RESOLVED_YES: Settled YES
- RESOLVED_NO: Settled NO

Use cases:
1. Predict probability of reaching resolution state from current state
2. Estimate time to resolution
3. Identify optimal entry/exit states
4. Detect anomalous state transitions (potential edge)
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


class MarketState:
    """Market price state categories."""
    LOW = "low"           # < 30%
    MID = "mid"           # 30-70%
    HIGH = "high"         # > 70%
    RESOLVED_YES = "yes"  # Settled YES
    RESOLVED_NO = "no"    # Settled NO
    
    ALL_STATES = [LOW, MID, HIGH, RESOLVED_YES, RESOLVED_NO]
    TRADING_STATES = [LOW, MID, HIGH]
    TERMINAL_STATES = [RESOLVED_YES, RESOLVED_NO]
    
    @staticmethod
    def from_price(price: float) -> str:
        """Convert price to state."""
        if price < 0.30:
            return MarketState.LOW
        elif price > 0.70:
            return MarketState.HIGH
        else:
            return MarketState.MID


@dataclass
class TransitionMatrix:
    """Markov transition probability matrix."""
    matrix: np.ndarray
    states: List[str]
    n_observations: int
    
    def get_probability(self, from_state: str, to_state: str) -> float:
        """Get transition probability from one state to another."""
        i = self.states.index(from_state)
        j = self.states.index(to_state)
        return self.matrix[i, j]
    
    def get_resolution_probability(self, current_state: str, 
                                    resolution: str = "yes") -> float:
        """
        Calculate probability of reaching resolution state from current state.
        
        Uses matrix exponentiation to handle multi-step transitions.
        """
        if current_state in MarketState.TERMINAL_STATES:
            return 1.0 if current_state == resolution else 0.0
        
        # Solve for absorbing state probabilities
        # For a simple approach, we'll use simulation
        n_sims = 1000  # Reduced for speed
        reached_resolution = 0
        
        for _ in range(n_sims):
            state = current_state
            steps = 0
            max_steps = 50
            
            while state in MarketState.TRADING_STATES and steps < max_steps:
                # Sample next state based on transition probabilities
                i = self.states.index(state)
                probs = self.matrix[i]
                state = np.random.choice(self.states, p=probs)
                steps += 1
            
            # Check resolution
            if resolution == "yes" and state == MarketState.RESOLVED_YES:
                reached_resolution += 1
            elif resolution == "no" and state == MarketState.RESOLVED_NO:
                reached_resolution += 1
        
        return reached_resolution / n_sims
    
    def expected_steps_to_resolution(self, current_state: str) -> float:
        """Estimate expected number of steps to reach any terminal state."""
        if current_state in MarketState.TERMINAL_STATES:
            return 0
        
        n_sims = 500  # Reduced for speed
        total_steps = 0
        
        for _ in range(n_sims):
            state = current_state
            steps = 0
            max_steps = 50
            
            while state in MarketState.TRADING_STATES and steps < max_steps:
                i = self.states.index(state)
                probs = self.matrix[i]
                state = np.random.choice(self.states, p=probs)
                steps += 1
            
            total_steps += steps
        
        return total_steps / n_sims
    
    def __str__(self):
        lines = [
            "Transition Matrix",
            "=" * 50,
            f"Observations: {self.n_observations}",
            "",
            f"{'From/To':<12}" + "".join(f"{s:>10}" for s in self.states),
            "-" * 62,
        ]
        
        for i, from_state in enumerate(self.states):
            row = f"{from_state:<12}"
            for j in range(len(self.states)):
                prob = self.matrix[i, j]
                row += f"{prob:>10.1%}"
            lines.append(row)
        
        return "\n".join(lines)


@dataclass
class MarkovAnalysis:
    """Complete Markov analysis results."""
    transition_matrix: TransitionMatrix
    
    # Resolution probabilities from each trading state
    prob_yes_from_low: float
    prob_yes_from_mid: float
    prob_yes_from_high: float
    
    # Expected steps to resolution
    steps_from_low: float
    steps_from_mid: float
    steps_from_high: float
    
    # Optimal entry recommendations
    best_entry_for_yes: str
    best_entry_for_no: str
    
    def __str__(self):
        return f"""
{self.transition_matrix}

Resolution Probabilities (YES outcome)
{'='*50}
  From LOW state:  {self.prob_yes_from_low:>6.1%}
  From MID state:  {self.prob_yes_from_mid:>6.1%}
  From HIGH state: {self.prob_yes_from_high:>6.1%}

Expected Steps to Resolution
{'='*50}
  From LOW:  {self.steps_from_low:>5.1f} price updates
  From MID:  {self.steps_from_mid:>5.1f} price updates
  From HIGH: {self.steps_from_high:>5.1f} price updates

Optimal Entry Points
{'='*50}
  For YES bets: Enter at {self.best_entry_for_yes.upper()} state
  For NO bets:  Enter at {self.best_entry_for_no.upper()} state
"""


class MarkovModel:
    """
    Markov chain model for prediction market price transitions.
    """
    
    def __init__(self):
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi')
        self.price_history_dir = self.data_dir / 'price_history'
        self.results_dir = self.data_dir / 'validation/results'
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Default transition matrix (can be learned from data)
        # Based on typical prediction market behavior
        self.default_matrix = np.array([
            # LOW    MID    HIGH   YES    NO
            [0.60,  0.30,  0.05,  0.02,  0.03],  # from LOW
            [0.15,  0.55,  0.18,  0.06,  0.06],  # from MID
            [0.03,  0.15,  0.60,  0.20,  0.02],  # from HIGH
            [0.00,  0.00,  0.00,  1.00,  0.00],  # from YES (absorbing)
            [0.00,  0.00,  0.00,  0.00,  1.00],  # from NO (absorbing)
        ])
    
    def load_price_history(self, ticker: str = None) -> List[Dict]:
        """Load price history for learning transitions."""
        histories = []
        
        if ticker:
            # Load specific ticker
            price_file = self.price_history_dir / f'{ticker}.jsonl'
            if price_file.exists():
                with open(price_file) as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            # Only include entries that look like price history
                            if 'price' in entry or 'ticker' in entry:
                                histories.append(entry)
        else:
            # Load all price histories - but only valid entries
            if self.price_history_dir.exists():
                for price_file in self.price_history_dir.glob('*.jsonl'):
                    # Skip non-price files
                    if 'history' not in price_file.name and 'scan' in price_file.name:
                        continue
                    with open(price_file) as f:
                        for line in f:
                            if line.strip():
                                entry = json.loads(line)
                                # Only include entries with price data
                                if 'price' in entry or ('ticker' in entry and 'outcome' in entry):
                                    histories.append(entry)
        
        return histories
    
    def learn_transitions(self, histories: List[Dict]) -> TransitionMatrix:
        """
        Learn transition probabilities from price history.
        
        Each history entry should have: timestamp, price, (optional) outcome
        """
        states = MarketState.ALL_STATES
        n_states = len(states)
        
        # Count transitions
        counts = np.zeros((n_states, n_states))
        
        # Group by market
        by_market = defaultdict(list)
        for h in histories:
            ticker = h.get('ticker', 'unknown')
            by_market[ticker].append(h)
        
        for ticker, market_history in by_market.items():
            # Sort by timestamp
            sorted_history = sorted(market_history, key=lambda x: x.get('timestamp', ''))
            
            prev_state = None
            
            for entry in sorted_history:
                price = entry.get('price', 0.5)
                outcome = entry.get('outcome')
                
                # Determine current state
                if outcome == 'yes':
                    current_state = MarketState.RESOLVED_YES
                elif outcome == 'no':
                    current_state = MarketState.RESOLVED_NO
                else:
                    current_state = MarketState.from_price(price)
                
                # Record transition
                if prev_state is not None:
                    i = states.index(prev_state)
                    j = states.index(current_state)
                    counts[i, j] += 1
                
                prev_state = current_state
        
        # Convert counts to probabilities
        matrix = np.zeros((n_states, n_states))
        
        for i in range(n_states):
            row_sum = counts[i].sum()
            if row_sum > 0:
                matrix[i] = counts[i] / row_sum
            else:
                # Use default for states with no observations
                matrix[i] = self.default_matrix[i]
        
        return TransitionMatrix(
            matrix=matrix,
            states=states,
            n_observations=int(counts.sum()),
        )
    
    def analyze(self, ticker: str = None) -> MarkovAnalysis:
        """
        Run full Markov analysis.
        """
        histories = self.load_price_history(ticker)
        
        if len(histories) < 10:
            # Use default matrix if insufficient data
            matrix = TransitionMatrix(
                matrix=self.default_matrix,
                states=MarketState.ALL_STATES,
                n_observations=0,
            )
        else:
            matrix = self.learn_transitions(histories)
        
        # Calculate resolution probabilities
        prob_yes_low = matrix.get_resolution_probability(MarketState.LOW, "yes")
        prob_yes_mid = matrix.get_resolution_probability(MarketState.MID, "yes")
        prob_yes_high = matrix.get_resolution_probability(MarketState.HIGH, "yes")
        
        # Expected steps
        steps_low = matrix.expected_steps_to_resolution(MarketState.LOW)
        steps_mid = matrix.expected_steps_to_resolution(MarketState.MID)
        steps_high = matrix.expected_steps_to_resolution(MarketState.HIGH)
        
        # Optimal entry points
        # For YES bets: enter where prob_yes is high relative to price
        # LOW state = cheap (< 30%) but prob_yes might be low
        # Need to compare edge: prob_yes - state_price
        
        yes_edge_low = prob_yes_low - 0.15  # Midpoint of LOW state
        yes_edge_mid = prob_yes_mid - 0.50  # Midpoint of MID state
        yes_edge_high = prob_yes_high - 0.85  # Midpoint of HIGH state
        
        yes_edges = {
            MarketState.LOW: yes_edge_low,
            MarketState.MID: yes_edge_mid,
            MarketState.HIGH: yes_edge_high,
        }
        
        best_entry_yes = max(yes_edges, key=yes_edges.get)
        
        # For NO bets: inverse
        no_edges = {
            MarketState.LOW: (1 - prob_yes_low) - 0.85,
            MarketState.MID: (1 - prob_yes_mid) - 0.50,
            MarketState.HIGH: (1 - prob_yes_high) - 0.15,
        }
        
        best_entry_no = max(no_edges, key=no_edges.get)
        
        analysis = MarkovAnalysis(
            transition_matrix=matrix,
            prob_yes_from_low=prob_yes_low,
            prob_yes_from_mid=prob_yes_mid,
            prob_yes_from_high=prob_yes_high,
            steps_from_low=steps_low,
            steps_from_mid=steps_mid,
            steps_from_high=steps_high,
            best_entry_for_yes=best_entry_yes,
            best_entry_for_no=best_entry_no,
        )
        
        # Save analysis
        self._save_analysis(analysis)
        
        return analysis
    
    def _save_analysis(self, analysis: MarkovAnalysis):
        """Save analysis to file."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        result_file = self.results_dir / f'markov_{timestamp}.json'
        
        result_dict = {
            'timestamp': timestamp,
            'transition_matrix': {
                'matrix': analysis.transition_matrix.matrix.tolist(),
                'states': analysis.transition_matrix.states,
                'n_observations': analysis.transition_matrix.n_observations,
            },
            'resolution_probabilities': {
                'from_low': analysis.prob_yes_from_low,
                'from_mid': analysis.prob_yes_from_mid,
                'from_high': analysis.prob_yes_from_high,
            },
            'expected_steps': {
                'from_low': analysis.steps_from_low,
                'from_mid': analysis.steps_from_mid,
                'from_high': analysis.steps_from_high,
            },
            'optimal_entry': {
                'for_yes': analysis.best_entry_for_yes,
                'for_no': analysis.best_entry_for_no,
            },
        }
        
        with open(result_file, 'w') as f:
            json.dump(result_dict, f, indent=2)
    
    def predict_resolution(self, current_price: float) -> Dict:
        """
        Predict resolution probability from current price.
        
        Returns dict with probabilities and confidence.
        """
        analysis = self.analyze()
        
        current_state = MarketState.from_price(current_price)
        
        if current_state == MarketState.LOW:
            prob_yes = analysis.prob_yes_from_low
            steps = analysis.steps_from_low
        elif current_state == MarketState.HIGH:
            prob_yes = analysis.prob_yes_from_high
            steps = analysis.steps_from_high
        else:
            prob_yes = analysis.prob_yes_from_mid
            steps = analysis.steps_from_mid
        
        return {
            'current_state': current_state,
            'current_price': current_price,
            'predicted_prob_yes': prob_yes,
            'predicted_prob_no': 1 - prob_yes,
            'expected_steps': steps,
            'edge_yes': prob_yes - current_price,
            'edge_no': (1 - prob_yes) - (1 - current_price),
        }


def main():
    """CLI for Markov model."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Markov chain price model')
    parser.add_argument('action', choices=['analyze', 'predict', 'matrix'],
                        help='Action to perform')
    parser.add_argument('--ticker', help='Specific ticker to analyze')
    parser.add_argument('--price', type=float, help='Current price for prediction')
    
    args = parser.parse_args()
    
    model = MarkovModel()
    
    if args.action == 'analyze':
        analysis = model.analyze(args.ticker)
        print(analysis)
    
    elif args.action == 'predict':
        if args.price is None:
            print("Error: --price required for predict action")
            return
        
        prediction = model.predict_resolution(args.price)
        
        print(f"Current price: {prediction['current_price']:.0%}")
        print(f"Current state: {prediction['current_state'].upper()}")
        print()
        print(f"Predicted YES probability: {prediction['predicted_prob_yes']:.1%}")
        print(f"Edge for YES: {prediction['edge_yes']*100:+.1f} points")
        print(f"Edge for NO: {prediction['edge_no']*100:+.1f} points")
        print(f"Expected steps to resolution: {prediction['expected_steps']:.1f}")
    
    elif args.action == 'matrix':
        analysis = model.analyze(args.ticker)
        print(analysis.transition_matrix)


if __name__ == '__main__':
    main()
