pub fn is_smaller_or_equal_lexicographic(to_check: &Vec<i32>, check_against: &Vec<i32>) -> bool {
    // Return true if both are equal
    if to_check == check_against {
        return true;
    }

    // Find indexes of elements that are not equal
    let mut indexes = Vec::new();
    for i in 0..to_check.len() {
        if to_check[i] != check_against[i] {
            indexes.push(i);
        }
    }

    if indexes.len() == 0 {
        return false;
    }

    // Check if first element is smaller
    to_check[indexes[0]] < check_against[indexes[0]]
}
