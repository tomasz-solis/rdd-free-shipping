"""
Unit tests for data generation module.

Tests ensure:
1. Data generation produces correct structure
2. Treatment assignment is sharp at cutoff
3. Known treatment effect is embedded correctly
4. Data quality constraints are met
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from generate_data import generate_rdd_ecommerce_data


class TestDataGeneration:
    """Test suite for RDD data generation."""

    def test_output_shape(self):
        """Test that generated data has correct dimensions."""
        df = generate_rdd_ecommerce_data(n_sessions=1000, random_seed=42)

        assert len(df) == 1000, "Should generate requested number of sessions"
        assert len(df.columns) >= 9, "Should have all required columns"

    def test_required_columns(self):
        """Test that all required columns exist."""
        df = generate_rdd_ecommerce_data(n_sessions=100, random_seed=42)

        required_cols = [
            'session_id', 'customer_age', 'account_tenure_days',
            'previous_purchases', 'product_category', 'items_in_cart',
            'cart_value', 'treatment', 'completed_purchase'
        ]

        for col in required_cols:
            assert col in df.columns, f"Missing required column: {col}"

    def test_sharp_treatment_assignment(self):
        """Test that treatment assignment is sharp at cutoff."""
        cutoff = 50.0
        df = generate_rdd_ecommerce_data(n_sessions=10000, cutoff=cutoff, random_seed=42)

        # All below cutoff should be control
        below = df[df['cart_value'] < cutoff]
        assert (below['treatment'] == 0).all(), "All below cutoff should be control"

        # All at or above cutoff should be treated
        above = df[df['cart_value'] >= cutoff]
        assert (above['treatment'] == 1).all(), "All at/above cutoff should be treated"

    def test_cart_value_range(self):
        """Test that cart values are within expected range."""
        df = generate_rdd_ecommerce_data(n_sessions=1000, random_seed=42)

        assert df['cart_value'].min() >= 5, "Cart values should be at least €5"
        assert df['cart_value'].max() <= 200, "Cart values should not exceed €200"
        assert df['cart_value'].isna().sum() == 0, "No missing cart values"

    def test_binary_outcome(self):
        """Test that outcome variable is binary."""
        df = generate_rdd_ecommerce_data(n_sessions=1000, random_seed=42)

        assert set(df['completed_purchase'].unique()).issubset({0, 1}), \
            "Outcome should be binary (0 or 1)"

    def test_treatment_effect_direction(self):
        """Test that treatment increases completion probability."""
        df = generate_rdd_ecommerce_data(
            n_sessions=10000,
            cutoff=50.0,
            treatment_effect=0.08,
            random_seed=42
        )

        # Use narrow bandwidth to compare similar customers
        near_cutoff = df[(df['cart_value'] >= 45) & (df['cart_value'] <= 55)]

        control_rate = near_cutoff[near_cutoff['treatment'] == 0]['completed_purchase'].mean()
        treatment_rate = near_cutoff[near_cutoff['treatment'] == 1]['completed_purchase'].mean()

        assert treatment_rate > control_rate, \
            "Treatment should increase completion rate"

        # Effect should be roughly 8pp (allow for sampling variation)
        effect = treatment_rate - control_rate
        assert 0.03 < effect < 0.13, \
            f"Effect {effect:.3f} should be near 0.08 (allow ±0.05 for noise)"

    def test_counterfactual_consistency(self):
        """Test that Y0 and Y1 columns are consistent with treatment effect."""
        df = generate_rdd_ecommerce_data(
            n_sessions=10000,
            treatment_effect=0.08,
            random_seed=42
        )

        # Y1 should generally be higher than Y0 (not always due to binary noise)
        avg_y0 = df['Y0'].mean()
        avg_y1 = df['Y1'].mean()

        assert avg_y1 > avg_y0, "Average Y1 should exceed average Y0"

        # Difference should be close to treatment effect
        diff = avg_y1 - avg_y0
        assert 0.06 < diff < 0.10, \
            f"Y1-Y0 difference {diff:.3f} should be near 0.08"

    def test_reproducibility(self):
        """Test that same seed produces identical data."""
        df1 = generate_rdd_ecommerce_data(n_sessions=500, random_seed=123)
        df2 = generate_rdd_ecommerce_data(n_sessions=500, random_seed=123)

        pd.testing.assert_frame_equal(df1, df2,
            "Same seed should produce identical data")

    def test_different_seeds_differ(self):
        """Test that different seeds produce different data."""
        df1 = generate_rdd_ecommerce_data(n_sessions=500, random_seed=1)
        df2 = generate_rdd_ecommerce_data(n_sessions=500, random_seed=2)

        # Cart values should differ
        assert not np.allclose(df1['cart_value'].values, df2['cart_value'].values), \
            "Different seeds should produce different cart values"

    def test_no_duplicate_session_ids(self):
        """Test that session IDs are unique."""
        df = generate_rdd_ecommerce_data(n_sessions=1000, random_seed=42)

        assert df['session_id'].nunique() == len(df), \
            "All session IDs should be unique"

    def test_covariate_realism(self):
        """Test that covariates have realistic distributions."""
        df = generate_rdd_ecommerce_data(n_sessions=10000, random_seed=42)

        # Previous purchases should be non-negative
        assert (df['previous_purchases'] >= 0).all(), \
            "Previous purchases should be non-negative"

        # Account tenure should be positive
        assert (df['account_tenure_days'] > 0).all(), \
            "Account tenure should be positive"

        # Items in cart should be at least 1
        assert (df['items_in_cart'] >= 1).all(), \
            "Must have at least 1 item in cart"

        # Age categories should be valid
        valid_ages = ['18-24', '25-34', '35-44', '45-54', '55+']
        assert df['customer_age'].isin(valid_ages).all(), \
            "Age categories should be valid"

    def test_custom_treatment_effect(self):
        """Test that custom treatment effects are embedded correctly."""
        te_values = [0.05, 0.10, 0.15]

        for te in te_values:
            df = generate_rdd_ecommerce_data(
                n_sessions=10000,
                treatment_effect=te,
                random_seed=42
            )

            # Check average difference between Y1 and Y0
            avg_effect = (df['Y1'] - df['Y0']).mean()

            assert abs(avg_effect - te) < 0.02, \
                f"Embedded effect {avg_effect:.3f} should match target {te}"

    def test_sufficient_density_near_cutoff(self):
        """Test that there's enough data near the cutoff for analysis."""
        df = generate_rdd_ecommerce_data(n_sessions=10000, cutoff=50.0, random_seed=42)

        # Should have decent sample in ±20 window
        near_cutoff = df[(df['cart_value'] >= 30) & (df['cart_value'] <= 70)]

        assert len(near_cutoff) > 3000, \
            "Should have sufficient observations near cutoff"

        # Both treatment and control should be represented
        n_control = (near_cutoff['treatment'] == 0).sum()
        n_treatment = (near_cutoff['treatment'] == 1).sum()

        assert n_control > 1000, "Should have enough control observations"
        assert n_treatment > 1000, "Should have enough treatment observations"


class TestDataQuality:
    """Tests for data quality and edge cases."""

    def test_no_missing_values(self):
        """Test that there are no missing values."""
        df = generate_rdd_ecommerce_data(n_sessions=1000, random_seed=42)

        assert df.isna().sum().sum() == 0, "Should have no missing values"

    def test_reasonable_completion_rates(self):
        """Test that completion rates are in reasonable range."""
        df = generate_rdd_ecommerce_data(n_sessions=10000, random_seed=42)

        overall_rate = df['completed_purchase'].mean()

        assert 0.3 < overall_rate < 0.7, \
            f"Overall completion rate {overall_rate:.2f} should be reasonable"

    def test_small_sample_works(self):
        """Test that generation works with small samples."""
        df = generate_rdd_ecommerce_data(n_sessions=10, random_seed=42)

        assert len(df) == 10, "Should handle small samples"

    def test_large_sample_works(self):
        """Test that generation works with large samples."""
        df = generate_rdd_ecommerce_data(n_sessions=50000, random_seed=42)

        assert len(df) == 50000, "Should handle large samples"
        assert df.memory_usage(deep=True).sum() < 50_000_000, \
            "Should not use excessive memory"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
