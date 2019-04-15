package main

import (
	"bytes"
	"io/ioutil"
	"math"
	"net/http"
	"os"
	"sort"
	"strconv"
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

type bigramKey struct {
	first string
	second string
}

type llrStatistic struct {
	bgram bigramKey
	value float64
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
	resp, err := client.Do(req)
	check(err) //problem with tokenizer
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
		go callTokenizer(response, dat)
		println(f.Name())
		corpus[processCount]=<-response
		processCount++
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

func filterTokens(tokens []token) []token {
	filteredTokens := make([]token, 0)
	for i := range tokens {
		if !IsLetter(tokens[i].basic) {
			continue
		} else {
			filteredTokens = append(filteredTokens, tokens[i])
		}
	}
	return filteredTokens
}

func createBigramKey(bgram bigram) bigramKey {
	var bgramKey bigramKey
	bgramKey.first = bgram.first.basic+":"+strings.Split(bgram.first.tags,":")[0]
	bgramKey.second = bgram.second.basic+":"+strings.Split(bgram.second.tags,":")[0]
	return bgramKey
}

func createBigramMap(bigrams []bigram) map[bigramKey]int {
	bigramDict := make(map[bigramKey]int)
	for i := range bigrams {
		bigramDict[createBigramKey(bigrams[i])]++
	}
	return bigramDict
}

func createTokenMap(tokens []token) map[string]int {
	tokenDict := make(map[string]int)
	for i := range tokens {
		tokenDict[tokens[i].basic+":"+strings.Split(tokens[i].tags,":")[0]]++
	}
	return tokenDict
}

func ex5(statistics []llrStatistic) []llrStatistic {
	output := make([]llrStatistic, 0)
	for i := range statistics {
		if strings.Split(statistics[i].bgram.first,":")[1] == "subst" && (strings.Split(statistics[i].bgram.second,":")[1] == "subst" || strings.Split(statistics[i].bgram.second,":")[1] == "adj") {
			output = append(output, statistics[i])
		}
	}
	return output
}

func main() {
	f, err := os.Create("results")
	check(err)
	defer f.Close()
	corpus := loadCorpus()
	parsedTokens := parseCorpus(corpus)
	bigrams := createBigrams(parsedTokens)
	filteredBigrams := filterBigrams(bigrams)
	bigramsMap := createBigramMap(filteredBigrams)
	filteredTokens := filterTokens(parsedTokens)
	tokensMap := createTokenMap(filteredTokens)
	statistics := llr(bigramsMap, tokensMap, len(filteredBigrams), len(filteredTokens))
	//println(statistics)
	sort.Slice(statistics,func(i, j int) bool {return statistics[i].value > statistics[j].value})
	output := ex5(statistics)
	for i:=1;i<50;i++ {
		_, err = f.WriteString(strconv.Itoa(i) + " " + output[i].bgram.first + " " + output[i].bgram.second + " " + strconv.FormatFloat(output[i].value, 'f', 6, 64) + "\n")
		check(err)
	}
	//for key, value := range bigramsMap {
	//	println(key.first + " " + key.second + " " + strconv.Itoa(value))
	//}
	//println(len(parsedTokens))
	//println(len(bigrams))
	//println(len(filteredBigrams))
	//println(corpus[2])
}

func llr(bigrams map[bigramKey]int, tokens map[string]int, bigramCount int, tokenCount int) []llrStatistic{
	statistics := make([]llrStatistic, 0)
	for key, value := range bigrams {
		pairs := value
		w1notw2 := tokens[key.first] - value
		w2notw1 := tokens[key.second] - value
		notw1notw2 := tokenCount - tokens[key.first] - tokens[key.second]
		llrvalue := 2 * float64(pairs + w1notw2 + w2notw1 + notw1notw2) * (h([]int{pairs, w1notw2, w2notw1, notw1notw2}) - h([]int{pairs + w2notw1, w1notw2 + notw1notw2}) - h([]int{pairs + w1notw2, w2notw1 + notw1notw2}))
		statistics = append(statistics, llrStatistic{key, llrvalue})
	}
	return statistics
}

func h(values []int) float64 {
	N := sum(values)
	v := make([]float64, 0)
	for i := range values {
		denominator :=0
		if values[i] == 0 {
			denominator = 1
		}
		comp := float64(values[i])/float64(N)*math.Log2(float64(values[i])/float64(N)+float64(denominator))
		v = append(v, comp)
	}
	return sumFloat(v)
}

func sum(arr []int) int {
	sum := 0
	for i := range arr {
		sum += arr[i]
	}
	return sum
}

func sumFloat(arr []float64) float64 {
	sum := float64(0)
	for i := range arr {
		sum += arr[i]
	}
	return sum
}
