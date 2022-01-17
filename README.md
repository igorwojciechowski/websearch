# websearch

A content discovery/enumeration tool utilizing python `asyncio` package.
Sends GET request to the target URL with a path read from wordlist and prints the result containing whole URL, status code and content length.

## Usage

```bash
usage: websearch.py [-h] -u URL -w WORDLIST [-t THREADS] [--max_errors MAX_ERRORS]

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     URL to be enumerated
  -w WORDLIST, --wordlist WORDLIST
                        path to a wordlist
  -t THREADS, --threads THREADS
                        number of threads
  --max_errors MAX_ERRORS
                        Max errors
```

```bash
$ ./websearch.py -u http://target.com -w /wordlists/evil.txt -t 50

http://target.com/admin.php 200 1337
http://target.com/user.php  200 1337
...
```