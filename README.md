# Regression Discontinuity Design: Free Shipping Impact Analysis

## What This Project Is About

This project uses Regression Discontinuity Design (RDD) to answer a straightforward question: does offering free shipping actually cause customers to complete their purchases, or does it just attract people who were going to buy anyway?

Many e-commerce sites use free shipping thresholds (like "free shipping over €50"), but the causal impact is rarely measured rigorously. This analysis demonstrates how to isolate the true effect using quasi-experimental methods.

## Why I Built This

I'm learning causal inference methods from first principles. RDD is one of the most intuitive quasi-experimental designs - if you can't run a randomized experiment, but you have a sharp policy threshold, you can still estimate causal effects by comparing people just above and below that threshold.

I'm using synthetic data, which allows me to validate my methods against known ground truth. Real-world RDD analysis would follow the same workflow, just with messier data and more uncertainty.

## The Setup

**Running Variable:** Cart value in euros (continuous, €5-200)

**Treatment Assignment:** 
- Carts below €50: Standard shipping fee (€5.95)
- Carts at or above €50: Free shipping

**Outcome:** Purchase completion (binary: did they complete checkout or abandon?)

**Key Assumption:** Customers with cart values just below €50 (say, €48) should be similar to customers just above €50 (say, €52) in every way except shipping cost. Near the threshold, treatment is effectively random.

## What I've Done So Far

### Project Setup
- Designed the data generating process
- Created synthetic e-commerce shopping sessions with realistic heterogeneity
- Set up project structure and documentation

### Visualization and Validation
- Generated 10,000 synthetic shopping sessions
- Created RDD discontinuity plots showing treatment effect
- Validated key RDD assumptions

## Key Results (So Far)

**Main Finding:**
Free shipping increases purchase completion by approximately 6.8 percentage points for customers with cart values near the €50 threshold.

**True effect (built into synthetic data):** 8.0 percentage points  
**My RDD estimate:** 6.8 percentage points  
**Estimation error:** 1.2 percentage points

This is quite good - the estimate recovered the true causal effect with high accuracy despite random noise in the data.

## Assumption Checks

For RDD to give valid causal estimates, three key assumptions must hold:

**1. Continuity (No Jump Without Treatment)**

The purchase completion rate should be smooth at €50 if free shipping didn't exist. Both visual inspection and local linear regression confirm smooth trends on both sides of the cutoff, with a clear discontinuous jump at exactly €50.

**2. Covariate Balance (Customers Are Similar Near Cutoff)**

Tested three customer characteristics:
- Account tenure: Balanced (p=0.36)
- Items in cart: Balanced (p=0.62)
- Previous purchases: Slight imbalance (p=0.043)

The previous purchases imbalance is statistically significant but small in practical terms (2.46 vs 2.18 purchases, difference of 0.28). Customers just below and above the threshold are highly similar, supporting the local randomization assumption.

