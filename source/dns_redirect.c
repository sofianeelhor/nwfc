#include <3ds.h>
#include <string.h>
#include <stdio.h>
#include "dns_redirect.h"

#define DNS_PORT 53
#define MAXPKT   512

static int fd = -1;
static int up = 0;
static u32 myip = 0;
static Thread thr = NULL;

// label = len+data, fini par 0. compression pas geree, j'en ai jamais vu
static int skipname(u8 *p, int off)
{
	while (p[off]) {
		if (p[off] & 0xc0)
			return off + 2;
		off += p[off] + 1;
	}
	return off + 1;
}

static int endswith(u8 *p, int off, int end, const char *suf)
{
	u8 name[256];
	int i, j = 0;
	int n = strlen(suf);

	while (off < end) {
		int l = p[off++];
		for (i = 0; i < l && off < end; i++)
			name[j++] = p[off++];
		if (off < end && p[off])
			name[j++] = '.';
	}
	name[j] = 0;
	if (j < n)
		return 0;
	return memcmp(name + j - n, suf, n) == 0;
}

// TODO verifier les offsets, faits au pif et ca tombe juste
static int build_reply(u8 *in, u8 *out)
{
	int i, q, off;

	memcpy(out, in, 2);			// id
	out[2] = 0x81; out[3] = 0x80;
	out[4] = 0; out[5] = 1;			// qd
	out[6] = 0; out[7] = 1;			// an
	out[8] = 0; out[9] = 0;
	out[10] = 0; out[11] = 0;

	for (i = 0; i < 12; i++)
		out[12 + i] = in[12 + i];
	q = skipname(in, 12);
	off = q + 4;
	memcpy(out + 12, in + 12, off - 12);

	out[off++] = 0xc0; out[off++] = 0x0c;
	out[off++] = 0x00; out[off++] = 0x01;
	out[off++] = 0x00; out[off++] = 0x01;
	out[off++] = 0x00; out[off++] = 0x00;
	out[off++] = 0x00; out[off++] = 0x3c;	// ttl 60
	out[off++] = 0x00; out[off++] = 0x04;
	out[off++] = (myip >>  0) & 0xff;
	out[off++] = (myip >>  8) & 0xff;
	out[off++] = (myip >> 16) & 0xff;
	out[off++] = (myip >> 24) & 0xff;
	return off;
}

static void dns_thread(void *a)
{
	u8 pkt[MAXPKT], out[MAXPKT];
	struct sockaddr_in from, me;
	socklen_t fl;
	int n, m;

	fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd < 0) {
		printf("dns: pas de socket\n");
		return;
	}
	memset(&me, 0, sizeof(me));
	me.sin_family = AF_INET;
	me.sin_port = htons(DNS_PORT);
	me.sin_addr.s_addr = INADDR_ANY;
	if (bind(fd, (struct sockaddr *)&me, sizeof(me)) < 0) {
		printf("dns: bind fail\n");
		return;
	}
	printf("dns: up sur 53\n");
	while (up) {
		fl = sizeof(from);
		n = recvfrom(fd, pkt, MAXPKT, 0, (struct sockaddr *)&from, &fl);
		if (n < 13)
			continue;
		if (!endswith(pkt, 12, n, ".nintendowifi.net"))
			continue;
		m = build_reply(pkt, out);
		sendto(fd, out, m, 0, (struct sockaddr *)&from, sizeof(from));
	}
	closesocket(fd);
}

int dns_start(u32 ip)
{
	myip = ip;
	up = 1;
	thr = threadCreate(dns_thread, NULL, 0x2000, 0x2f, -2, false);
	return 0;
}

void dns_stop(void)
{
	up = 0;
}
