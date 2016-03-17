from flask import Flask, render_template, request
from wifi import Cell, Scheme
import os
import subprocess
import socket
import pyping
import time
wifi = 'wlan0'
app = Flask(__name__)

def vpn_status():
    status = subprocess.Popen(["systemctl status openvpn"], stdout=subprocess.PIPE, shell=True)
    (out, err) = status.communicate()
    start = out.find('Active:') + 7
    end = out.find('(',start)
    response = pyping.ping('192.168.100.1')
    if response.ret_code == 0:
      return_text = "Server is reachable"
    else:
      return_text = "Server is unreachable"
    return "{}<br>OpenVPN status: {}".format(return_text,out[start:end])

@app.route('/connect', methods=['POST','GET'])
def wificonnect():
  if request.method == 'POST':
    ssid = request.form['ssid']
    try:
      password = request.form['password']
    except:
      password = None
    cells = Cell.all(wifi)
    counter = 0
    end = counter
    for cell in cells:
      if cell.ssid == ssid:
        end = counter
      counter += 1
    return_text = "{} has {} as a password and is index number {}<br>{}".format(ssid, password, end,cells[end])
    scheme = Scheme.for_cell(wifi,ssid,cells[end],password)
    try:
      scheme.save()
      return_text += "<br>Configuration saved"
    except:
      scheme.delete()
      scheme.save()
      return_text += "<br>Removed previous configuration"
    return return_text
  cells = Cell.all(wifi)
  cells.sort(key=lambda x: x.signal, reverse=True)
  return render_template('wifi.html', cells=cells)

@app.route('/vpn/<status>')
def vpnconfig(status):
  if status=='active':
    os.system('systemctl start openvpn')
    time.sleep(5)
  elif status=='inactive':
    os.system('systemctl stop openvpn')
    time.sleep(5)
  return_text = vpn_status()
  return return_text
    
@app.route('/list')
def listaps():
  text_return = ""
  schemes = Scheme.all()
  #for items in schemes:
  #  text_return +=  items.name
  #return text_return
  return render_template('aplist.html', schemes=schemes)

@app.route('/activate/<ssid>')
def activate_ssid(ssid):
  scheme = Scheme.find(wifi,ssid)
  try:
    scheme.activate()
  except:
    os.system('ifconfig wlan1 up')
    scheme.activate()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
