#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-6-5
import os
import re
import json
import requests
import html2text
from parse_content import parse

"""
just for study and fun
Talk is cheap
show me your code
"""


class ZhiHu(object):
    def __init__(self):
        self.request_content = None

    def request(self, url, retry_times=10):
        header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
            'Host': 'www.zhihu.com'
        }
        times = 0
        while retry_times > 0:
            times += 1
            print 'request %s, times: %d' % (url, times)
            try:
                self.request_content = requests.get(url, headers=header, timeout=10).content
            except Exception, e:
                print e
                retry_times -= 1
            else:
                return self.request_content

    def get_all_answer_content(self, question_id, flag=2):
        first_url_format = 'https://www.zhihu.com/api/v4/questions/{}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_collapsed%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit=20&offset=3'
        first_url = first_url_format.format(question_id)
        response = self.request(first_url)
        if response:
            contents = json.loads(response)
            print contents.get('paging').get('is_end')
            while not contents.get('paging').get('is_end'):
                for content in contents.get('data'):
                    self.parse_content(content, flag)
                next_page_url = contents.get('paging').get('next').replace('http', 'https')
                contents = json.loads(self.request(next_page_url))
        else:
            raise ValueError('failed 10 times, quit......')

    def get_single_answer_content(self, answer_url, flag=1):
        all_content = {}
        question_id, answer_id = re.findall('https://www.zhihu.com/question/(\d+)/answer/(\d+)', answer_url)[0]

        html_content = self.request(answer_url)
        if html_content:
            all_content['main_content'] = html_content
        else:
            raise ValueError('failed 10 times, quit......')

        ajax_answer_url = 'https://www.zhihu.com/api/v4/answers/{}'.format(answer_id)
        ajax_content = self.request(ajax_answer_url)
        if ajax_content:
            all_content['ajax_content'] = json.loads(ajax_content)
        else:
            raise ValueError('failed 10 times, quit......')

        self.parse_content(all_content, flag, )

    def parse_content(self, content, flag=None):
        data = parse(content, flag)
        self.transform_to_markdown(data)

    def transform_to_markdown(self, data):
        content = data['content']
        author_name = data['author_name']
        answer_id = data['answer_id']
        question_id = data['question_id']
        question_title = data['question_title']
        vote_up_count = data['vote_up_count']
        create_time = data['create_time']

        file_name = u'%s--%s的回答[%d].md' % (question_title, author_name, answer_id)
        folder_name = u'%s' % (question_title)

        if not os.path.exists(os.path.join(os.getcwd(), folder_name)):
            os.mkdir(folder_name)
        os.chdir(folder_name)

        f = open(file_name, "wt")
        f.write("-" * 40 + "\n")
        origin_url = 'https://www.zhihu.com/question/{}/answer/{}'.format(question_id, answer_id)
        f.write("## 本答案原始链接: " + origin_url + "\n")
        f.write("### question_title: " + question_title.encode('utf-8') + "\n")
        f.write("### Author_Name: " + author_name.encode('utf-8') + "\n")
        f.write("### Answer_ID: %d" % answer_id + "\n")
        f.write("### Question_ID %d: " % question_id + "\n")
        f.write("### VoteCount: %s" % vote_up_count + "\n")
        f.write("### Create_Time: " + create_time + "\n")
        f.write("-" * 40 + "\n")

        text = html2text.html2text(content.decode('utf-8')).encode("utf-8")
        # 标题
        r = re.findall(r'\*\*(.*?)\*\*', text, re.S)
        for i in r:
            if i != " ":
                text = text.replace(i, i.strip())

        r = re.findall(r'_(.*)_', text)
        for i in r:
            if i != " ":
                text = text.replace(i, i.strip())
        text = text.replace('_ _', '')

        # 图片
        r = re.findall(r'!\[\]\((?:.*?)\)', text)
        for i in r:
            text = text.replace(i, i + "\n\n")

        f.write(text)

        f.close()


if __name__ == '__main__':
    zhihu = ZhiHu()
    url = 'https://www.zhihu.com/question/27621722/answer/105331078'
    zhihu.get_single_answer_content(url)

    # question_id = '27621722'
    # zhihu.get_all_answer_content(question_id)
