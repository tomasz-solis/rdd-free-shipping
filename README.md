# Learning RDD: Free Shipping Impact Analysis

## What This Project Is

I'm learning Regression Discontinuity Design (RDD) from scratch by working through a realistic business problem: does free shipping actually cause customers to complete purchases, or does it just attract people who would buy anyway?

This is my learning portfolio showing how I built understanding of RDD step-by-step, including the analytical decisions I made, what surprised me, and what I'd do differently next time.

## Why This Approach

**Learning method:** I'm using synthetic data where I know the true treatment effect (8 percentage points). This lets me validate whether my RDD analysis actually recovers the truth. It's like practicing with the answer key before tackling real-world messiness.

**Why RDD:** It's one of the most intuitive quasi-experimental designs. When you can't run an A/B test but have a sharp policy threshold (like €50 for free shipping), you can still estimate causal effects by comparing customers just above vs just below that threshold.

**Portfolio goal:** Show that I can think rigorously about causal inference, not just execute code. The notebooks document my thought process, analytical choices, and what I learned along the way.

## The E-commerce Scenario

**Business Context:** Online retailer offers free shipping on orders €50+

**Running Variable:** Cart value (€5-200)

**Treatment Assignment:**
- Cart < €50 → Standard shipping (€5.95)
- Cart ≥ €50 → Free shipping

**Outcome:** Purchase completion (did they checkout or abandon?)

**The Causal Question:** For customers near €50, does free shipping actually cause them to buy, or would they have bought anyway?

**Key RDD Assumption:** Customers with €48 carts are essentially identical to customers with €52 carts, except for shipping cost. Near the threshold, treatment is effectively random.

## What I've Built

### Setup and Data Generation
- Designed realistic data generating process with 10,000 shopping sessions
- Included customer demographics (age, tenure, purchase history)
- Added product categories and realistic heterogeneity
- Built in a known 8pp treatment effect to validate methods

### Visualization and Assumption Validation
- Created RDD discontinuity plots showing the jump at €50
- Tested for manipulation (McCrary density test)
- Checked covariate balance
- Validated that assumptions hold

### Formal Estimation and Robustness
- Ran proper RDD regression with standard errors and confidence intervals
- Tested sensitivity to bandwidth choice (€5 to €30)
- Tested sensitivity to covariate controls
- Ran two placebo tests (fake cutoffs at €40 and €60)

## Key Results

### Main Finding
**Free shipping increases purchase completion by 6.84 percentage points for customers near the €50 threshold.**

- True effect (built into data): 8.0pp
- My RDD estimate: 6.84pp
- 95% Confidence Interval: [1.87pp, 11.81pp]
- p-value: 0.007 (highly significant)
- Estimation error: 1.16pp

**Translation:** For every 100 customers with €48 carts who don't buy (completion rate ~48%), about 7 more would complete their purchase if they had €52 carts and got free shipping (completion rate ~55%).

### Why the Naive Comparison Fails

If I just compared everyone who got free shipping vs everyone who didn't:

- Paid shipping group: 44.8% completion
- Free shipping group: 58.2% completion
- Naive difference: 13.4pp

**Problem:** This confounds treatment effect with customer type. People with €150 carts are fundamentally more committed buyers than people with €20 carts. The 13.4pp difference includes both the shipping effect AND the fact that high cart-value customers are different people.

**RDD solution:** Compare ONLY customers near €50 (€48 vs €52) where confounding is minimal. This gives the more accurate 6.84pp estimate.

## Assumption Validation

### 1. No Manipulation (Local Randomization)

**Test:** McCrary density test for bunching at cutoff

**Results:**
- Carts €48-50: 350 sessions
- Carts €50-52: 308 sessions
- Ratio: 0.88 (no excess at threshold)
- Exact €50.00 carts: 0.03% of total

**Interpretation:** Even though customers know about free shipping, they can't precisely control their cart values. Random variation in exact prices, availability, and browsing creates enough noise that treatment assignment near €50 is effectively random.

**Learning:** Knowledge of policy ≠ violation of assumptions. What matters is whether customers can PRECISELY manipulate which side of €50 they land on. They can't.

### 2. Covariate Balance (Continuity)

**Test:** Check if customer characteristics are smooth at €50

**Results:**
- Account tenure: Balanced (p=0.36)
- Items in cart: Balanced (p=0.62)
- Previous purchases: Slight imbalance (p=0.043, diff=0.28 purchases)

**Interpretation:** Customers just below and above €50 are highly similar. The previous purchases imbalance is statistically significant but practically negligible (2.46 vs 2.18 purchases).

