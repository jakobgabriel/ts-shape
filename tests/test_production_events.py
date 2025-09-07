import pandas as pd  # type: ignore

from ts_shape.events.production import (
    MachineStateEvents,
    LineThroughputEvents,
    ChangeoverEvents,
    FlowConstraintEvents,
)


def test_machine_state_intervals_and_transitions():
    t = pd.date_range('2024-01-01 00:00:00', periods=6, freq='30s')
    run = [False, False, True, True, False, False]
    df = pd.DataFrame({
        'uuid': ['run'] * len(t),
        'systime': t,
        'value_bool': run,
        'is_delta': [True] * len(t),
    })

    mse = MachineStateEvents(df, run_state_uuid='run')
    intervals = mse.detect_run_idle(min_duration='30s')
    assert not intervals.empty
    assert set(intervals['state'].unique()) == {'run', 'idle'}

    transitions = mse.transition_events()
    assert not transitions.empty
    assert set(transitions['transition'].unique()) == {'idle_to_run', 'run_to_idle'}


def test_line_throughput_count_and_takt():
    # Counter increments every minute by 5 parts
    t = pd.date_range('2024-01-01 00:00:00', periods=6, freq='1min')
    counter = [0, 5, 10, 15, 20, 25]
    df = pd.DataFrame({
        'uuid': ['cnt'] * len(t),
        'systime': t,
        'value_integer': counter,
        'is_delta': [True] * len(t),
    })
    lte = LineThroughputEvents(df)
    counts = lte.count_parts(counter_uuid='cnt', window='2min')
    assert not counts.empty
    assert 'count' in counts.columns

    # Use boolean trigger to define cycle boundaries, takt=90s
    tb = pd.DataFrame({
        'uuid': ['cyc'] * len(t),
        'systime': t,
        'value_bool': [True, False, True, False, True, False],
        'is_delta': [True] * len(t),
    })
    lte2 = LineThroughputEvents(tb)
    takt = lte2.takt_adherence(cycle_uuid='cyc', value_column='value_bool', takt_time='90s', min_violation='0s')
    assert not takt.empty
    assert 'cycle_time_seconds' in takt.columns


def test_changeover_detect_and_window_stable_band():
    # Product changes A->B at t=60s, metric stabilizes after 2 minutes
    t = pd.date_range('2024-01-01 00:00:00', periods=7, freq='1min')
    prod = ['A', 'A', 'B', 'B', 'B', 'B', 'B']
    df_prod = pd.DataFrame({'uuid': ['prod']*len(t), 'systime': t, 'value_string': prod, 'is_delta': [True]*len(t)})
    metric_vals = [10.0, 10.2, 12.5, 12.2, 12.1, 12.05, 12.0]  # settles near 12 ±0.2 for ≥2m
    df_m = pd.DataFrame({'uuid': ['m1']*len(t), 'systime': t, 'value_double': metric_vals, 'is_delta': [True]*len(t)})
    df = pd.concat([df_prod, df_m], ignore_index=True)

    co = ChangeoverEvents(df)
    changes = co.detect_changeover(product_uuid='prod', value_column='value_string', min_hold='0s')
    assert not changes.empty
    win = co.changeover_window(
        product_uuid='prod',
        value_column='value_string',
        until='stable_band',
        config={'metrics': [{'uuid': 'm1', 'value_column': 'value_double', 'band': 0.25, 'hold': '2m'}]}
    )
    assert not win.empty
    assert (win['end'] >= win['start']).all()


def test_flow_blocked_and_starved():
    t = pd.date_range('2024-01-01 00:00:00', periods=6, freq='30s')
    up = [False, True, True, True, False, False]
    dn = [False, False, True, True, True, False]
    df_up = pd.DataFrame({'uuid': ['up']*len(t), 'systime': t, 'value_bool': up, 'is_delta': [True]*len(t)})
    df_dn = pd.DataFrame({'uuid': ['dn']*len(t), 'systime': t, 'value_bool': dn, 'is_delta': [True]*len(t)})
    df = pd.concat([df_up, df_dn], ignore_index=True)

    fce = FlowConstraintEvents(df)
    blocked = fce.blocked_events(roles={'upstream_run': 'up', 'downstream_run': 'dn'}, tolerance='0s', min_duration='30s')
    assert not blocked.empty
    assert (blocked['type'] == 'blocked').all()

    starved = fce.starved_events(roles={'upstream_run': 'up', 'downstream_run': 'dn'}, tolerance='0s', min_duration='30s')
    assert isinstance(starved, pd.DataFrame)

