import os
import argparse
import bs4
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import re


def get_all_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    absolute_links = [urljoin(url, link['href']) for link in links]
    return absolute_links


def get_all_archives_butterfly(url):
    s = []
    pattern = r'\d+/\d+/\d+'
    all_links = get_all_links(url)
    for i in all_links:
        match = re.search(pattern, i)
        if len(i.split('/')) > 6 and match:
            s.append(i)
    return s


def get_all_archives(url, same_url):
    s = []
    pattern = r'\d+/\d+/\d+'
    all_links = get_all_links(url)
    for i in all_links:
        match = re.search(pattern, i)
        if i not in same_url and match:
            s.append(i)
    return s


def process_a_tags(tag, base_url):
    if tag.name == "a":
        href = tag.get("href")
        title = tag.get("title")
        link_text = tag.get_text(strip=True)

        if href:
            if not urlparse(href).scheme and base_url:
                absolute_url = urljoin(base_url, href)
            else:
                absolute_url = href

            markdown_link = f"[{link_text}]({absolute_url} '{title}')"
            tag.replace_with(markdown_link)
    elif tag.name == "img":
        src = tag.get("src")
        absolute_url = urljoin(base_url, src)
        alt = tag.get("alt")
        title = tag.get("title")
        markdown_img = f"![{alt}]({absolute_url} '{title}')\n"
        tag.replace_with(markdown_img)


def convert_all_a_tags_to_url(article_tag, base_url=None):
    for a_tag in article_tag.find_all("a"):
        process_a_tags(a_tag, base_url)
    for a_tag in article_tag.find_all("img"):
        process_a_tags(a_tag, base_url)


def process_code_block(tag, classes):
    code_tag = tag.find('td', class_='code')
    if code_tag:
        code_content = str(code_tag).replace('<br/>', '\n')
        soup = BeautifulSoup(code_content, 'html.parser')
        code_text = soup.get_text()
        if classes != 'plaintext':
            new_code_block = f"````{classes}\n{code_text}\n````"
        else:
            new_code_block = f"````\n{code_text}\n````"
        tag.replace_with(new_code_block)


def process_code_tag(code_tag):
    if code_tag.name == 'code':
        code_content = code_tag.get_text(strip=True)
        new_inline_code = f"`{code_content}`"
        code_tag.replace_with(new_inline_code)


def html_to_md_first(url, base_url):
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text

    bs = bs4.BeautifulSoup(html_content, "html.parser")
    core = bs.find("article")

    if core:
        header_tags = core.find_all(re.compile(r'^h[1-6]$'))
        for header_tag in header_tags:
            header_content = header_tag.get_text(strip=True)
            header_level = int(header_tag.name[1])
            markdown_heading = f"{'#' * header_level} {header_content}\n"
            header_tag.replace_with(bs.new_string(markdown_heading))

        li_tags = core.find_all("li")
        for li_tag in li_tags:
            li_content = li_tag.get_text(strip=True)
            markdown_list_item = f"* {li_content}\n"
            li_tag.replace_with(bs.new_string(markdown_list_item))

        convert_all_a_tags_to_url(core, base_url)
        figure_tags = core.find_all("figure", class_="highlight")
        if figure_tags:
            for figure_tag in figure_tags:
                classes = figure_tag.get('class', [])
                process_code_block(figure_tag, classes[1])

        code_light_tag = core.find_all()
        for code_tag in code_light_tag:
            process_code_tag(code_tag)

        md = core.prettify()

        md_no_html = re.sub(r'</?[a-zA-Z]+[^<>]*>', '', md)

        return md_no_html
    else:
        print("未找到 <article> 元素")
        return None


def html_to_md_second(md_lines):
    md_cleaned = '\n'.join(md_lines)
    md_cleaned = md_cleaned.split('\n')
    for i in range(len(md_cleaned)):
        md_cleaned[i] += '\n'
    for i in range(len(md_cleaned)):
        if md_cleaned[i][0] == '`' and md_cleaned[i][len(md_cleaned[i]) - 2] == '`' and len(
                md_cleaned[i].replace('`', '')) != 1:
            md_cleaned[i - 1] = md_cleaned[i - 1].replace('\n', '')
            md_cleaned[i] = md_cleaned[i].replace('\n', '')
    md_cleaned = ''.join(md_cleaned)
    md_cleaned = md_cleaned.replace('&gt;', '>')
    md_cleaned = md_cleaned.replace('&lt;', '<')
    md_cleaned = md_cleaned.replace('&amp;', '&')
    return md_cleaned


def md_clean(md_string):
    md_lines = []
    in_backticks_block = False
    for i in md_string:
        if '````' in i and len(i.lstrip()) <= 20:
            in_backticks_block = not in_backticks_block
            md_lines.append(i)
        elif not in_backticks_block:
            if i.isspace() or i == '':
                continue
            else:
                md_lines.append(i.lstrip())
        else:
            md_lines.append(i)
    return md_lines


def get_all_urls(input_url):
    url1 = input_url.strip('/') + '/archives'
    url2 = input_url.strip('/') + '/archives/page/2'

    all_links1 = get_all_links(url1)
    all_links2 = get_all_links(url2)

    link1 = set(all_links1)
    link2 = set(all_links2)
    same = link1.intersection(link2)

    all_url = []

    for i in range(1, 100):
        try:
            if i == 1:
                all_link = url1
                s = get_all_archives(all_link, same)
                if len(s) == 0:
                    break
                else:
                    all_url += s

            else:
                all_link = url1 + '/page/' + str(i)
                s = get_all_archives(all_link, same)
                if len(s) == 0:
                    break
                else:
                    all_url += s
        except:
            if i > 2:
                break
    return all_url


def get_all_urls_butterfly(input_url):
    url1 = input_url.strip('/') + '/archives'
    all_url = []
    for i in range(1, 100):
        try:
            if i == 1:
                all_link = url1
                s = get_all_archives_butterfly(all_link)
                all_url += s
                if len(s) == 0:
                    break
                else:
                    all_url += s

            else:
                all_link = url1 + '/page/' + str(i)
                s = get_all_archives_butterfly(all_link)
                if len(s) == 0:
                    break
                else:
                    all_url += s
        except:
            if i > 2:
                break
    return all_url


def main():
    parser = argparse.ArgumentParser(description='blog 爬虫')
    parser.add_argument('-u', '--input_url', type=str, help='输入爬取blog主页的网站路径')
    parser.add_argument('-o', '--output_folder', type=str, help='输出文件夹的路径')
    args = parser.parse_args()
    return args
