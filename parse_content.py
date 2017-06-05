#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-6-5
import time
from bs4 import BeautifulSoup


def html_template(data):
    # api content
    html = '''
        <html>
        <head>
        <body>
        %s
        </body>
        </head>
        </html>
        ''' % data
    return html


def parse(content, flag=None):
    data = {}
    if flag == 1:
        # single
        main_content = content.get('main_content')
        ajax_content = content.get('ajax_content')

        soup = BeautifulSoup(main_content.decode("utf-8"), "lxml")
        answer = soup.find("span", class_="RichText CopyrightRichText-richText")

        author_name = ajax_content.get('author').get('name')
        answer_id = ajax_content.get('id')
        question_id = ajax_content.get('question').get('id')
        question_title = ajax_content.get('question').get('title')
        vote_up_count = soup.find("meta", itemprop="upvoteCount")["content"]
        create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ajax_content.get('created_time')))


    else:
        # all
        answer_content = content.get('content')

        author_name = content.get('author').get('name')
        answer_id = content.get('id')
        question_id = content.get('question').get('id')
        question_title = content.get('question').get('title')
        vote_up_count = content.get('voteup_count')
        create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(content.get('created_time')))

        content = html_template(answer_content)
        soup = BeautifulSoup(content, 'lxml')
        answer = soup.find("body")

    print author_name,answer_id,question_id,question_title,vote_up_count,create_time
    # 这里非原创，看了别人的代码，修改了一下
    soup.body.extract()
    soup.head.insert_after(soup.new_tag("body", **{'class': 'zhi'}))

    soup.body.append(answer)

    img_list = soup.find_all("img", class_="content_image lazy")
    for img in img_list:
        img["src"] = img["data-actualsrc"]
    img_list = soup.find_all("img", class_="origin_image zh-lightbox-thumb lazy")
    for img in img_list:
        img["src"] = img["data-actualsrc"]
    noscript_list = soup.find_all("noscript")
    for noscript in noscript_list:
        noscript.extract()

    data['content'] = soup
    data['author_name'] = author_name
    data['answer_id'] = answer_id
    data['question_id'] = question_id
    data['question_title'] = question_title
    data['vote_up_count'] = vote_up_count
    data['create_time'] = create_time

    return data
