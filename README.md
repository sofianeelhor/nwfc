# nwfc

reversed the nintendo wfc services a bit. nas/gpcm/gpsp are spitting
enough to keep a gen4/5 client alive and answer the gts.

tested with ~30 pcap from d/p/hgss/bw/b2w2. lot of stuff is still
wrong, see PROTOCOL.txt. the \lt presence blob is a pure guess,
j'ai que des morceaux.

## what works

- nas /ac -> token
- gpcm \login\ + \ka\ keepalive
- gts op 0x0001, 0x0004. le 0x0002 c'est faux je crois
- pk4/pk5 decode + checksum + shuffle

## build

	make

devkitARM r54, libctru 1.6.0. rien de special.

## run

	python3 py/nas.py &
	python3 py/gpcm.py --port 29900 &
	sudo python3 tools/dns_poison.py --ip 192.168.1.42

et pointer le dns du ds sur la machine. le ds resout les noms en dur
donc faut vraiment passer par le dns, on peut pas juste editer un hosts.

## todo

- shuffle peut etre toujours faux sur certains pid
- presences (\lt) : que des bouts
- 0x0004 je sais pas ce que ca renvoie au juste
- gen5 pas teste du tout
- le sniff.py bouffe de la ram sur les gros pcap, a voir

## credits

merci a ceux qui ont dump leurs pcaps.
le format pk4/pk5 vient de ce que j'ai pu lire a droite a gauche,
j'ai rien copie de pkhex (j'ai pas le niveau en c#)

gpl3.
