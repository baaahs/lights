import model.opc as opc
import sys
import time

server_ip_port = "10.0.1.103:7890"
max_pixels = 1500

client = opc.Client(server_ip_port, True)

pixels = [(0,0,0)] * max_pixels


ch = int(sys.argv[1])

print "Channel %d" % (ch)

start = ch * 64
end = start + 64

for p in range(start,end):
	pixels[p] = (255,0,0)

client.put_pixels(pixels)
client.put_pixels(pixels)