**Learning:** Statistical significance (p<0.05) doesn't automatically mean practical significance. A 0.28 purchase difference is trivial.

### 3. Visual Discontinuity

**Test:** Plot completion rates vs cart value

**Results:** Clear jump at €50, smooth trends on both sides

**Interpretation:** The discontinuity is exactly where treatment kicks in, not elsewhere. This is what we want to see.

## Robustness Checks

### Bandwidth Sensitivity

**Test:** Does estimate change with different bandwidth choices?

**Results:**

| Bandwidth | Sample | Estimate | 95% CI | p-value |
|-----------|--------|----------|---------|---------|
| €5 | 1,594 | 6.83pp | [-3.01, 16.66] | 0.174 |
| €10 | 3,134 | 4.12pp | [-2.77, 11.02] | 0.241 |
| €15 | 4,590 | 7.00pp | [1.31, 12.67] | 0.016 |
| €20 | 5,835 | 6.84pp | [1.87, 11.81] | 0.007 |
| €25 | 6,832 | 6.62pp | [2.11, 11.13] | 0.004 |
| €30 | 7,613 | 7.72pp | [3.53, 11.90] | 0.0003 |

**Key finding:** Estimates stable across reasonable bandwidths (6-8pp range). All confidence intervals include the true 8pp effect.

**Learning:** The bias-variance tradeoff is real. Narrow bandwidths are noisy (BW=5: wide CI, not significant). Wide bandwidths are precise but could introduce bias. I chose BW=20 as a reasonable middle ground.

### Covariate Control

**Test:** Does controlling for the slightly imbalanced covariate change results?

**Results:**
- Without control: 6.84pp
- With previous_purchases control: 6.89pp
- Difference: 0.05pp

**Learning:** The slight imbalance doesn't bias my estimate. RDD's local comparison already handles this. In RDD, controls are for precision, not identification (unlike in standard regression).

### Placebo Tests

**Test:** Look for discontinuities at fake cutoffs where treatment doesn't change

**Placebo 1 (€40):** 
- Both sides have paid shipping
- Estimate: Small, not significant (p>0.05)
- Expected: No effect ✓

**Placebo 2 (€60):**
- Both sides have free shipping
- Estimate: Small, not significant (p>0.05)
- Expected: No effect ✓

**Real cutoff (€50):**
- Treatment changes here
- Estimate: 6.84pp, highly significant (p=0.007)
- Expected: Real effect ✓

**Learning:** This validates my method isn't finding spurious discontinuities. The effect at €50 is real, not a statistical artifact.

## What I Learned

### Conceptual Insights

1. **RDD estimates local effects (LATE), not global effects (ATE).** My 6.84pp applies to customers NEAR €50, not all customers. Can't assume it applies to €20 or €100 carts.

2. **RDD doesn't require controlling for confounders like regression does.** The discontinuity design handles confounding by comparing nearly identical customers. This is powerful.

