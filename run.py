#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: zhoubin  2350686113@qq.com
# @Date: 2019/12/31

import requests
import json
import os

from config import PHONE, PASSWORD


class Musics(object):

    _server = 'http://127.0.0.1:3000'
    _filepath = os.path.dirname(__file__)

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
        :return: 歌单列表
        """
        m_data = []
        url = self._server + '/user/playlist?uid={}'.format(uid)
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

    def get_song_info(self, mid):
        """
        获取歌单中歌曲ID
        :param mid: 歌单ID
        :return: 歌曲信息
        """
        song_list = []
        url = self._server + '/playlist/detail?id={}'.format(mid)
        response = self.login.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            playlist = data['playlist']['tracks']
            for i in playlist:
                record = {
                    'id': i['id'],
                    'name': i['name'],
                    'singer': i['ar'][0]['name'],
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
        url = self._server + '/check/music?id={}'.format(sid)
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
        url = self._server + '/song/url?id={}'.format(sid)
        response = self.login.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)['data'][0]
            url = data['url']
            br = data['br']
            return url, br

    def make_new_song_list(self, mid):
        """
        提取有效的歌曲，组合成有版权的歌单
        :return:
        """
        new_song_list = []
        print('正在提取有效歌曲...')
        song_mapping = self.get_song_info(mid)
        for song in song_mapping:
            status = self.vail_song(song['id'])
            if status:
                url, br = self.get_song_url(song['id'])
                record = {
                    'id': song['id'],
                    'name': song['name'],
                    'singer': song['singer'],
                    'br': br,
                    'url': url,
                }
                print('添加歌曲 "{}" '.format(song['name']))
                new_song_list.append(record)
        print('所有有效歌曲添加完成...')
        return new_song_list

    def download(self, sid):
        """
        下载单首歌曲
        :return:
        """
        url, br = self.get_song_url(sid)
        name = input('请输入歌名：')
        singer = input("请输入歌手：")
        filename = name + '-' + singer + '.mp3'
        response = requests.get(url)
        if response.status_code == 200:
            print('正在下载歌曲 {} ...'.format(filename))
            with open(os.path.join(self._filepath, 'musics', filename), 'wb') as f:
                f.write(response.content)

    def downloads(self, mid):
        """
        下载歌单所有音乐
        :return:
        """
        songs = self.make_new_song_list(mid)
        print('开始下载歌曲...')
        for song in songs:
            name = song['name'] + '-' + song['singer'] + '.mp3'
            print('正在下载 {} ...'.format(name))
            url = song['url']
            if url:
                response = self.login.get(url)
                if response.status_code == 200:
                    with open(os.path.join(self._filepath, 'musics', name), 'wb') as f:
                        f.write(response.content)


if __name__ == '__main__':
    m = Musics()
    ret = m.status
    uid = ret['profile']['userId']  # 获取用户 ID
    music_mapping = m.get_mid(uid)  # 获取歌单列表
    m.download(1413087236)
    # m.downloads(3109278173)
    # song_mapping = m.make_new_song_list(974291055)     # 获取某歌单中的歌曲列表
    # for i in song_mapping:
    #     print(i)
