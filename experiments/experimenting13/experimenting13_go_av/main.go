package experimenting13_go_av

// toy antivirus for windows XP?
// we have a backend and a frontend
// the backend should do the following:
//  update definitions (from a centralized server)
//  update the program itself
//  scan a file, scan a registry key, scan a process/thread, scan memory
// 	  to scan a file: hash it with whatever algorithm i'm using, then compare efficiently against
//    the list of hashes of known malware - trie? if all malware definitions are stored locally,
// 	  a giant trie might make sense? fast lookup, then
//

//  scan a set of system resources
//

// or: something GUI, networked, security, and using cool algorithms
// an antivirus would be networked, security, and GUI, and maybe i can do something with
// heuristics

func main() {

}

func scanFile(path string) {
	// given a path to a file, scan it
	// return a status code and information about what it found
}
