use std::convert::TryFrom;

#[derive(Debug, Clone, Copy)]
pub enum RelationType {
    FinishToFinish,
    FinishToStart,
    StartToFinish,
    StartToStart,
}

impl TryFrom<i32> for RelationType {
    type Error = ();

    fn try_from(value: i32) -> Result<Self, Self::Error> {
        match value {
            0 => Ok(RelationType::FinishToFinish),
            1 => Ok(RelationType::FinishToStart),
            2 => Ok(RelationType::StartToFinish),
            3 => Ok(RelationType::StartToStart),
            _ => Err(()),
        }
    }
}
