use std::collections::HashMap;

pub fn calculate_rank(entries: &Vec<Vec<i32>>) -> Vec<usize> {
    // get the unique entries
    let mut unique_entries: Vec<Vec<i32>> = Vec::new();
    for entry in entries {
        if !unique_entries.contains(entry) {
            unique_entries.push(entry.clone());
        }
    }

    // sort the unique entries
    unique_entries.sort();

    // create a hashmap to store the rank of each unique entry
    let mut rank_map: HashMap<Vec<i32>, usize> = HashMap::new();
    for (i, entry) in unique_entries.iter().enumerate() {
        rank_map.insert(entry.clone(), i);
    }

    // get the rank of each entry
    let mut ranks: Vec<usize> = Vec::new();
    for entry in entries {
        ranks.push(*rank_map.get(entry).unwrap());
    }

    ranks
}
