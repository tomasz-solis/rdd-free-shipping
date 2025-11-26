# Regression Discontinuity Design: Free Shipping Impact on Purchase Behavior

## Project Overview

This project applies Regression Discontinuity Design (RDD) to evaluate the causal impact of free shipping on e-commerce purchase completion and customer behavior. The analysis examines whether offering free shipping above a cart value threshold increases conversion rates and affects customer lifetime value.

## Learning Context

This is a learning project focused on mastering causal inference methods, specifically RDD. The dataset is synthetic and designed to mirror realistic e-commerce shopping behavior while providing controlled conditions for learning and validating the methodology.

The project follows a progressive approach:
- Clean RDD with no violations (current phase)
- Adding complexity (manipulation, covariates, robustness checks)
- Fuzzy RDD and treatment heterogeneity
- Full realistic scenario with multiple complications

## Research Question

**What is the causal effect of free shipping eligibility on purchase completion rates for customers with cart values near the €50 threshold?**

## Methodology

**Design:** Sharp Regression Discontinuity Design

**Running Variable:** Pre-checkout cart value in euros, ranging from €0-200

**Cutoff:** €50

**Treatment:**
- Below €50: Standard shipping fee (€5.95)
- At or above €50: Free shipping (€0)

**Outcome:** Purchase completion (binary: completed checkout vs abandoned cart)

**Sample Size:** 10,000 shopping sessions

## Business Context

Many e-commerce retailers use free shipping thresholds to incentivize larger purchases. However, it's unclear whether free shipping actually causes customers to complete purchases, or simply attracts customers who would have purchased anyway. RDD allows us to isolate the causal effect by comparing customers just below and just above the threshold.

Understanding this effect helps answer critical business questions:
- Does free shipping increase conversion for marginal shoppers?
- What is the ROI of offering free shipping?
- Where should we set the threshold to maximize profit?
- Are customers gaming the system by adding items to reach the threshold?

## Key Assumptions

**Continuity Assumption:** In the absence of free shipping, purchase completion probability would be smooth at the €50 cutoff.

**Local Randomization:** Customers with cart values just below €50 (e.g., €48) are essentially identical to those just above €50 (e.g., €52) in all characteristics except shipping cost.

**No Manipulation:** Customers cannot precisely control their cart value to be exactly at €50 (though strategic behavior near the threshold is interesting to study).

## Project Structure

```
rdd-free-shipping/
├── data/              # Generated datasets
├── notebooks/         # Analysis notebooks
│   ├── 01_data_generation.ipynb
│   ├── 02_exploratory_analysis.ipynb (planned)
│   └── 03_rdd_estimation.ipynb (planned)
└── src/              # Reusable functions
```

## Progress Log

### 2024-11-26
- Initial project setup
- Defined research question and methodology
- Established data generating process
- Created project structure

## Technical Approach

The analysis will cover:
1. Data generation with known treatment effects
2. Visual inspection of the discontinuity
3. Covariate balance checks (customer demographics, product categories)
4. Bandwidth selection (data-driven methods)
5. Local linear regression estimation
6. Manipulation testing (McCrary density test for bunching at threshold)
7. Sensitivity analysis (varying bandwidths, functional forms)
8. Validation against true treatment effect

## Why This Matters

Free shipping thresholds are ubiquitous in e-commerce, but the causal impact is often assumed rather than rigorously measured. This analysis demonstrates:
- How to separate selection effects from true causal effects
- How to test for strategic customer behavior
- How to quantify ROI of shipping promotions
- How to optimize threshold placement

RDD is particularly well-suited for this problem because:
- Thresholds create sharp discontinuities in treatment
- Cart values are continuous and quasi-randomly distributed near the cutoff
- Customers near the threshold are plausibly similar
- No randomized experiment is required

## Data Generating Process

The synthetic data includes:
- Customer demographics (age, account tenure, previous purchases)
- Product categories in cart (electronics, fashion, home goods)
- Shopping behavior (time on site, items viewed)
- Cart value (continuous running variable)
- Treatment assignment (free shipping based on threshold)
- Purchase outcome (binary completion indicator)

The true treatment effect is set at 8 percentage points increase in conversion, allowing validation of RDD estimates.

## Notes

The synthetic data allows for validation of methods against known ground truth, which is pedagogically valuable but impossible with real observational data.

The focus is on methodological rigor, clear assumptions, and honest interpretation of limitations rather than sophisticated modeling or advanced techniques. The e-commerce context provides intuitive understanding while maintaining analytical depth.