"""
Interactive Dashboard for RDD Free Shipping Analysis

This dashboard allows stakeholders to:
1. Explore the RDD results visually
2. Adjust business parameters to see ROI impact
3. View treatment effects by customer segment
4. Compare RDD to alternative methods
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Page config
st.set_page_config(
    page_title="Free Shipping Impact Analysis",
    page_icon="📦",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    data_path = Path(__file__).parent.parent / 'data' / 'rdd_ecommerce.csv'
    return pd.read_csv(data_path)

df = load_data()

# Title
st.title("Free Shipping Impact Analysis")
st.markdown("### Regression Discontinuity Design Results")

# Sidebar for parameters
st.sidebar.header("Analysis Parameters")

bandwidth = st.sidebar.slider(
    "Bandwidth (€)",
    min_value=5,
    max_value=40,
    value=20,
    step=5,
    help="Window around €50 cutoff to include in analysis"
)

st.sidebar.markdown("---")
st.sidebar.header("Business Parameters")

margin_rate = st.sidebar.slider(
    "Gross Margin (%)",
    min_value=10,
    max_value=50,
    value=25,
    step=5,
    help="Product gross margin percentage"
) / 100

shipping_cost = st.sidebar.number_input(
    "Shipping Cost (€)",
    min_value=0.0,
    max_value=20.0,
    value=5.95,
    step=0.50
)

monthly_sessions = st.sidebar.number_input(
    "Monthly Sessions Near €50",
    min_value=1000,
    max_value=50000,
    value=5000,
    step=1000
)

# Main analysis
cutoff = 50.0

# Filter to bandwidth
df_window = df[
    (df['cart_value'] >= cutoff - bandwidth) &
    (df['cart_value'] <= cutoff + bandwidth)
].copy()

df_window['cart_centered'] = df_window['cart_value'] - cutoff
df_window['treat_x_cart'] = df_window['treatment'] * df_window['cart_centered']

# Run RDD regression
from sklearn.linear_model import LinearRegression

X = df_window[['cart_centered', 'treatment', 'treat_x_cart']]
y = df_window['completed_purchase']

# Simple OLS for point estimate
treated_near = df_window[df_window['treatment'] == 1]['completed_purchase'].mean()
control_near = df_window[df_window['treatment'] == 0]['completed_purchase'].mean()
naive_diff = treated_near - control_near

# Proper RDD with controls
model = LinearRegression()
model.fit(X, y)
treatment_effect = model.coef_[1]

# Bootstrap CI
n_boot = 500
boot_effects = []
for _ in range(n_boot):
    boot_idx = np.random.choice(len(df_window), len(df_window), replace=True)
    boot_X = X.iloc[boot_idx]
    boot_y = y.iloc[boot_idx]
    boot_model = LinearRegression()
    boot_model.fit(boot_X, boot_y)
    boot_effects.append(boot_model.coef_[1])

ci_lower = np.percentile(boot_effects, 2.5)
ci_upper = np.percentile(boot_effects, 97.5)

# Display key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Treatment Effect",
        f"{treatment_effect*100:.2f}pp",
        help="Increase in purchase completion from free shipping"
    )

with col2:
    st.metric(
        "95% Confidence Interval",
        f"[{ci_lower*100:.1f}, {ci_upper*100:.1f}]pp"
    )

with col3:
    st.metric(
        "Sample Size",
        f"{len(df_window):,}",
        help=f"Sessions in €{cutoff-bandwidth:.0f}-{cutoff+bandwidth:.0f} range"
    )

with col4:
    significant = "Yes" if ci_lower > 0 else "No"
    st.metric(
        "Statistically Significant",
        significant
    )

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["RDD Visualization", "ROI Calculator", "Heterogeneous Effects", "Method Comparison"])

with tab1:
    st.subheader("Purchase Completion by Cart Value")

    # Bin data for visualization
    df['cart_bin'] = pd.cut(df['cart_value'], bins=40)
    binned = df.groupby('cart_bin', observed=True).agg({
        'completed_purchase': 'mean',
        'cart_value': 'mean'
    }).reset_index()

    fig = go.Figure()

    # Scatter plot
    below_cutoff = binned[binned['cart_value'] < cutoff]
    above_cutoff = binned[binned['cart_value'] >= cutoff]

    fig.add_trace(go.Scatter(
        x=below_cutoff['cart_value'],
        y=below_cutoff['completed_purchase'] * 100,
        mode='markers',
        name='Control (No Free Shipping)',
        marker=dict(color='red', size=8, opacity=0.6)
    ))

    fig.add_trace(go.Scatter(
        x=above_cutoff['cart_value'],
        y=above_cutoff['completed_purchase'] * 100,
        mode='markers',
        name='Treatment (Free Shipping)',
        marker=dict(color='green', size=8, opacity=0.6)
    ))

    # Add cutoff line
    fig.add_vline(
        x=cutoff,
        line_dash="dash",
        line_color="blue",
        annotation_text="Free Shipping Cutoff (€50)"
    )

    # Fitted lines
    left_fit = df_window[df_window['treatment'] == 0].copy()
    right_fit = df_window[df_window['treatment'] == 1].copy()

    if len(left_fit) > 0:
        left_poly = np.polyfit(left_fit['cart_value'], left_fit['completed_purchase'], 1)
        left_x = np.linspace(cutoff - bandwidth, cutoff, 50)
        left_y = np.polyval(left_poly, left_x)
        fig.add_trace(go.Scatter(
            x=left_x, y=left_y * 100,
            mode='lines',
            name='Fitted (Control)',
            line=dict(color='red', width=2)
        ))

    if len(right_fit) > 0:
        right_poly = np.polyfit(right_fit['cart_value'], right_fit['completed_purchase'], 1)
        right_x = np.linspace(cutoff, cutoff + bandwidth, 50)
        right_y = np.polyval(right_poly, right_x)
        fig.add_trace(go.Scatter(
            x=right_x, y=right_y * 100,
            mode='lines',
            name='Fitted (Treatment)',
            line=dict(color='green', width=2)
        ))

    fig.update_layout(
        xaxis_title="Cart Value (€)",
        yaxis_title="Purchase Completion Rate (%)",
        height=500,
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show bandwidth effect
    st.markdown("### Bandwidth Sensitivity")

    bw_options = [5, 10, 15, 20, 25, 30]
    bw_results = []

    for bw in bw_options:
        df_temp = df[
            (df['cart_value'] >= cutoff - bw) &
            (df['cart_value'] <= cutoff + bw)
        ].copy()
        df_temp['cart_centered'] = df_temp['cart_value'] - cutoff
        df_temp['treat_x_cart'] = df_temp['treatment'] * df_temp['cart_centered']

        X_temp = df_temp[['cart_centered', 'treatment', 'treat_x_cart']]
        y_temp = df_temp['completed_purchase']
        model_temp = LinearRegression()
        model_temp.fit(X_temp, y_temp)

        bw_results.append({
            'Bandwidth': f"€{bw}",
            'Effect (pp)': model_temp.coef_[1] * 100,
            'Sample Size': len(df_temp)
        })

    bw_df = pd.DataFrame(bw_results)
    st.dataframe(bw_df, use_container_width=True)

with tab2:
    st.subheader("ROI Calculator")

    st.markdown("""
    This calculator estimates the financial impact of lowering the free shipping threshold from €50 to €49.

    **Key assumption**: The treatment effect applies to customers currently in the €45-50 range.
    """)

    # ROI calculation
    avg_cart = 50.0
    sessions_affected = monthly_sessions / 2
    baseline_conversion = 0.478

    # Incremental conversions
    additional_conversions = sessions_affected * treatment_effect

    # Revenue
    additional_revenue = additional_conversions * avg_cart
    additional_profit = additional_revenue * margin_rate

    # Cost
    baseline_conversions = sessions_affected * baseline_conversion
    total_shipments = baseline_conversions + additional_conversions
    monthly_shipping_subsidy = total_shipments * shipping_cost

    # Net
    net_monthly = additional_profit - monthly_shipping_subsidy
    net_annual = net_monthly * 12

    roi = (additional_profit / monthly_shipping_subsidy - 1) * 100 if monthly_shipping_subsidy > 0 else 0

    # Display results
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Revenue Impact")
        st.metric("Additional Conversions/Month", f"{additional_conversions:.0f}")
        st.metric("Additional Revenue/Month", f"€{additional_revenue:,.0f}")
        st.metric("Additional Profit/Month", f"€{additional_profit:,.0f}")

    with col2:
        st.markdown("#### Cost Impact")
        st.metric("Baseline Conversions", f"{baseline_conversions:.0f}")
        st.metric("Total Free Shipments", f"{total_shipments:.0f}")
        st.metric("Monthly Shipping Cost", f"€{monthly_shipping_subsidy:,.0f}")

    st.markdown("---")

    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric(
            "Net Monthly Impact",
            f"€{net_monthly:,.0f}",
            delta=f"{'Profit' if net_monthly > 0 else 'Loss'}"
        )

    with col4:
        st.metric("Net Annual Impact", f"€{net_annual:,.0f}")

    with col5:
        st.metric("ROI", f"{roi:.1f}%")

    # Verdict
    if net_monthly > 0:
        st.success(f"✅ **PROFITABLE**: Lowering threshold to €49 generates €{net_monthly:,.0f}/month in profit")
    else:
        st.error(f"❌ **UNPROFITABLE**: Lowering threshold to €49 loses €{abs(net_monthly):,.0f}/month")
        st.markdown("""
        **Why?** The shipping subsidy exceeds incremental profit. Most of the cost goes to
        *inframarginal* customers who would have purchased anyway.
        """)

    # Sensitivity analysis
    st.markdown("### Break-Even Analysis")

    breakeven_margin = monthly_shipping_subsidy / additional_revenue if additional_revenue > 0 else 0

    st.write(f"**Break-even margin**: {breakeven_margin*100:.1f}%")
    st.write(f"**Current margin**: {margin_rate*100:.0f}%")

    if margin_rate < breakeven_margin:
        st.warning(f"Your margins ({margin_rate*100:.0f}%) are below break-even ({breakeven_margin*100:.1f}%). This promotion is unprofitable.")
    else:
        st.success(f"Your margins ({margin_rate*100:.0f}%) exceed break-even. This promotion is profitable.")

with tab3:
    st.subheader("Treatment Effects by Customer Segment")

    st.markdown("""
    Does free shipping work equally well for all customers?
    """)

    # Segment by loyalty
    df_window['loyalty_segment'] = pd.cut(
        df_window['previous_purchases'],
        bins=[-1, 0, 2, 100],
        labels=['New', 'Occasional', 'Loyal']
    )

    segment_results = []

    for segment in ['New', 'Occasional', 'Loyal']:
        df_seg = df_window[df_window['loyalty_segment'] == segment]
        if len(df_seg) > 50:
            X_seg = df_seg[['cart_centered', 'treatment', 'treat_x_cart']]
            y_seg = df_seg['completed_purchase']
            model_seg = LinearRegression()
            model_seg.fit(X_seg, y_seg)

            segment_results.append({
                'Segment': segment,
                'Sample Size': len(df_seg),
                'Effect (pp)': model_seg.coef_[1] * 100,
                'Baseline Conversion %': df_seg[df_seg['treatment']==0]['completed_purchase'].mean() * 100
            })

    seg_df = pd.DataFrame(segment_results)

    # Display table
    st.dataframe(seg_df.round(2), use_container_width=True)

    # Visualize
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=seg_df['Segment'],
        y=seg_df['Effect (pp)'],
        marker_color=['lightcoral', 'lightsalmon', 'lightgreen'],
        text=seg_df['Effect (pp)'].round(1),
        textposition='inside'
    ))

    fig.update_layout(
        title="Treatment Effect by Customer Loyalty",
        xaxis_title="Customer Segment",
        yaxis_title="Treatment Effect (percentage points)",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **Interpretation**:
    - If effects are similar across segments, the promotion works universally
    - If effects differ, target the promotion to high-response segments
    """)

