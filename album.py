import json
import os
import sys
from datetime import datetime

import xbmc
import xbmcgui
import xbmcplugin

from utils import API_KEY, getThumbUrl, get_url, conn, RAW_SERVER_URL, datelong, timestamp, SHARED_ONLY, \
    strftime_polyfill

HANDLE = int(sys.argv[1])


def list_albums():
    headers = {
        'Accept': 'application/json',
        'User-agent': xbmc.getUserAgent(),
        'x-api-key': API_KEY
    }
    conn.request("GET", f"/api/albums?shared={SHARED_ONLY or 'false'}", '', headers)
    res = json.loads(conn.getresponse().read().decode('utf-8'))

    items = [(get_url(action='album', id=i['id']), xbmcgui.ListItem(i['albumName']), True) for i in res]
    for i in range(len(res)):
        if 'startDate' in res[i]:
            items[i][1].setDateTime(
                datetime.fromisoformat(res[i]['startDate'][:-5]).strftime('%Y-%m-%dT%H:%M:%SZ'))
        if 'albumThumbnailAssetId' in res[i]:
            items[i][1].setArt({'thumb': getThumbUrl(res[i]['albumThumbnailAssetId'])})
    xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addDirectoryItems(HANDLE, items, len(items))
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)


def album(id):
    xbmcplugin.setContent(HANDLE, 'images')

    headers = {
        'Accept': 'application/json',
        'User-agent': xbmc.getUserAgent(),
        'x-api-key': API_KEY
    }
    conn.request("GET", f"/api/albums/{id}", '', headers)
    res = json.loads(conn.getresponse().read().decode('utf-8'))['assets']

    items = [
        (
            f'{RAW_SERVER_URL}/api/assets/{i["id"]}/original|x-api-key={API_KEY}',
            xbmcgui.ListItem(
                strftime_polyfill(datetime.fromisoformat(i['fileCreatedAt'][:-5]), datelong + " " + timestamp)), False)
        for i in res]
    for i in range(len(res)):
        items[i][1].setArt({'thumb': getThumbUrl(res[i]["id"])})
        items[i][1].setProperty('MimeType', res[i]["originalMimeType"])
        items[i][1].setDateTime(
            datetime.fromisoformat(res[i]['exifInfo']['dateTimeOriginal'][:-5]).strftime('%Y-%m-%dT%H:%M:%SZ'))
        items[i][1].setInfo('pictures', {'exif:resolution': ''})
        if 'exifInfo' in res[i] and 'fileSizeInByte' in res[i]['exifInfo']:
            items[i][1].setInfo('pictures', {'size': res[i]['exifInfo']['fileSizeInByte']})
    xbmcplugin.addDirectoryItems(HANDLE, items, len(items))
    xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
