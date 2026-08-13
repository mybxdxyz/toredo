mod storage;
mod model;

fn main() {
    let mut tasks_list: Vec<model::Task> = storage::load_tasks();
    let json_string: String = 
    let _ = storage::save_tasks(json_string);
}