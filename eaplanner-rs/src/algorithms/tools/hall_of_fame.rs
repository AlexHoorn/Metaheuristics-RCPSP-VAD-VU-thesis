use crate::algorithms::tools::individual::Individual;

pub struct HallOfFame {
    items: Vec<Individual>,
    maxsize: usize,
}

impl HallOfFame {
    pub fn new(maxsize: usize) -> Self {
        Self {
            items: Vec::new(),
            maxsize,
        }
    }

    pub fn get(&self, index: usize) -> &Individual {
        &self.items[index]
    }

    pub fn update(&mut self, individual: &Vec<Individual>) {
        for i in individual {
            self.items.push(i.clone());
        }
        // sort lexicographically
        self.items
            .sort_by(|a, b| a.fitness.partial_cmp(&b.fitness).unwrap());
        self.items.truncate(self.maxsize as usize);
    }
}