**3. No Manipulation (Customers Aren't Gaming the System)**

Tested for suspicious bunching at €50:
- Density ratio (€48-50 vs €50-52): 0.88 (no excess carts at threshold)
- Carts at exactly €50.00: Only 0.03% of all sessions
- Visual inspection: Smooth density through the cutoff

No evidence that customers are strategically adding items to reach the free shipping threshold.

## Why These Checks Matter

Without these validations, I couldn't confidently claim the 6.8pp effect is causal. The checks rule out alternative explanations:

- If covariates jumped at €50, different types of customers might be on each side (confounding)
- If customers bunched at €50, they're self-selecting into treatment (selection bias)
- If the outcome wasn't smooth, something else changes at €50 besides shipping (violation of continuity)

All checks passed (with minor noted caveats), so the RDD design is valid.

## The Naive Comparison Problem

If I just compared all customers who got free shipping vs all who didn't:

- Control group (paid shipping): 44.8% completion
- Treatment group (free shipping): 58.2% completion
- Naive difference: 13.4 percentage points

But this is wrong. The treatment group includes people with €150 carts (highly committed buyers), while the control group includes people with €20 carts (casual browsers). Part of that 13.4pp difference is because they're different types of customers, not because of free shipping.

RDD fixes this by comparing customers near the cutoff:
- Control (€45-50): ~48% completion
- Treatment (€50-55): ~55% completion  
- RDD estimate: 6.8 percentage points

Much closer to the truth (8.0pp).

## Technical Approach

**Data Generation:**
- 10,000 shopping sessions
- Customer demographics (age, account tenure, purchase history)
- Product categories (Electronics, Fashion, Home & Garden, Books, Sports)
- Realistic noise and heterogeneity in purchase propensity

**Estimation:**
- Local linear regression with bandwidth = €20
- Separate fits on each side of cutoff
- Treatment effect = discontinuity at €50

**Visualization:**
- Binned scatter plots with fitted regression lines
- Covariate balance plots
- Density histograms for manipulation testing

## What's Next

**Formal Estimation (Planned)**
- Proper standard errors and confidence intervals
- Optimal bandwidth selection (data-driven methods)
- Sensitivity analysis (how do estimates change with bandwidth?)
- Robustness checks (placebo cutoffs, donut-hole RDD)
- Controlling for the slight covariate imbalance to verify it doesn't matter

**Advanced Topics (Planned)**
- Treatment effect heterogeneity (does free shipping work better for some customers?)
- Fuzzy RDD (what if treatment assignment isn't perfect?)
- Multiple outcomes (time to purchase, cart abandonment reasons)

## Why This Matters

Free shipping thresholds are ubiquitous in e-commerce. Understanding the causal impact helps answer:
- What's the ROI of offering free shipping?
- Where should we set the threshold?
- Which customers benefit most?
- Are we losing money on shipping, or gaining it through increased conversion?

More broadly, this demonstrates how to:
- Design and validate quasi-experiments
- Separate causal effects from selection effects
- Test assumptions rigorously before making causal claims
- Communicate limitations honestly

## Project Structure

```
rdd-free-shipping/
├── README.md                          # This file
├── data/
│   └── rdd_ecommerce.csv              # Generated synthetic data
├── notebooks/
│   └── 01_data_generation.ipynb       # Day 1-2 work
└── src/
    ├── generate_data.py               # Data generation functions
    └── __init__.py
```

## How to Run

**Requirements:**
- Python 3.8+
- See requirements.txt for dependencies

**Generate data and run analysis:**
```python
from src.generate_data import generate_rdd_ecommerce_data

# Generate synthetic data
df = generate_rdd_ecommerce_data(
    n_sessions=10000,
    cutoff=50.0,
    treatment_effect=0.08,
    random_seed=14
)

# See notebooks for full analysis workflow
```

## Notes on Synthetic Data

Using synthetic data has pedagogical advantages:
- I know the true treatment effect (8.0pp), so I can validate my methods
- I can add violations (manipulation, confounding) and see how they break RDD
- I can experiment with different scenarios without privacy concerns

Real-world applications would follow the same workflow but with:
- Actual transaction data from an e-commerce platform
- Unknown true effects (estimating, not validating)
- Messier data (missing values, outliers, measurement error)
- More uncertainty about assumptions

The methods transfer directly - this is genuine causal inference practice, not toy analysis.

## Learning Approach

This project follows a structured progression:
1. Start with clean data and perfect conditions
2. Add complications one at a time
3. Build up to realistic messy scenarios

The goal is not to showcase advanced techniques, but to demonstrate rigorous thinking:
- Clear assumptions
- Thorough validation
- Honest interpretation of limitations
- Transparent about uncertainty

These are the skills that matter in applied causal inference work.

## References and Resources

**Learning Resources:**
- Causal Inference: The Mixtape (Cunningham)
- Causal Inference in Python (Facure Alves)

**Classic RDD Applications:**
- Minimum legal drinking age studies
- School admission cutoffs and educational outcomes
- Election threshold discontinuities

**Why This Context:**
The free shipping problem is intuitive and economically significant, making it a good vehicle for learning RDD while staying grounded in practical business questions.

## Contact and Feedback

If you spot errors in my methodology or have suggestions for improvement, I'd welcome the feedback.

The point is not to present polished final work, but to show the actual process of learning causal inference - including the mistakes, iterations, and refinements along the way.
