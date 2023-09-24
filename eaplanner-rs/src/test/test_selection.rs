use crate::algorithms::tools::selection::calculate_rank;

#[test]
fn test_calculate_rank() {
    let entries: Vec<Vec<i32>> = vec![
        vec![1, 2, 3], // 0
        vec![4, 5, 6], // 1
        vec![1, 2, 3], // 0
        vec![7, 8, 9], // 3
        vec![4, 5, 6], // 1
        vec![4, 6, 6], // 2
    ];

    let ranks = calculate_rank(&entries);
    assert_eq!(ranks, vec![0, 1, 0, 3, 1, 2]);
}

#[test]
fn test_calculate_rank_empty() {
    let entries: Vec<Vec<i32>> = Vec::new();

    let ranks = calculate_rank(&entries);
    assert_eq!(ranks, Vec::<usize>::new());
}

#[test]
fn test_calculate_rank_single_entry() {
    let entries: Vec<Vec<i32>> = vec![vec![1, 2, 3]];

    let ranks = calculate_rank(&entries);
    assert_eq!(ranks, vec![0]);
}
