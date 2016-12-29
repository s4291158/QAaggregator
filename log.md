# Aim: Maximum views on my answer

## Experiment 1

### Part 1
**Hypothesis:** High views on question results in high views on answers

**Approach:** 
    1. Grab top (max 6) answers from each question
    2. Obtain datasets for `mean answer view count` and `question's view count`
    3. Normalise datasets
    4. Use Pearson's r to determine correlation between two datasets
    
**Conclusion:** Medium association (r=0.488) between question and answer view count

**Evidence:** `from quora.executes import Ex1; Ex1().calculate_r()`

### Part 2
**Hypothesis:** 