#[derive(serde::Serialize, serde::Deserialize, Debug)]
pub struct Task {
    desc: String,
    completed: bool
}

impl Task {
    fn new(desc: String) -> Self {
        Task {
            desc,
            completed: false
        }
    }

    fn toggle_completed(&mut self) {
        self.completed = !self.completed
    }
}