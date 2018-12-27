#include <3ds.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "dns_redirect.h"

#define PORT 29900
#define BUF  2048
#define SRV  "192.168.1.42"	// la machine qui fait tourner les py

int running = 1;
int sock = -1;
char buf[BUF];
char challenge[32];

// TODO decouper ca en modules

static void logmsg(const char *s)
{
	printf("%s\n", s);
}

int tcp_connect(const char *h, int p)
{
	struct sockaddr_in a;

	sock = socket(AF_INET, SOCK_STREAM, 0);
	if (sock < 0)
		goto fail;

	memset(&a, 0, sizeof(a));
	a.sin_family = AF_INET;
	a.sin_port = htons(p);
	a.sin_addr.s_addr = inet_addr(h);

	if (connect(sock, (struct sockaddr *)&a, sizeof(a)) < 0)
		goto fail;
	return 0;

fail:
	logmsg("tcp_connect: rate");
	// ca fuit. je sais
	return -1;
}

int do_login(const char *token)
{
	char req[256];

	snprintf(req, sizeof(req),
		"\\login\\\\challenge\\%s\\response\\%s\\str\\",
		challenge, token);
	send(sock, req, strlen(req), 0);
	return 0;
}

int main(int argc, char **argv)
{
	u32 kDown;

	socInit((u32 *)memalign(0x1000, 0x100000), 0x100000);
	dns_start(inet_addr(SRV));

	consoleInit(GFX_TOP, NULL);
	printf("nwfc\n");
	printf("dns up, gpcm sur %s:%d\n", SRV, PORT);

	if (tcp_connect(SRV, PORT) < 0)
		goto end;

	while (aptMainLoop()) {
		hidScanInput();
		kDown = hidKeysDown();
		if (kDown & KEY_START)
			break;
		if (kDown & KEY_A)
			do_login("00000000000000000000000000000000");
		// TODO le \ka\ sinon ca coupe
		gfxFlushBuffers();
		gfxSwapBuffers();
		gspWaitForVBlank();
	}

end:
	dns_stop();
	socExit();
	return 0;
}
