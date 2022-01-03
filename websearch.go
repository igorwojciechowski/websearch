package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
	"sync"
)

type Data struct {
	url           string
	path          string
	statusCode    int
	contentLength int
}

func readWordlist(path string) []string {
	data, _ := ioutil.ReadFile(path)
	return strings.Split(string(data), "\n")
}

func checkFlags(urlFlag string, wordlistFlag string) {
	isError := false
	if len(urlFlag) == 0 {
		fmt.Println("-u (target URL) flag must be specified")
		isError = true
	}
	if len(wordlistFlag) == 0 {
		fmt.Println("-w (wordlist) flag must be specified")
		isError = true
	}
	if isError {
		os.Exit(1)
	}
}

func request(url string, path string) Data {
	u := fmt.Sprintf("%s/%s", url, path)
	response, _ := http.Get(u)
	fmt.Println(u, response.StatusCode, response.ContentLength)
	return Data{
		url:           url,
		path:          path,
		statusCode:    response.StatusCode,
		contentLength: int(response.ContentLength),
	}
}

func main() {
	urlFlag := flag.String("u", "", "target URL")
	wordlistFlag := flag.String("w", "", "wordlist")
	threadsFlag := flag.Int("t", 30, "number of threads")
	flag.Parse()
	checkFlags(*urlFlag, *wordlistFlag)

	var wg sync.WaitGroup
	var words = make(chan string)

	var data []Data

	go func() {
		for _, w := range readWordlist(*wordlistFlag) {
			words <- w
		}
		close(words)
	}()

	for i := 0; i < *threadsFlag; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for word := range words {
				data = append(data, request(*urlFlag, word))
			}
		}()
	}

	wg.Wait()
	fmt.Print(data)
}
