package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
	"sync"
)

type Data struct {
	Url           string `json:"url"`
	Path          string `json:"path"`
	StatusCode    int    `json:"statusCode"`
	ContentLength int    `json:"contentLength"`
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
	response, err := http.Get(u)
	if err != nil {
		return Data{}
	}
	body, _ := ioutil.ReadAll(response.Body)
	contentLength := len(string(body))
	fmt.Println(u, response.StatusCode, contentLength)
	return Data{
		Url:           url,
		Path:          path,
		StatusCode:    response.StatusCode,
		ContentLength: contentLength,
	}
}

func outputToFile(data []Data, path string) {
	j, _ := json.Marshal(data)
	ioutil.WriteFile(path, j, 0644)
}

func main() {
	urlFlag := flag.String("u", "", "target URL")
	wordlistFlag := flag.String("w", "", "path to wordlist file")
	threadsFlag := flag.Int("t", 30, "number of threads")
	outputFlag := flag.String("o", "", "output file (json)")
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

	if len(*outputFlag) != 0 {
		outputToFile(data, *outputFlag)
	}
}
