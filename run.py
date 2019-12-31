#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: zhoubin  2350686113@qq.com
# @Date: 2019/12/31

import requests
import json

from config import PHONE, PASSWORD


class Musics(object):

    _server = 'http://127.0.0.1:3000'

    @property
    def login(self):
        """
        登录网易云音乐账号
        """
        session = requests.session()
        url = self._server + '/login/cellphone?'
        parm = {
            'phone': PHONE,
            'password': PASSWORD
        }
        response = session.post(url, data=parm)
        if response.status_code == 200:
            return session

    @property
    def status(self):
        """
        检查登录状态
        """
        url = self._server + '/login/status'
        response = self.login.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data

    def get_mid(self, uid):
        """
        获取歌单id
        :param uid: 用户 ID
        :return: 歌单列表 [{'id': 974291055, 'name': 'wanwu_z喜欢的音乐'}, {'id': 3109278173, 'name': '每日歌曲推荐(2019.12.08)'}]
        """
        self.uid = uid
        m_data = []
        url = self._server + '/user/playlist?uid={}'.format(self.uid)
        response = self.login.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            record = data['playlist']
            for i in record:
                record = {
                    'id': i['id'],
                    'name': i['name']
                }
                m_data.append(record)
            return m_data

    def get_sid(self, mid):
        """
        获取歌单中歌曲ID
        :param mid: 歌单ID
        :return: 歌曲ID列表 # [{'id': 176430, 'name': '爱上你是一个错', 'br': 320000}, {'id': 1295824261, 'name': '又何苦', 'br': 320000}]
        """
        self.mid = mid
        song_list = []
        url = self._server + '/playlist/detail?id={}'.format(self.mid)
        response = self.login.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            mlist = data['playlist']['tracks']
            for i in mlist:
                if i['h']:
                    record = {
                        'id': i['id'],
                        'name': i['name'],
                        'br': i['h']['br']
                    }
                    song_list.append(record)
                elif i['m']:
                    record = {
                        'id': i['id'],
                        'name': i['name'],
                        'br': i['m']['br']
                    }
                    song_list.append(record)
                else:
                    record = {
                        'id': i['id'],
                        'name': i['name'],
                        'br': i['l']['br'],
                        'url': ''
                    }
                    song_list.append(record)
            return song_list

    def vail_song(self, sid):
        """
        检查歌曲是否可用
        :param sid: 歌曲 ID
        :return:
        """
        self.sid = sid
        url = self._server + '/check/music?id={}'.format(self.sid)
        response = self.login.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data['success']

    def get_song_url(self, sid):
        """
        获取歌曲链接
        :param sid: 歌曲ID
        :return:
        """
        self.sid = sid
        url = self._server + '/song/url?id={}'.format(self.sid)
        response = self.login.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data['data']


if __name__ == '__main__':
    m = Musics()
    ret = m.status
    uid = ret['profile']['userId']  # 获取用户 ID
    music_mapping = m.get_mid(uid)  # 获取歌单列表
    print(music_mapping)
    song_mapping = m.get_sid(974291055)     # 获取某歌单中的歌曲列表
    print(song_mapping)
    new_song_list = []
    # 验证歌曲是否可用
    for song in song_mapping:
        status = m.vail_song(song['id'])
        if status == True:
            #print('正在添加歌曲 "{}" ...'.format(song['name']))
            urls = m.get_song_url(song['id'])
            record = {
                'id': song['id'],
                'name': song['name'],
                'br': song['br'],
                'url': urls
            }
            new_song_list.append(record)
    print(new_song_list)