fn ttt() -> Option<i32>{
    assert_eq!(1, 2);
    return Option::<i32>::None;
}

fn tt() -> Option<i32>{
    return ttt();
}

fn main(){

    tt().unwrap();
}