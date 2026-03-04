#!/usr/bin/env python3
"""
Demonstration of supply chain event detection in ts-shape.

This script shows how to use:
1. InventoryMonitoringEvents (low stock, consumption rate, reorder breach, stockout prediction)
2. LeadTimeAnalysisEvents (lead time calculation, statistics, anomaly detection)
3. DemandPatternEvents (demand aggregation, spike detection, seasonality)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import ts_shape
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ts_shape.events.supplychain.inventory_monitoring import InventoryMonitoringEvents
from ts_shape.events.supplychain.lead_time_analysis import LeadTimeAnalysisEvents
from ts_shape.events.supplychain.demand_pattern import DemandPatternEvents


def create_inventory_data():
    """Create synthetic inventory level data with consumption and replenishment."""
    np.random.seed(42)
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    rows = []

    level = 500.0  # starting inventory
    t = start_time

    for i in range(200):
        rows.append({
            'systime': t,
            'uuid': 'warehouse_a',
            'value_double': level,
            'is_delta': True,
        })

        # Consume inventory
        consumption = np.random.uniform(2, 8)
        level -= consumption

        # Replenishment at certain points
        if i in [60, 120, 170]:
            level += 300.0  # big replenishment

        # Ensure non-negative
        level = max(0, level)

        t += timedelta(hours=1)

    return pd.DataFrame(rows)


def create_lead_time_data():
    """Create synthetic order/delivery event data."""
    np.random.seed(77)
    start_time = datetime(2024, 1, 1, 8, 0, 0)
    rows = []

    n_orders = 20
    t = start_time

    for i in range(n_orders):
        order_id = f"PO-{1000 + i}"

        # Order placement
        rows.append({
            'systime': t,
            'uuid': 'order_placed',
            'value_string': order_id,
            'is_delta': True,
        })

        # Delivery: normally 48-72 hours later, with some anomalies
        lead_time_hours = np.random.normal(60, 8)
        if i in [7, 15]:  # anomalous orders
            lead_time_hours = 120 + np.random.uniform(0, 20)

        delivery_time = t + timedelta(hours=max(24, lead_time_hours))
        rows.append({
            'systime': delivery_time,
            'uuid': 'delivery_received',
            'value_string': order_id,
            'is_delta': True,
        })

        # Next order in 1-3 days
        t += timedelta(hours=np.random.uniform(24, 72))

    return pd.DataFrame(rows)


def create_demand_data():
    """Create synthetic demand signal with weekly seasonality and spikes."""
    np.random.seed(33)
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    rows = []

    for day in range(60):
        t = start_time + timedelta(days=day)
        weekday = t.weekday()

        # Base demand with day-of-week pattern
        if weekday < 5:  # weekdays
            base_demand = np.random.normal(100, 15)
        else:  # weekends
            base_demand = np.random.normal(40, 10)

        # Inject demand spikes
        if day in [10, 35, 50]:
            base_demand += np.random.uniform(80, 120)

        # Generate hourly demand within the day
        for hour in range(8, 20):  # business hours
            hourly_demand = max(0, base_demand / 12 + np.random.normal(0, 2))
            rows.append({
                'systime': t + timedelta(hours=hour),
                'uuid': 'product_demand',
                'value_double': hourly_demand,
                'is_delta': True,
            })

    return pd.DataFrame(rows)


def demo_inventory_monitoring():
    """Demo 1: Inventory monitoring events."""
    print("\n" + "=" * 70)
    print("DEMO 1: Inventory Monitoring Events")
    print("=" * 70)

    df = create_inventory_data()
    print(f"\nDataset: {len(df)} inventory level readings")

    monitor = InventoryMonitoringEvents(
        dataframe=df,
        level_uuid='warehouse_a',
        event_uuid='sc:inventory',
        value_column='value_double',
    )

    # Low stock detection
    print("\n--- Low Stock Detection (min_level=100, hold=2h) ---")
    low_stock = monitor.detect_low_stock(min_level=100, hold='2h')
    print(f"  Low stock intervals: {len(low_stock)}")
    if not low_stock.empty:
        print(low_stock[['start', 'end', 'min_value', 'avg_value', 'duration_seconds']].to_string())

    # Consumption rate
    print("\n--- Consumption Rate (4-hour windows) ---")
    consumption = monitor.consumption_rate(window='4h')
    if not consumption.empty:
        positive_consumption = consumption[consumption['consumption_rate'] > 0]
        print(f"  Windows analyzed: {len(consumption)}")
        print(f"  Windows with consumption: {len(positive_consumption)}")
        if not positive_consumption.empty:
            print(f"  Avg consumption rate: {positive_consumption['consumption_rate'].mean():.2f} units/hour")
            print(f"  Max consumption rate: {positive_consumption['consumption_rate'].max():.2f} units/hour")
        print(consumption[['window_start', 'consumption_rate', 'level_start', 'level_end']].head(10).to_string())

    # Reorder point breach
    print("\n--- Reorder Point Breach (reorder=200, safety=50) ---")
    breaches = monitor.reorder_point_breach(reorder_level=200, safety_stock=50)
    print(f"  Breach events: {len(breaches)}")
    if not breaches.empty:
        print(breaches[['systime', 'current_level', 'breach_type', 'deficit']].to_string())

    # Stockout prediction
    print("\n--- Stockout Prediction ---")
    predictions = monitor.stockout_prediction(consumption_rate_window='8h')
    if not predictions.empty:
        finite_predictions = predictions[predictions['estimated_stockout_time_hours'] < np.inf]
        print(f"  Total predictions: {len(predictions)}")
        print(f"  With finite stockout time: {len(finite_predictions)}")
        if not finite_predictions.empty:
            print(f"  Min time to stockout: {finite_predictions['estimated_stockout_time_hours'].min():.1f} hours")
            print("\n  Samples with lowest stockout time:")
            print(finite_predictions.nsmallest(5, 'estimated_stockout_time_hours')[
                ['systime', 'current_level', 'consumption_rate',
                 'estimated_stockout_time_hours']].to_string())


def demo_lead_time_analysis():
    """Demo 2: Lead time analysis events."""
    print("\n" + "=" * 70)
    print("DEMO 2: Lead Time Analysis Events")
    print("=" * 70)

    df = create_lead_time_data()
    print(f"\nDataset: {len(df)} records (orders + deliveries)")

    analyzer = LeadTimeAnalysisEvents(
        dataframe=df,
        event_uuid='sc:lead_time',
    )

    # Calculate lead times
    print("\n--- Lead Time Calculation ---")
    lead_times = analyzer.calculate_lead_times(
        order_uuid='order_placed',
        delivery_uuid='delivery_received',
    )
    print(f"  Order-delivery pairs: {len(lead_times)}")
    if not lead_times.empty:
        print(lead_times[['order_time', 'delivery_time', 'lead_time_hours', 'order_id']].to_string())

    # Lead time statistics
    print("\n--- Lead Time Statistics ---")
    stats = analyzer.lead_time_statistics(
        order_uuid='order_placed',
        delivery_uuid='delivery_received',
    )
    if not stats.empty:
        print(stats.to_string(index=False))

    # Detect anomalies
    print("\n--- Lead Time Anomalies (threshold_factor=1.5) ---")
    anomalies = analyzer.detect_lead_time_anomalies(
        order_uuid='order_placed',
        delivery_uuid='delivery_received',
        threshold_factor=1.5,
    )
    print(f"  Anomalous lead times: {len(anomalies)}")
    if not anomalies.empty:
        print(anomalies[['order_time', 'delivery_time', 'lead_time_hours', 'z_score']].to_string())


def demo_demand_patterns():
    """Demo 3: Demand pattern analysis events."""
    print("\n" + "=" * 70)
    print("DEMO 3: Demand Pattern Events")
    print("=" * 70)

    df = create_demand_data()
    print(f"\nDataset: {len(df)} demand records over 60 days")

    analyzer = DemandPatternEvents(
        dataframe=df,
        demand_uuid='product_demand',
        event_uuid='sc:demand',
        value_column='value_double',
    )

    # Demand by period (daily)
    print("\n--- Daily Demand Aggregation ---")
    daily = analyzer.demand_by_period(period='1D')
    if not daily.empty:
        print(f"  Days with data: {len(daily)}")
        print(f"  Avg daily demand: {daily['total_demand'].mean():.1f}")
        print(f"  Max daily demand: {daily['total_demand'].max():.1f}")
        print(daily[['period_start', 'total_demand', 'avg_demand', 'peak_demand']].head(10).to_string())

    # Demand spikes
    print("\n--- Demand Spike Detection (threshold_factor=1.5) ---")
    spikes = analyzer.detect_demand_spikes(threshold_factor=1.5, window='1D')
    print(f"  Demand spikes detected: {len(spikes)}")
    if not spikes.empty:
        print(spikes[['period_start', 'demand', 'baseline_mean', 'spike_magnitude']].to_string())

    # Seasonality by day of week
    print("\n--- Seasonality Summary (day-of-week) ---")
    seasonal = analyzer.seasonality_summary(period='1D')
    if not seasonal.empty:
        print(seasonal.to_string(index=False))

    # Hourly seasonality
    print("\n--- Hourly Demand Pattern ---")
    hourly = analyzer.seasonality_summary(period='1h')
    if not hourly.empty:
        print(hourly.to_string(index=False))


def main():
    """Run all supply chain event demonstrations."""
    print("\n" + "=" * 70)
    print("Supply Chain Events Demonstration")
    print("=" * 70)

    try:
        demo_inventory_monitoring()
        demo_lead_time_analysis()
        demo_demand_patterns()

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
