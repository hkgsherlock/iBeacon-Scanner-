import json
import requests
import MySQLdb
import sqlite3

httpReportUrl = "http://itd-moodle.ddns.net/2014fyp_ips/beacons/report.php"
httpAttendUrl = "http://itd-moodle.ddns.net/2014fyp_ips/beacons/attend.php"
httpReportLocalUrl = "http://127.0.0.1/beacons/report.php"
httpUsePost = True

httpReportJsonUrl = "http://itd-moodle.ddns.net/2014fyp_ips/beacons/report_json.php"
httpReportLocalJsonUrl = "http://127.0.0.1/beacons/report_json.php"

mysqlHost = "hkgsherlock.no-ip.org"
mysqlPort = 3306
mysqlUser = "ibeacon"
mysqlPass = "1Beac0n"
mysqlDb = "ibeacon_traces"
mysqlTable = "traces"

sqlite3DbPath = '/usr/share/nginx/sqlite_db/ibeacons.sqlite3'
sqlite3DbTable = 'traces'

__mysqlPrepared = False


def in_http(bleScanResult):
    return __in_http_single(bleScanResult, httpReportUrl)


def in_http_attend(bleScanResult):
    result = __in_http_single(bleScanResult, httpAttendUrl)
    if (result.status_code == 500):
        print(result.content)
    return result


def in_http_local(bleScanResult):
    return __in_http_single(bleScanResult, httpReportLocalUrl)


def __in_http_single(bleScanResult, url):
    return __in_http({"selfMac": bleScanResult.selfMac,
                      "uuid": bleScanResult.uuid,
                      "major": bleScanResult.major,
                      "minor": bleScanResult.minor,
                      "mac": bleScanResult.mac,
                      "txpower": bleScanResult.txpower,
                      "rssi": bleScanResult.rssi}, url)


def in_http_list_as_json(resultList):
    # convert to json-serialisable
    dictarr = map(lambda e: e.__dict__, resultList)
    response = __in_http({'jsonData': json.dumps(dictarr)}, httpReportJsonUrl)
    if response.status_code != 200:
        print(response.content)
    return response


def in_http_local_list_as_json(resultList):
    # convert to json-serialisable
    dictarr = map(lambda e: e.__dict__, resultList)
    response = __in_http({'jsonData': json.dumps(dictarr)}, httpReportLocalJsonUrl)
    if response is not None and response.status_code != 200:
        print(response.content)
    return response


def __in_http(data, url):
    params = None
    if httpUsePost:
        method = 'post'
    else:
        method = 'get'
    result = None
    try:
        result = requests.request(method, url, data=data, params=params, timeout=1.0)
        print('http request sent to url "' + url + '", result code is %d' % result.status_code)
    except Exception as e:
        print('cannot send result http request, reason: %s' % e.message)
    return result


def in_mysql(bleScanResult):
    db = None
    try:
        db = MySQLdb.connect(host=mysqlHost, port=mysqlPort, user=mysqlUser, passwd=mysqlPass, db=mysqlDb)
        cursor = db.cursor()
        sql = "INSERT INTO " + mysqlTable + "(selfMac, uuid, major, minor, mac, txpower, rssi) \
               VALUES (%d, 0x%s, %d, %d, %d, %d, %d)" % \
                                            (int(bleScanResult.selfMac.replace(":", ""), 16),
                                             bleScanResult.uuid,  # .replace("-", "")
                                             bleScanResult.major,
                                             bleScanResult.minor,
                                             int(bleScanResult.mac.replace(":", ""), 16),
                                             bleScanResult.txpower,
                                             bleScanResult.rssi)
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print(sql)
        print(e)
        db.rollback()
    finally:
        if db != None:
            db.close()


def in_sqlite(bleScanResult):
    db = None
    try:
        db = sqlite3.connect(sqlite3DbPath)
        c = db.cursor()
        c.execute("INSERT INTO " + sqlite3DbTable + "(selfMac, uuid, major, minor, mac, txpower, rssi) \
               VALUES (%d, x'%s', %d, %d, %d, %d, %d)" % \
                  (int(bleScanResult.selfMac.replace(":", ""), 16),
                   bleScanResult.uuid,  # .replace("-", "")
                   bleScanResult.major,
                   bleScanResult.minor,
                   int(bleScanResult.mac.replace(":", ""), 16),
                   bleScanResult.txpower,
                   bleScanResult.rssi))
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
    finally:
        if db != None:
            db.close()
