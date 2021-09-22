package main

import (
	"fmt"
	"io"
	"log"
	"math/rand"
	"net/http"
	"regexp"
	"sort"
	"strings"
)

const (
	SITE      = "https://github.com"
	SITE_RAW  = "https://raw.githubusercontent.com"
	SITE_PATH = "/helioloureiro/canalunixloadon/tree/master/pautas"
)

func curl(url string) string {
	resp, err := http.Get(url)
	if err != nil {
		log.Fatal(err)
	}
	body, err := io.ReadAll(resp.Body)
	defer resp.Body.Close()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("status_code:", resp.StatusCode)
	if resp.StatusCode != 200 {
		return ""
	}
	return string(body)
}

func print(i ...interface{}) {
	fmt.Println(i)
}

func grep(pattern, text string) bool {
	matched, err := regexp.MatchString(pattern, text)
	if err != nil {
		return false
	}
	if matched {
		return true
	}
	return false
}

func sed(old, new, text string) string {
	re := regexp.MustCompile(old)
	return re.ReplaceAllString(text, new)
}

func main() {
	fmt.Println("random articles")
	content := curl(SITE + SITE_PATH)
	lines := strings.Split(content, "\n")

	var listaPautas []string

	for _, line := range lines {
		// print(line)
		if grep("repo-content-pjax-container", line) {
			// print(line)
			line = sed(".*href=\"", "", line)
			line = sed("\".*", "", line)
			if grep("[0-9]", line) {
				// print(line)
				listaPautas = append(listaPautas, line)
			}
		}
	}

	getnew := make(chan string, 1)
	requestnew := make(chan int, 1)

	sort.Strings(listaPautas)
	ultimaPauta := listaPautas[len(listaPautas)-1]
	ultimaPauta = sed("/blob", "", ultimaPauta)
	print("Ultima:" + ultimaPauta)

	go func() {
		// print("link1: " + SITE_RAW + ultimaPauta)
		// print("link2: " + "https://raw.githubusercontent.com/helioloureiro/canalunixloadon/master/pautas/20210911.md")

		conteudoPauta := curl(SITE_RAW + ultimaPauta)
		var assuntos []string
		for _, line := range strings.Split(conteudoPauta, "\n") {
			if grep(`^\*`, line) {
				// print(line)
				assuntos = append(assuntos, line)
			}
		}

		var nr int
		var lidos []int
		for {
			select {
			case <-requestnew:
				for {
					nr = rand.Intn(len(assuntos))
					// print("Número randômico:", nr)
					temValor := false
					for _, v := range lidos {
						if nr == v {
							// print("Valor já existe:", nr)
							temValor = true
						}
					}
					if !temValor {
						break
					}
				}
				lidos = append(lidos, nr)
				getnew <- assuntos[nr]
			}
		}
	}()

	for {
		var entradaDados string
		fmt.Print("Pressione <Enter> pra novo assunto ou digite \"q\" pra sair:")
		size, err := fmt.Scanf("%s", &entradaDados)
		if err != nil {
			// size == 0: apertou <Enter>
			if size != 0 {
				// print("error no Scan()")
				log.Fatal(err)
			}
		}
		// fmt.Println("Entrada de dados:", entradaDados)
		// fmt.Println("tamanho dos dados:", size)
		if entradaDados == "q" {
			// print("saindo do loop")
			break
		}

		requestnew <- 1
		article := <-getnew
		print(article)
	}

}