3. **Manipulation test checks running variable density, not outcome.** Common confusion: you check if CART VALUES bunch (manipulation test), not if PURCHASE RATES jump (that's the treatment effect you want!).

4. **Statistical significance ≠ practical significance.** The covariate imbalance taught me this. p=0.043 sounds important, but 0.28 purchases difference is negligible.

5. **Robustness checks build credibility.** Showing what you DIDN'T find (placebo tests) is as important as showing what you DID find.

### Technical Skills

- Implemented RDD from scratch in Python (no rdrobust package)
- Created publication-quality visualizations with Plotly
- Ran proper sensitivity analyses (bandwidth, controls, placebos)
- Used statsmodels for regression with standard errors
- Wrote clean, documented code with proper functions

### What Surprised Me

- How well RDD recovered the true 8pp effect despite noise and confounding
- How little the covariate imbalance actually mattered
- How narrow bandwidths can be too noisy even with 10,000 observations
- That placebo tests are such powerful validation tools

### What I'd Do Differently

**In this analysis:**
- Use data-driven and not arbitrary method for optimal bandwidth selection - possibly Imbens-Kalyanaraman
- Test more placebo cutoffs to be even more thorough
- Check for heterogeneous effects by subgroup

**In real-world application:**
- Dig deeper into business context (what else might change at €50?)
- Interview customers about shopping behavior
- Check for seasonal patterns or promotional periods
- Be more cautious about extrapolating to all customers

## Technical Implementation

### Data Generation
```python
from src.generate_data import generate_rdd_ecommerce_data

df = generate_rdd_ecommerce_data(
    n_sessions=10000,
    cutoff=50.0,
    treatment_effect=0.08,  # 8pp
    random_seed=14
)
```

### RDD Estimation
```python
# Filter to bandwidth window
df_rdd = df[(df['cart_value'] >= 30) & (df['cart_value'] <= 70)]

# Center at cutoff
df_rdd['cart_centered'] = df_rdd['cart_value'] - 50

# Create interaction
df_rdd['treat_x_cart'] = df_rdd['treatment'] * df_rdd['cart_centered']

# Run regression
model = smf.ols(
    'completed_purchase ~ cart_centered + treatment + treat_x_cart',
    data=df_rdd
).fit()

# Extract treatment effect
treatment_effect = model.params['treatment']
```

## Project Structure

```
rdd-free-shipping/
├── README.md                           # This file
├── data/
│   └── rdd_ecommerce.csv              # Synthetic data (10k sessions)
├── notebooks/
│   ├── 01_data_generation.ipynb       # Data generation and validation
│   └── 02_rdd_estimation.ipynb        # Analysis, sensitivity, robustness
├── outputs/
│   └── figures/                       # All visualizations
│       ├── 01_purchase_completion_by_cart_value.png
│       ├── 02_manipulation_test.png
│       ├── 03_rdd_estimate_vs_true_effect.png
│       ├── 04_bandwidth_sensitivity_analysis.png
│       └── 05_placebo_tests.png
└── src/
    ├── generate_data.py               # Data generation with full docstrings
    └── __init__.py
```

## Key Files

**Notebook 01:** Data generation, exploration, manipulation testing
**Notebook 02:** RDD estimation, sensitivity analysis, placebo tests, full results

**All notebooks include:**
- Explanatory markdown showing my thought process
- Reflections on what I found vs expected
- Clear documentation of analytical choices
- Learning-focused tone (not expert-level polish)

## Why Synthetic Data Works for Learning

**Advantages:**
- I know the true effect (8pp), so I can validate my methods
- I can test what happens when assumptions are violated
- No privacy concerns or data access issues
- Can experiment freely with different scenarios

**Translation to real work:**
- Same workflow applies to actual transaction data
- Same assumptions need validation
- Same sensitivity checks are required
- Methods transfer directly

**The difference:** In real analysis, you don't have ground truth. You estimate effects, you don't validate them. But the rigorous thinking is identical.

## Methodology Notes

### Why Not Just Use a Package?

I could have used the `rdrobust` package in R or Python, which automates much of this. I chose to implement from scratch because:

1. **Learning:** Building it yourself forces you to understand what's actually happening
2. **Transparency:** Every analytical choice is explicit and documented
3. **Flexibility:** Easy to customize for specific business contexts
4. **Portfolio:** Shows deeper understanding than just calling library functions

**When I'd use packages:** Production analysis at work where robustness and established methods matter more than learning.

### Causal Inference Philosophy

This project reflects my approach to causal inference:

1. **Start with a clear causal question:** "Does free shipping CAUSE purchases?"
2. **Identify the identification strategy:** RDD exploits threshold discontinuity
3. **State assumptions explicitly:** Continuity, local randomization, LATE
4. **Test assumptions rigorously:** Manipulation, covariate balance, visual checks
5. **Show robustness:** Bandwidth, controls, placebo tests
6. **Interpret honestly:** LATE caveat, limitations, uncertainty
7. **Communicate clearly:** What did I find? What does it mean? What are the limits?

## References

**Primary learning resources:**
- *Causal Inference: The Mixtape* by Scott Cunningham (main textbook)
- *Causal Inference in Python* by Matheus Facure Alves

**Why e-commerce context:**
- Free shipping is economically significant and widely used
- The scenario is intuitive and doesn't require domain expertise
- Good vehicle for learning RDD while staying grounded in business

## A Note on Learning vs Expertise

This project shows my learning process, not expert-level work. You'll see:
- Honest reflections on what confused me
- Decisions I'd make differently next time
- Questions I'm still working through
- Authentic "learning in progress" tone

**This is intentional.** The goal is demonstrating how I think about causal inference, build understanding, and validate my work - not pretending I'm an econometrics PhD.

If you're reviewing this as a hiring manager: I'm a strong Python-using analyst who's serious about learning causal inference rigorously. I can explain my reasoning, test my assumptions, and communicate results clearly. That's the skill set that matters.

## Contact

**Tomasz Solis**
- Email: tomasz.solis@gmail.com
- LinkedIn: [linkedin.com/in/tomaszsolis](https://www.linkedin.com/in/tomaszsolis/)
- GitHub: [github.com/tomasz-solis](https://github.com/tomasz-solis)