mod taskhandle;

#[derive(Debug)]
struct Task {
    description: String,
    status: bool
}

impl std::fmt::Display for Task {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
    if self.status {
        write!(f, "[x] {}", self.description)
    } else {
        write!(f, "[] {}", self.description)
    }
}
}

fn handle_request(choice: Option<char>) {
    match choice {
        Some('a') => taskhandle::create_task(),
        _ => println!("Unknown command!")
    }
}

fn main() {
    let mut tasks_list: Vec<Task> = Vec::new();
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).unwrap();
    let choice = input.trim().chars().next();
    handle_request(choice)
}