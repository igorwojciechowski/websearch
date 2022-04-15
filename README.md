# websearch

A content discovery/enumeration tool utilizing python `asyncio` package.
Sends GET request to the target URL with a path read from wordlist and prints the result containing whole URL, status code and content length.

## Usage

```shell


        █ █ █ ██▀ █▄▄ █▀ ██▀ ▄▀█ █▀█ █▀▀ █ █
        ▀▄▀▄▀ █▄▄ █▄█ ▄█ █▄▄ █▀█ █▀▄ █▄▄ █▀█ 0.1


usage: websearch.py [-h] -u URL -w WORDLIST [-t THREADS] [-m METHODS] [--max_errors MAX_ERRORS] [-fi FILTER_INCLUDE]
                    [-fe FILTER_EXCLUDE]

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     URL to be enumerated
  -w WORDLIST, --wordlist WORDLIST
                        path to a wordlist
  -t THREADS, --threads THREADS
                        number of threads
  -m METHODS, --methods METHODS
  --max_errors MAX_ERRORS
                        Max errors
  -fi FILTER_INCLUDE, --filter_include FILTER_INCLUDE
                        include only status codes; comma-separated
  -fe FILTER_EXCLUDE, --filter_exclude FILTER_EXCLUDE
                        exclude status codes; comma-separated
```

```bash
$ ./websearch.py -u http://target.com -w /wordlists/evil.txt -t 50



        █ █ █ ██▀ █▄▄ █▀ ██▀ ▄▀█ █▀█ █▀▀ █ █
        ▀▄▀▄▀ █▄▄ █▄█ ▄█ █▄▄ █▀█ █▀▄ █▄▄ █▀█ 0.1


METHOD          URL                                             STATUS          CONTENT LENGTH
GET             http://target.com/admin.php                     200             1337
GET             http://target.com/config.json                   301             0
...
```