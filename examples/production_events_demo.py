#!/usr/bin/env python3
"""
Demonstration of production event detection in ts-shape.

This script shows how to use:
1. MachineStateEvents (run/idle detection, transitions, rapid transitions)
2. LineThroughputEvents (part counting, takt adherence, OEE)
3. ChangeoverEvents (product changeover detection, changeover windows)
4. FlowConstraintEvents (blocked/starved detection)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import ts_shape
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ts_shape.events.production.machine_state import MachineStateEvents
from ts_shape.events.production.line_throughput import LineThroughputEvents
from ts_shape.events.production.changeover import ChangeoverEvents
from ts_shape.events.production.flow_constraints import FlowConstraintEvents


def create_machine_state_data():
    """Create synthetic machine run/idle state data."""
    start_time = datetime(2024, 1, 1, 6, 0, 0)
    rows = []
    t = start_time
    # Pattern: run 5 min, idle 1 min, run 8 min, idle 2 min, repeat
    pattern = [
        (True, 300),   # run 5 min
        (False, 60),   # idle 1 min
        (True, 480),   # run 8 min
        (False, 120),  # idle 2 min
    ]
    for cycle in range(4):
        for state, duration_secs in pattern:
            for s in range(0, duration_secs, 10):
                rows.append({
                    'systime': t + timedelta(seconds=s),
                    'uuid': 'machine_run_state',
                    'value_bool': state,
                    'is_delta': True,
                })
            t += timedelta(seconds=duration_secs)

    return pd.DataFrame(rows)


def create_throughput_data():
    """Create synthetic part counter and cycle trigger data."""
    start_time = datetime(2024, 1, 1, 8, 0, 0)
    rows = []

    # Monotonically increasing part counter
    counter = 1000
    for i in range(120):
        t = start_time + timedelta(minutes=i)
        counter += np.random.randint(3, 8)
        rows.append({
            'systime': t,
            'uuid': 'part_counter',
            'value_integer': counter,
            'value_bool': None,
            'is_delta': True,
        })

    # Boolean cycle triggers (True at each cycle completion)
    cycle_time_base = 45  # seconds
    t = start_time
    for i in range(150):
        cycle_time = cycle_time_base + np.random.normal(0, 5)
        t += timedelta(seconds=max(20, cycle_time))
        # Rising edge: False then True
        rows.append({
            'systime': t - timedelta(seconds=1),
            'uuid': 'cycle_trigger',
            'value_integer': None,
            'value_bool': False,
            'is_delta': True,
        })
        rows.append({
            'systime': t,
            'uuid': 'cycle_trigger',
            'value_integer': None,
            'value_bool': True,
            'is_delta': True,
        })

    return pd.DataFrame(rows)


def create_changeover_data():
    """Create synthetic product changeover data."""
    start_time = datetime(2024, 1, 1, 6, 0, 0)
    rows = []

    products = ['PRODUCT_A', 'PRODUCT_B', 'PRODUCT_C']
    current_product = 0
    t = start_time

    for i in range(200):
        # Change product every ~40 records
        if i > 0 and i % 40 == 0:
            current_product = (current_product + 1) % len(products)

        rows.append({
            'systime': t,
            'uuid': 'product_id',
            'value_string': products[current_product],
            'is_delta': True,
        })

        # Also add a metric signal for stable_band detection
        metric_val = 100.0 + np.random.normal(0, 2.0)
        if i % 40 < 5:  # First 5 records after changeover are unstable
            metric_val += np.random.uniform(-10, 10)
        rows.append({
            'systime': t,
            'uuid': 'quality_metric',
            'value_double': metric_val,
            'is_delta': True,
        })

        t += timedelta(seconds=30)

    return pd.DataFrame(rows)


def create_flow_constraint_data():
    """Create synthetic upstream/downstream run state data for blocked/starved detection."""
    start_time = datetime(2024, 1, 1, 8, 0, 0)
    rows = []
    np.random.seed(55)

    for i in range(300):
        t = start_time + timedelta(seconds=i * 5)
        # Upstream runs most of the time
        up_running = True if np.random.random() > 0.1 else False
        # Downstream runs most of the time but occasionally stops
        dn_running = True if np.random.random() > 0.15 else False

        # Inject a blocked period (upstream running, downstream stopped)
        if 100 <= i <= 115:
            up_running = True
            dn_running = False

        # Inject a starved period (downstream running, upstream stopped)
        if 200 <= i <= 210:
            up_running = False
            dn_running = True

        rows.append({
            'systime': t,
            'uuid': 'upstream_run',
            'value_bool': up_running,
            'is_delta': True,
        })
        rows.append({
            'systime': t,
            'uuid': 'downstream_run',
            'value_bool': dn_running,
            'is_delta': True,
        })

    return pd.DataFrame(rows)


def demo_machine_state():
    """Demo 1: Machine state detection and transitions."""
    print("\n" + "=" * 70)
    print("DEMO 1: Machine State Events")
    print("=" * 70)

    df = create_machine_state_data()
    print(f"\nDataset: {len(df)} state samples")

    machine = MachineStateEvents(
        dataframe=df,
        run_state_uuid='machine_run_state',
        event_uuid='machine:state',
    )

    # Run/idle intervals
    print("\n--- Run/Idle Intervals ---")
    intervals = machine.detect_run_idle()
    print(f"  Total intervals: {len(intervals)}")
    if not intervals.empty:
        run_intervals = intervals[intervals['state'] == 'run']
        idle_intervals = intervals[intervals['state'] == 'idle']
        print(f"  Run intervals: {len(run_intervals)}, "
              f"avg duration: {run_intervals['duration_seconds'].mean():.0f}s")
        print(f"  Idle intervals: {len(idle_intervals)}, "
              f"avg duration: {idle_intervals['duration_seconds'].mean():.0f}s")
        print("\n  First 5 intervals:")
        print(intervals[['start', 'end', 'state', 'duration_seconds']].head())

    # Filtered intervals (min 30s)
    print("\n--- Filtered Intervals (min_duration=30s) ---")
    filtered = machine.detect_run_idle(min_duration='30s')
    print(f"  Intervals after filtering: {len(filtered)}")

    # Transition events
    print("\n--- Transition Events ---")
    transitions = machine.transition_events()
    print(f"  Total transitions: {len(transitions)}")
    if not transitions.empty:
        print(transitions[['systime', 'transition', 'time_since_last_transition_seconds']].head())

    # State quality metrics
    print("\n--- State Quality Metrics ---")
    metrics = machine.state_quality_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")


def demo_line_throughput():
    """Demo 2: Line throughput and takt adherence."""
    print("\n" + "=" * 70)
    print("DEMO 2: Line Throughput Events")
    print("=" * 70)

    df = create_throughput_data()
    print(f"\nDataset: {len(df)} records (counter + cycle triggers)")

    throughput = LineThroughputEvents(
        dataframe=df,
        event_uuid='prod:throughput',
    )

    # Part counts per window
    print("\n--- Part Counts (5-minute windows) ---")
    parts = throughput.count_parts('part_counter', value_column='value_integer', window='5min')
    print(f"  Windows: {len(parts)}")
    if not parts.empty:
        print(f"  Avg parts/window: {parts['count'].mean():.1f}")
        print(f"  Max parts/window: {parts['count'].max():.0f}")
        print(parts[['window_start', 'count']].head())

    # Takt adherence
    print("\n--- Takt Adherence (takt=50s) ---")
    takt = throughput.takt_adherence(
        'cycle_trigger',
        value_column='value_bool',
        takt_time='50s',
    )
    print(f"  Total cycles measured: {len(takt)}")
    if not takt.empty:
        violations = takt[takt['violation']]
        print(f"  Takt violations: {len(violations)} ({len(violations)/len(takt)*100:.1f}%)")
        print(f"  Avg cycle time: {takt['cycle_time_seconds'].mean():.1f}s")
        print(f"  Max cycle time: {takt['cycle_time_seconds'].max():.1f}s")
        print(takt[['systime', 'cycle_time_seconds', 'violation']].head())

    # OEE metrics
    print("\n--- OEE Metrics (1-hour windows) ---")
    oee = throughput.throughput_oee('part_counter', value_column='value_integer', window='1h')
    if not oee.empty:
        print(f"  Avg OEE score: {oee['oee_score'].mean():.2f}")
        print(oee[['window_start', 'actual_count', 'performance', 'oee_score']].head())


def demo_changeover():
    """Demo 3: Changeover event detection."""
    print("\n" + "=" * 70)
    print("DEMO 3: Changeover Events")
    print("=" * 70)

    df = create_changeover_data()
    print(f"\nDataset: {len(df)} records")

    changeover = ChangeoverEvents(
        dataframe=df,
        event_uuid='prod:changeover',
    )

    # Detect changeovers
    print("\n--- Changeover Detection ---")
    changes = changeover.detect_changeover('product_id', value_column='value_string')
    print(f"  Changeovers detected: {len(changes)}")
    if not changes.empty:
        print(changes[['systime', 'new_value']].to_string())

    # Changeover windows (fixed duration)
    print("\n--- Changeover Windows (fixed 10-minute window) ---")
    windows = changeover.changeover_window(
        'product_id',
        value_column='value_string',
        until='fixed_window',
        config={'duration': '10m'},
    )
    if not windows.empty:
        print(windows[['start', 'end', 'method', 'completed']].to_string())

    # Changeover quality metrics
    print("\n--- Changeover Quality Metrics ---")
    metrics = changeover.changeover_quality_metrics('product_id', value_column='value_string')
    if not metrics.empty:
        print(metrics.to_string())


def demo_flow_constraints():
    """Demo 4: Flow constraint (blocked/starved) detection."""
    print("\n" + "=" * 70)
    print("DEMO 4: Flow Constraint Events")
    print("=" * 70)

    df = create_flow_constraint_data()
    print(f"\nDataset: {len(df)} records (upstream + downstream states)")

    flow = FlowConstraintEvents(
        dataframe=df,
        event_uuid='prod:flow',
    )

    roles = {
        'upstream_run': 'upstream_run',
        'downstream_run': 'downstream_run',
    }

    # Blocked events
    print("\n--- Blocked Events ---")
    blocked = flow.blocked_events(roles=roles, tolerance='10s', min_duration='5s')
    print(f"  Blocked events: {len(blocked)}")
    if not blocked.empty:
        print(blocked[['start', 'end', 'type', 'severity', 'duration']].to_string())

    # Starved events
    print("\n--- Starved Events ---")
    starved = flow.starved_events(roles=roles, tolerance='10s', min_duration='5s')
    print(f"  Starved events: {len(starved)}")
    if not starved.empty:
        print(starved[['start', 'end', 'type', 'severity', 'duration']].to_string())

    # Comprehensive analytics
    print("\n--- Flow Constraint Analytics ---")
    analytics = flow.flow_constraint_analytics(roles=roles, tolerance='10s', min_duration='5s')
    summary = analytics['summary']
    print(f"  Total constraint events: {summary['total_constraint_events']}")
    print(f"  Blocked count: {summary['blocked_count']}")
    print(f"  Starved count: {summary['starved_count']}")
    print(f"  Blocked total duration: {summary['blocked_total_duration']}")
    print(f"  Starved total duration: {summary['starved_total_duration']}")
    print(f"  Alignment quality: {summary['overall_alignment_quality']:.2f}")


def main():
    """Run all production event demonstrations."""
    print("\n" + "=" * 70)
    print("Production Events Demonstration")
    print("=" * 70)

    try:
        demo_machine_state()
        demo_line_throughput()
        demo_changeover()
        demo_flow_constraints()

        print("\n" + "=" * 70)
        print("All demonstrations completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