with tab4:
    st.subheader("RDD vs Alternative Methods")

    st.markdown("""
    Comparing Regression Discontinuity Design to simpler approaches.
    """)

    # Naive comparison (all data)
    naive_treated = df[df['treatment'] == 1]['completed_purchase'].mean()
    naive_control = df[df['treatment'] == 0]['completed_purchase'].mean()
    naive_effect = naive_treated - naive_control

    # RDD estimate
    rdd_effect = treatment_effect

    # Display comparison
    comparison_data = pd.DataFrame([
        {
            'Method': 'Naive Comparison (All Data)',
            'Estimate (pp)': naive_effect * 100,
            'Issue': 'Confounded by customer selection'
        },
        {
            'Method': 'RDD (Local Comparison)',
            'Estimate (pp)': rdd_effect * 100,
            'Issue': 'Valid under continuity assumption'
        }
    ])

    st.dataframe(comparison_data, use_container_width=True)

    st.markdown(f"""
    **Key Insight**:
    - Naive comparison: {naive_effect*100:.1f}pp
    - RDD estimate: {rdd_effect*100:.1f}pp
    - **Bias from selection**: {(naive_effect - rdd_effect)*100:.1f}pp

    RDD removes bias by comparing similar customers near the threshold.
    """)

    # Visualization
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=['Naive', 'RDD'],
        y=[naive_effect * 100, rdd_effect * 100],
        marker_color=['red', 'green'],
        text=[f"{naive_effect*100:.1f}pp", f"{rdd_effect*100:.1f}pp"],
        textposition='inside'
    ))

    fig.add_hline(y=8.0, line_dash="dash", line_color="blue",
                  annotation_text="True Effect (8.0pp)")

    fig.update_layout(
        title="Method Comparison",
        yaxis_title="Estimated Effect (percentage points)",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
**About this analysis**:
This dashboard presents results from a Regression Discontinuity Design analysis of free shipping impact.
The analysis uses synthetic data with a known 8pp treatment effect for validation.

**Methodology**: RDD exploits the sharp assignment of free shipping at €50 to estimate causal effects by comparing customers just above and below the threshold.

**Limitations**:
- Results apply only to customers near €50
- Assumes no precise manipulation of cart value
- Synthetic data simplifies real behavioral dynamics
""")
