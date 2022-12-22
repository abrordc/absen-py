from zk import ZK, const
import sys
import os
import socketio
import requests
import json
from datetime import datetime
IP = sys.argv[1]
sys.path.insert(1, os.path.abspath("./pyzk"))
sio = socketio.Client()
sio.connect('http://192.168.223.15:8000')
pid = os.getpid()
print(pid)
print('my sid is', sio.sid)
# @sio.on('connect')
# def catch_all(event, data):


@sio.event
def connect():
    print("I'm connected!")


@sio.event
def disconnect():
    print("I'm disconnected!")
    quit()


sio.emit('get_id_machine', IP)


@sio.on('id_macchine')
def on_message(data):
    print(data["id_macchine"])
    print(data)
    sio.emit('up', {
        "id_macchine": data["id_macchine"],
        "nama_mesin": data["nama_mesin"],
        "id": data["socket_id"],
        "ip": IP,
        "up": True
    })


def kirim(PIN, DateTime):
    url = 'http://192.168.223.24/api/insert2'
    pos = {
        'IP': IP,
        'PIN': PIN,
        'DateTime': DateTime
    }
    x = requests.post(url, data=json.dumps(pos, indent=4, sort_keys=True, default=str))
    print(x.text)


conn = None
# create ZK instance
zk = ZK(IP, port=4370, timeout=5,
        password=0, force_udp=False, ommit_ping=False)
try:
    # connect to device
    conn = zk.connect()
    # disable device, this method ensures no activity on the device while the process is run
    conn.disable_device()
    zktime = conn.get_time()
    print(zktime)
    newtime = datetime.today()
    conn.set_time(newtime)
    # another commands will be here!
    # Example: Get All Users
    users = conn.get_users()
    for user in users:
        privilege = 'User'
        if user.privilege == const.USER_ADMIN:
            privilege = 'Admin'
        # print('+ UID #{}'.format(user.uid))
        # print('  Name       : {}'.format(user.name))
        # print('  Privilege  : {}'.format(privilege))
        # print('  Password   : {}'.format(user.password))
        # print('  Group ID   : {}'.format(user.group_id))
        # print('  User  ID   : {}'.format(user.user_id))
        # Test Voice: Say Thank You
    # conn.test_voice(index=13)
    # re-enable device after all commands already executed
    conn.enable_device()
    try:
        for attendance in conn.live_capture():
            if attendance is None:
                # implement here timeout logic
                pass
            else:
                #conn.test_voice(index=13)
                kirim(attendance.user_id, attendance.timestamp)
                # print(attendance.user_id)  # Attendance object
    except KeyboardInterrupt:
        print("\nExiting...")

except Exception as e:
    print("Process terminate : {}".format(e))
    sys.exit()
    # sio.emit('kill', pid)
    # exec("kill ".pid)
    # quit()
    # exit()
finally:
    if conn:
        conn.disconnect()
        quit()
