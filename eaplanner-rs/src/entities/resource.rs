use std::{cell::RefCell, rc::Rc};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Resource {
    name: RefCell<String>,
    capacity: RefCell<i32>,
}

impl Resource {
    pub fn new(name: String, capacity: i32) -> Rc<Resource> {
        Rc::new(Self {
            name: RefCell::new(name),
            capacity: RefCell::new(capacity),
        })
    }

    pub fn name(&self) -> String {
        self.name.borrow().clone()
    }

    pub fn capacity(&self) -> i32 {
        *self.capacity.borrow()
    }
}
