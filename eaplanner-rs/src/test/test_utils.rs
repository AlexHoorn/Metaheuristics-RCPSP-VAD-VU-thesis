use crate::algorithms::tools::utils::is_smaller_or_equal_lexicographic;

#[test]
fn test_is_smaller_or_equal_lexicographic() {
    let base = vec![1, 1, 1];
    let equal = vec![1, 1, 1];
    let smaller1 = vec![0, 2, 2];
    let smaller2 = vec![1, 1, 0];
    let larger1 = vec![1, 2, 4];
    let larger2 = vec![2, 1, 1];

    assert_eq!(is_smaller_or_equal_lexicographic(&base, &equal), true);
    assert_eq!(is_smaller_or_equal_lexicographic(&base, &smaller1), false);
    assert_eq!(is_smaller_or_equal_lexicographic(&base, &smaller2), false);
    assert_eq!(is_smaller_or_equal_lexicographic(&base, &larger1), true);
    assert_eq!(is_smaller_or_equal_lexicographic(&base, &larger2), true);
}
