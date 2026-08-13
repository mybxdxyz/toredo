use std::fs::File;
use std::io::Write;

pub fn load_tasks() {
    let mut file = File::open("tasks.json");
    return serde_json::from_str(file);
}

pub fn save_tasks(vect: Vec<Task>) -> std::io::Result<()> {
    let mut file = File::create("tasks.json")?;
    let output: String = serde_json::to_string_pretty(&vect).unwrap();
    write!(file, "{}", vect)?;
    Ok(())
}