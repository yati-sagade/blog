---
date: 2018-06-24

layout: post

title: Creating lock-files in Unix

tags:
    - unix
    - programming
    - rust
---

Lockfiles are commonly used for process level mutal exclusion. For example, a
cronjob processing hourly logs can hold a lock so in the event it ends up taking
more time than an hour, the next hourly job does not clobber the working
directory. Databases like Postgres also use lockfiles in their data directories
to ensure at most one serving process is handling the data.

On Unix, a very simple way of doing this is to open a file with the desired path
with `O_RDWR` and `O_EXCL` specified:

    int fd = open("/path/to/.lockfile", O_CREAT | O_RDWR | O_EXCL, 0600);


- `O_CREAT` asks `open()` to create the file if it does not exist.
- `O_RDWR` requests a read/write handle.
- `O_EXCL` ensures that _this_ call creates the file. From the Linux `open(2)`
  manpage,
  
  ...if this flag is specified in conjunction with O_CREAT, and pathname
  already exists, then open() will fail. When these two flags are specified,
  symbolic links are not followed: if pathname is a symbolic link, then open()
  fails regardless of where the symbolic link points to.


Once such an `open()` succeeds, it is common practice to put the pid of the
process that holds this "lock" into the opened lockfile before closing the
handle.

In Rust, this can be achieved using the `std::fs::OpenOptions::create_new()`
function. We can wrap that in this small struct:
```rust
use std::fs::OpenOptions;
use std::path::{Path, PathBuf};
use std::process;
use std::io::{self, Write};
use std::fs;

#[derive(Debug)]
pub struct LockFile {
    path: PathBuf,
}

impl LockFile {
    pub fn new<P>(path: P, lockfile_contents: Option<&[u8]>) -> io::Result<LockFile>
    where
        P: AsRef<Path>,
    {

        {
            // create_new() translates to O_EXCL|O_CREAT being specified to the
            // underlying open() syscall on *nix (and CREATE_NEW to the
            // CreateFileW Windows API), which means that the call is successful
            // only if it is the one which created the file.
            let mut file = OpenOptions::new().write(true).create_new(true).open(
                path.as_ref(),
            )?;
            if let Some(contents) = lockfile_contents {
                file.write_all(contents)?;
            }
        }
        debug!(
            "Successfully wrote lockfile {:?}, pid: {}",
            path.as_ref(),
            process::id()
        );
        // By this time the file we created is closed, and we are sure that
        // we are the one who created it.
        Ok(LockFile { path: path.as_ref().to_path_buf() })
    }
}

impl Drop for LockFile {
    fn drop(&mut self) {
        debug!("Removing lockfile {:?}, pid: {}", &self.path, process::id());
        fs::remove_file(&self.path).unwrap();
    }
}
```


Note that the lockfile will automatically be removed when the `LockFile` value
associated with it is dropped.

For a much more interesting implementation, see the [CreateLockFile][1] function
from Postgres. It is of course way more involved because of failure recovery
requirements.


[1]: https://github.com/postgres/postgres/blob/c37b3d08ca6873f9d4eaf24c72a90a550970cbb8/src/backend/utils/init/miscinit.c#L864

