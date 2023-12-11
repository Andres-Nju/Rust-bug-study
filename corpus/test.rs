
fn main(){

    let mut a = [1, 2, 3];
    let b = &mut a[..];
    println!("{:?}", b);
    b.swap(1, 1);
    println!("{:?}", b);
    let b1 = &mut b[1];
    let b2 = &mut b[2];
    println!("{:?}", b1);
    println!("{:?}", b2);
}
