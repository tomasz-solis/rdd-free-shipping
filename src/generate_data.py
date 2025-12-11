"""
Data Generation for RDD Free Shipping Analysis

This module generates synthetic e-commerce shopping session data for learning 
Regression Discontinuity Design.

Key features:
- Cart value as running variable (€0-200)
- Sharp treatment assignment at threshold = €50 (free shipping)
- Known treatment effect for validation
- Realistic customer heterogeneity and shopping behavior
"""

import numpy as np
import pandas as pd


def generate_rdd_ecommerce_data(
    n_sessions: int = 10000,
    cutoff: float = 50.0,
    shipping_cost: float = 5.95,
    treatment_effect: float = 0.08,
    random_seed: int = 42
) -> pd.DataFrame:
    """Generate synthetic e-commerce sessions with sharp RDD at cutoff threshold."""
    np.random.seed(random_seed)
    
    # Generate customer demographics
    age_categories = ['18-24', '25-34', '35-44', '45-54', '55+']
    age_probs = [0.15, 0.35, 0.25, 0.15, 0.10]
    customer_age = np.random.choice(age_categories, size=n_sessions, p=age_probs)
    
    # Account tenure (days since account creation)
    # Mix of new and returning customers
    account_tenure_days = np.random.gamma(shape=2, scale=100, size=n_sessions)
    account_tenure_days = np.clip(account_tenure_days, 1, 2000)
    
    # Previous purchase history
    # Most customers have few purchases, some are loyal repeat buyers
    previous_purchases = np.random.negative_binomial(n=1, p=0.3, size=n_sessions)
    previous_purchases = np.clip(previous_purchases, 0, 50)
    
    # Product category
    categories = ['Electronics', 'Fashion', 'Home & Garden', 'Books & Media', 'Sports & Outdoors']
    category_probs = [0.25, 0.30, 0.20, 0.15, 0.10]
    product_category = np.random.choice(categories, size=n_sessions, p=category_probs)
    
    # Number of items in cart
    items_in_cart = np.random.poisson(lam=3, size=n_sessions) + 1  # At least 1 item
    items_in_cart = np.clip(items_in_cart, 1, 15)
    
    # Generate cart value (running variable)
    # Use gamma distribution to create realistic right-skewed cart values
    # Centered around €50 with good density near the threshold
    cart_value_base = np.random.gamma(shape=3, scale=15, size=n_sessions)
    
    # Add some relationship to items in cart and category
    category_price_effect = {
        'Electronics': 20,
        'Fashion': 10,
        'Home & Garden': 15,
        'Books & Media': -5,
        'Sports & Outdoors': 12
    }
    category_effect = np.array([category_price_effect[cat] for cat in product_category])
    
    cart_value = cart_value_base + 0.5 * items_in_cart + category_effect
    cart_value = cart_value + np.random.normal(0, 5, n_sessions)  # Add noise
    cart_value = np.clip(cart_value, 5, 200)  # Keep in reasonable range
    
    # Treatment assignment (sharp RDD)
    treatment = (cart_value >= cutoff).astype(int)
    
    # Generate potential outcomes
    # Baseline purchase completion probability (without free shipping)
    # Factors that increase purchase probability:
    # - Higher cart value (people who add more are more committed)
    # - More previous purchases (loyal customers)
    # - Longer account tenure (trust in the store)
    
    # Base probability increases slightly with cart value
    base_prob = 0.40 + 0.001 * cart_value
    
    # Loyal customers more likely to complete
    loyalty_boost = 0.02 * np.minimum(previous_purchases / 10, 0.15)
    
    # Older accounts slightly more likely to complete
    tenure_boost = 0.01 * np.minimum(account_tenure_days / 365, 0.10)
    
    # Electronics and fashion have slightly higher completion rates
    category_completion = {
        'Electronics': 0.05,
        'Fashion': 0.03,
        'Home & Garden': 0.00,
        'Books & Media': -0.02,
        'Sports & Outdoors': 0.01
    }
    category_boost = np.array([category_completion[cat] for cat in product_category])
    
    # Add individual heterogeneity (unobserved factors)
    individual_noise = np.random.normal(0, 0.08, n_sessions)
    
    # Y0: Purchase probability WITHOUT free shipping
    p_Y0 = base_prob + loyalty_boost + tenure_boost + category_boost + individual_noise
    p_Y0 = np.clip(p_Y0, 0.05, 0.95)  # Keep probabilities valid
    
    # Y1: Purchase probability WITH free shipping
    # Free shipping increases probability by treatment_effect
    p_Y1 = p_Y0 + treatment_effect
    p_Y1 = np.clip(p_Y1, 0.05, 0.95)
    
    # Generate binary outcomes
    Y0 = np.random.binomial(1, p_Y0)
    Y1 = np.random.binomial(1, p_Y1)
    
    # Observed outcome (fundamental problem of causal inference)
    completed_purchase = np.where(treatment == 1, Y1, Y0)
    
    # Create DataFrame
    df = pd.DataFrame({
        'session_id': range(1, n_sessions + 1),
        'customer_age': customer_age,
        'account_tenure_days': account_tenure_days.astype(int),
        'previous_purchases': previous_purchases,
        'product_category': product_category,
        'items_in_cart': items_in_cart,
        'cart_value': cart_value.round(2),
        'treatment': treatment,
        'completed_purchase': completed_purchase,
        'Y0': Y0,  # Include for validation (would not observe in real data)
        'Y1': Y1   # Include for validation (would not observe in real data)
    })
    
    return df


if __name__ == '__main__':
    # Generate data
    df = generate_rdd_ecommerce_data(
        n_sessions=10000, 
        cutoff=50.0,
        shipping_cost=5.95,
        treatment_effect=0.08
    )
    
    # Print summary statistics
    print(f"Generated {df.shape[0]:,} sessions with {df.shape[1]} columns")
    print(f"Treatment split: {(df['treatment']==1).sum():,} treated, {(df['treatment']==0).sum():,} control")
    
    completion_rates = df.groupby('treatment')['completed_purchase'].mean()
    print(f"Completion rates: {completion_rates[0]:.1%} control, {completion_rates[1]:.1%} treated")
    print(f"Cart value range: €{df['cart_value'].min():.0f}-€{df['cart_value'].max():.0f}")
    
    threshold_window = df[(df['cart_value'] >= 45) & (df['cart_value'] <= 55)]
    print(f"Sessions near threshold (€45-55): {len(threshold_window):,}")
    
    # Save to CSV
    output_path = '../data/rdd_ecommerce.csv'
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
