package main

import (
	"bytes"
	"io/ioutil"
	"net/http"
	"strings"
	"unicode"
)

type token struct {
	original string
	delimiter string
	basic string
	tags string
	something string
}

type bigram struct {
	first token
	second token
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func IsLetter(s string) bool {
	for _, r := range s {
		if !unicode.IsLetter(r) {
			return false
		}
	}
	return true
}


func callTokenizer(c chan string, data []byte){
	url := "http://localhost:9200"
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(data))
	check(err)
	client := &http.Client{}
	resp, _ := client.Do(req)
	//check(err) problem with tokenizer
	body, _ := ioutil.ReadAll(resp.Body)
	c <- string(body)
}

func loadCorpus() []string{
	files, err := ioutil.ReadDir("../ustawy")
	corpus := make([]string, len(files))
	check(err)
	response := make(chan string)
	processCount := 0
	for _, f := range files {
		dat, err := ioutil.ReadFile("../ustawy/"+f.Name())
		check(err)
		processCount++
		go callTokenizer(response, dat)
	}
	for ;processCount>0;processCount-- {
		println(processCount)
		corpus[processCount-1]=<-response
	}
	return corpus
}

func parseCorpus(corpus []string) []token {
	parsedTokens := make([]token, 0)
	for i := 0; i<len(corpus); i++ {
		lines := strings.Split(corpus[i],"\n")
		for j := 0; j<len(lines); j++ {
			words := strings.Split(lines[j], "\t")
			if len(words) != 2 {
				continue
			}
			var parsedToken token
			parsedToken.original = words[0]
			parsedToken.delimiter = words[1]
			j++
			words = strings.Split(lines[j], "\t")
			parsedToken.basic = words[1]
			parsedToken.tags = words[2]
			parsedToken.something = words[3]
			parsedTokens = append(parsedTokens, parsedToken)
		}
		var parsedToken token
		parsedToken.original = "<endOfFile>"
		parsedTokens = append(parsedTokens, parsedToken)
	}
	return parsedTokens
}

func createBigrams(tokens []token) []bigram {
	bigrams := make([]bigram, 0)
	for i:=1;i<len(tokens);i++ {
		if tokens[i].original == "<endOfFile>" {
			i += 2
		} else {
			var bgram bigram
			bgram.first = tokens[i-1]
			bgram.second = tokens[i]
			bigrams = append(bigrams, bgram)
		}
	}
	return bigrams
}

func filterBigrams(bigrams []bigram) []bigram {
	filteredBigrams := make([]bigram, 0)
	for i := range bigrams {
		if !(IsLetter(bigrams[i].first.basic) && IsLetter(bigrams[i].second.basic)) {
			continue
		} else {
			filteredBigrams = append(filteredBigrams, bigrams[i])
		}
	}
	return filteredBigrams
}

func main() {
	print(IsLetter("."))
	corpus := loadCorpus()
	parsedTokens := parseCorpus(corpus)
	bigrams := createBigrams(parsedTokens)
	filteredBigrams := filterBigrams(bigrams)

	println(len(parsedTokens))
	println(len(bigrams))
	println(len(filteredBigrams))
	//println(corpus[2])
}
