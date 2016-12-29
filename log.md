# Aim: Maximum views on my answers

## Definitions

**question infancy period:** 2 days
**developing question:** A question that has little to no answers, likely to be within infancy period
**developed question:** A question that has many answers, likely to be over infancy period
**top answers:** Top *(max 6, scrape limit)* answers to a given question

## Note
* Code based evidence requires inspection of the code

## Experiment 1
**Results:** Answer questions with higher view count

### Part 1
**Hypothesis:** For developed questions, high views on question results in high views on top answers

**Approach:** 

    1. Grab top answers from each of 250 developed questions
    2. Obtain datasets for `mean answer view count` and `question's view count`
    3. Normalise datasets
    4. Use Pearson's r to determine correlation between two datasets
    
**Conclusion:** Medium association (0.3<r=0.488<0.5) between question and top answers view count

**Evidence:** `from quora.ex1.scripts import P1; P1().calculate_r()`

### Part 2
**Hypothesis:** Pearson's r remains same or improves for developing questions

**Approach:**

    1. Grab top answers from each of 250 developing questions
    2. Obtain datasets for `mean answer view count` and `question's view count`
    3. Normalise datasets
    4. Use Pearson's r to determine correlation between two datasets
    5. Compare Pearson's r with that of the developed questions
    
**Conclusion:** Pearson's r is higher (r=0.682) for developing questions 

**Evidence:** `from quora.ex1.scripts import P2; P2().calculate_r()`

