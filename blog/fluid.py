import bs4
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re


def get_all_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    absolute_links = [urljoin(url, link['href']) for link in links]
    return absolute_links


def get_all_archives(url, same_url):
    s = []
    pattern = r'\d+/\d+/\d+'
    all_links = get_all_links(url)
    for i in all_links:
        match = re.search(pattern, i)
        if i not in same_url and match:
            s.append(i)
    print(s)
    return s


def process_a_tags(tag, base_url):
    if tag.name == "a":
        href = tag.get("href")
        title = tag.get("title")
        link_text = tag.get_text(strip=True)

        if href:
            if not urlparse(href).scheme and base_url:
                # 如果是相对路径且存在 base_url，则转换为绝对路径
                absolute_url = urljoin(base_url, href)
            else:
                absolute_url = href

            markdown_link = f"[{link_text}]({absolute_url} '{title}')"
            new_tag = bs4.BeautifulSoup(markdown_link, "html.parser")
            tag.replace_with(new_tag)
    elif tag.name == "img":
        src = tag.get("src")
        absolute_url = urljoin(base_url, src)
        alt = tag.get("alt")
        title = tag.get("title")
        markdown_img = f"![{alt}]({absolute_url} '{title}')\n"
        new_tag = bs4.BeautifulSoup(markdown_img, "html.parser")
        tag.replace_with(new_tag)


def convert_all_a_tags_to_url(article_tag, base_url=None):
    for a_tag in article_tag.find_all("a"):
        process_a_tags(a_tag, base_url)
    for a_tag in article_tag.find_all("img"):
        process_a_tags(a_tag, base_url)


def process_code_block(tag):
    code_tag = tag.find("code")
    if code_tag:
        code_content = code_tag.get_text()
        new_code_block = f"```\n{code_content}\n```"
        tag.replace_with(new_code_block)


def convert_webpage_to_markdown(url, output_file, base_url=""):
    try:
        # 获取网页内容
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

        # 使用BeautifulSoup解析HTML
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
            for figure_tag in figure_tags:
                process_code_block(figure_tag)

            md = core.prettify()
            md_no_html = re.sub(r'</?[a-zA-Z]+[^<>]*>', '', md)
            md_stripped = md_no_html.strip()
            md_lines = [line.lstrip() for line in md_stripped.splitlines() if line.strip()]
            md_cleaned = '\n'.join(md_lines)

            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(md_cleaned)

        else:
            print("未找到 <article> 元素")
    except requests.RequestException as e:
        print(f"Error in making request: {e}")
    except bs4.BeautifulSoup as e:
        print(f"Error in parsing HTML: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


url1 = ''
url2 = ''
# 获取所有链接
all_links1 = get_all_links(url1)
all_links2 = get_all_links(url2)

link1 = set(all_links1)
link2 = set(all_links2)
same = link1.intersection(link2)

print(same)

for i in range(1, 100):
    try:
        if i == 1:
            all_link = ''
            s = get_all_archives(all_link, same)
            if len(s) == 0:
                break
            else:
                for j in s:
                    convert_webpage_to_markdown(j, 'output.md')
                    break
            break

        else:
            all_link = '' + str(i)
            s = get_all_archives(all_link, same)
            if len(s) == 0:
                break
    except:
        if i > 2:
            break
