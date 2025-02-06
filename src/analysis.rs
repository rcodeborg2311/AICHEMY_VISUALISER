use std::cmp::Reverse;
use std::collections::{BinaryHeap, HashMap, HashSet};
use lambda_calculus::Term;

// Note: These need to be available in the soup.rs implementation
use crate::soup::Soup;
use crate::utils::HeapObject;

// Move all the analysis functions into the Soup implementation in soup.rs
// This is better as these are methods on the Soup type rather than standalone functions
impl Soup {
    /// Returns a set of unique expressions within the soup.
    pub fn unique_expressions(&self) -> HashSet<Term> {
        HashSet::<Term>::from_iter(self.expressions().cloned())
    }

    /// Calculates the frequency of each expression within the soup.
    pub fn expression_counts(&self) -> HashMap<Term, u32> {
        let mut map = HashMap::<Term, u32>::new();
        for expr in self.expressions().cloned() {
            *map.entry(expr).or_default() += 1;
        }
        map
    }

    /// Finds the `k` most frequent expressions in the soup.
    /// Uses a min-heap to efficiently manage the top `k` expressions.
    pub fn k_most_frequent_exprs(&self, k: usize) -> Vec<Term> {
        let mut map = HashMap::<&Term, u32>::new();
        for x in self.expressions() {
            *map.entry(x).or_default() += 1;
        }

        // Min-heap to store the most frequent expressions
        let mut heap = BinaryHeap::with_capacity(k + 1);
        for (x, count) in map.into_iter() {
            heap.push(Reverse(HeapObject::new(count, x)));
            if heap.len() > k {
                heap.pop();
            }
        }

        // Collect the most frequent terms as a vector
        heap.into_sorted_vec()
            .into_iter()
            .map(|r| r.0.to_tuple().1.clone())
            .collect()
    }

    /// Calculates the entropy of the soup population based on expression frequencies.
    pub fn population_entropy(&self) -> f32 {
        let mut entropy = 0.0;
        let n = self.len() as f32;
        for &count in self.expression_counts().values() {
            let pi = count as f32 / n;
            entropy -= pi * pi.log2();  // Using log2 for bits (Shannon entropy)
        }
        entropy
    }

    /// Computes the Jaccard index (similarity) between two soup populations.
    pub fn jaccard_index(&self, other: &Soup) -> f32 {  // Fixed typo in function name
        let self_counts = self.expression_counts();
        let other_counts = other.expression_counts();

        let mut intersection = 0;
        for (expr, &count) in self_counts.iter() {
            if let Some(&other_count) = other_counts.get(expr) {
                intersection += count.min(other_count);
            }
        }

        let union = self.len() + other.len() - intersection as usize;
        if union > 0 {
            intersection as f32 / union as f32
        } else {
            1.0  // Both soups are identical if union is zero
        }
    }
}