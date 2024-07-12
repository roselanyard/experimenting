use std::net;
use std::str;

fn main() {
    let socket = net::UdpSocket::bind("127.0.0.1:5001").expect("Could not connect to socket");
    let mut buf = [0;1000];
    let (bytes_read, sender_addr) = socket.recv_from(&mut buf).expect("Failed to receive from socket");
    let string = str::from_utf8(&buf).expect("Failed to convert from UTF-8");
    println!("{}", string);
}

mod tree {
    struct TreeNode<T> {
        pub left: Option<Box<TreeNode<T>>>,
        pub right: Option<Box<TreeNode<T>>>,
        pub key: T,
    }
    impl<T> TreeNode<T> {
        pub fn new(key: T) -> Self {
            TreeNode {left:None, right:None, key}
        }
        pub fn left(mut self, node: TreeNode<T>) -> Self {
            self.left = Some(Box::new(node));
            self
        }
        pub fn right(mut self, node: TreeNode<T>) -> Self {
            self.right = Some(Box::new(node));
            self
        }
        pub fn left_(&mut self, node: TreeNode<T>) -> &Self {
            self.left = Some(Box::new(node));
            self
        }
        pub fn right_(&mut self, node: TreeNode<T>) -> &Self{
            self.right = Some(Box::new(node));
            self
        }
    }
    pub fn test() {
        let mut node = TreeNode::<String>::new("Testing!".to_string());
        let mut node2: TreeNode<String> = TreeNode::<String>::new("Testing".to_string());
        let mut node3: TreeNode<String> = TreeNode::<String>::new("Testing.".to_string());
        //node = node.left(node2);
        //node = node.right(node3);
        node = node.left(node2);
        node = node.right(node3);
    }
}