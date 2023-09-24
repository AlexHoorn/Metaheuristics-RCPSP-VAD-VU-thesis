use std::{
    cell::RefCell,
    rc::Rc,
    sync::atomic::{AtomicUsize, Ordering},
};

static ASG_ID_ITER: AtomicUsize = AtomicUsize::new(0);

#[derive(Debug, Default)]
pub struct Assignment {
    hours: RefCell<i32>,
    id: RefCell<usize>,
    start: RefCell<i32>,
    duration: RefCell<i32>,
    hours_per_day: RefCell<i32>,
}

impl Assignment {
    pub fn new(id: Option<usize>, hours: i32) -> Rc<Self> {
        let id = match id {
            Some(id) => id,
            None => ASG_ID_ITER.fetch_add(1, Ordering::Relaxed),
        };
        Rc::new(Self {
            hours: RefCell::new(hours),
            id: RefCell::new(id),
            ..Default::default()
        })
    }

    pub fn id(&self) -> usize {
        *self.id.borrow()
    }

    pub fn hours(&self) -> i32 {
        *self.hours.borrow()
    }

    pub fn set_hours(&self, value: i32) {
        *self.hours.borrow_mut() = value;
        self.set_hours_per_day();
    }

    fn set_hours_per_day(&self) {
        let hours_per_day = self.hours() as f32 / self.duration() as f32;
        *self.hours_per_day.borrow_mut() = hours_per_day.ceil() as i32;
    }

    pub fn end(&self) -> i32 {
        self.start() + self.duration()
    }

    pub fn set_end(&self, value: i32) {
        *self.start.borrow_mut() = value - self.duration();
        self.set_hours_per_day();
    }

    pub fn duration(&self) -> i32 {
        *self.duration.borrow()
    }

    pub fn set_duration(&self, value: i32) {
        let mut value = value;
        if value < 1 {
            value = 1;
        }
        *self.duration.borrow_mut() = value;
        self.set_hours_per_day();
    }

    pub fn start(&self) -> i32 {
        *self.start.borrow()
    }

    pub fn set_start(&self, value: i32) {
        *self.start.borrow_mut() = value;
    }

    pub fn hours_per_day(&self) -> i32 {
        *self.hours_per_day.borrow()
    }
}
