from base import *


def convert_webpage_to_markdown(url, output_file, base_url, output_folder):
    print(url)
    try:
        md_no_html = html_to_md_first(url, base_url)
        md_string = md_no_html.split('\n')
        md_lines = md_clean(md_string)
        md_cleaned = html_to_md_second(md_lines)
        file_path = os.path.join(output_folder, output_file)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(md_cleaned)

    except requests.RequestException as e:
        print(f"Error in making request: {e}")
    except bs4.BeautifulSoup as e:
        print(f"Error in parsing HTML: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def perform_operation(input_url, output_folder, img):
    try:
        os.mkdir(output_folder)
    except FileExistsError:
        print("文件夹已存在")
    if img:
        try:
            os.mkdir(os.path.join(output_folder, "img"))
        except FileExistsError:
            print("图片文件夹已存在")

    all_url = get_all_urls_butterfly(input_url)

    for j in sorted(set(all_url), reverse=True):
        out_file = j.split('/')
        convert_webpage_to_markdown(j, f'{unquote(out_file[-2])}.md',
                                    input_url.strip('/'), output_folder)


if __name__ == '__main__':
    args = main()
    perform_operation(args.input_url, args.output_folder, args.have_img)
