import requests
import MySQLdb

httpUrl = "http://hkgsherlock.no-ip.org/beacons/report.php"
httpUsePost = True

mysqlHost = "hkgsherlock.no-ip.org"
mysqlPort = 3306
mysqlUser = "ibeacon"
mysqlPass = "1Beac0n"
mysqlDb = "ibeacon_traces"
mysqlTable = "traces"


__mysqlPrepared = False

def in_http(devBdaddr, bleScanResult):
    beaconContent = {"selfMac": devBdaddr,
                     "uuid": bleScanResult.uuid,
                     "major": bleScanResult.major,
                     "minor": bleScanResult.minor,
                     "mac": bleScanResult.mac,
                     "txpower": bleScanResult.u_txpower,
                     "rssi": bleScanResult.rssi}
    method = ''
    data = None
    params = None
    if httpUsePost:
        method = 'post'
        data = beaconContent
    else:
        method = 'get'
        params = beaconContent
    r = requests.request(method, httpUrl, data=data, params=params)
    # return r.status_code == 200 & r.content == "1"


def in_mysql(devBdaddr, bleScanResult):
    db = MySQLdb.connect(host=mysqlHost, port=mysqlPort, user=mysqlUser, passwd=mysqlPass, db=mysqlDb)
    cursor = db.cursor()
    sql = "INSERT INTO " + mysqlTable + "(selfMac, uuid, major, minor, mac, txpower, rssi) \
           VALUES (%d, 0x%s, %d, %d, %d, %d, %d)" % \
                                        (int(devBdaddr.replace(":", ""), 16),
                                         bleScanResult.uuid,  # .replace("-", "")
                                         bleScanResult.major,
                                         bleScanResult.minor,
                                         int(bleScanResult.mac.replace(":", ""), 16),
                                         bleScanResult.u_txpower,
                                         bleScanResult.rssi)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()