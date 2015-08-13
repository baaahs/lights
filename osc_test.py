import lib.OSC as osc


host = "127.0.0.1"
port = 5700

client = osc.OSCClient()
client.connect((host, port))


msg = osc.OSCMessage("/main/color/0/rgb")
# Red
# msg.append("255")
# msg.append("0")
# msg.append("0")

# Green
# msg.append(0)
# msg.append(255)
# msg.append(0)

# Blue
msg.append(0.0)
msg.append(0.0)
msg.append(1.0)

client.send(msg)