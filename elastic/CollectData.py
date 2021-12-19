import requests
from lxml import html
import urllib
import urllib.parse
from langdetect import detect
import langid

from elastic.models import ParagraphsCorpus

def url_encode(url):
    com = urllib.parse.urlparse(url)
    encoded = com.scheme + '://' + com.netloc + urllib.parse.quote(com.path)
    return encoded

def get_corpus(url, title_xpath, en_xpath, vi_xpath, break_word):
    if ('%' not in url):
        url = url_encode(url)
    print(url)
    response = requests.get(url)
 
    # get byte string
    byte_data = response.content
    # get filtered source code
    source_code = html.fromstring(byte_data)
    
    title = source_code.xpath(title_xpath)
    title = title[0].text_content()
    print('Title: ', title)
    
    en_content_tags=source_code.xpath(en_xpath)
    vi_content_tags=source_code.xpath(vi_xpath)
    en = []
    vi = []
    
    for i in range(len(break_word)):
        break_word[i] = break_word[i].upper()
    
    print('============== XỬ LÝ TIẾNG ANH ================')
    print(len(en_content_tags))
    for sentence in en_content_tags:
        tmp = sentence
        try:
            tmp = sentence.text_content()
        except:
            pass
        print()
        print('Gặp: ', tmp.replace('\n',''))
        if (tmp == '' or len(tmp) <= 5):
            continue
        break_scan = False
        for i in break_word:     
            if(i in tmp.upper()):
                break_scan = True
        if(break_scan == True):
            break
        count = 0
        for i in tmp.split(' '):
            try:
                if(detect(i) == 'en' or langid.classify(i)[0] == 'en'):
                    count += 1
            except:
                continue
        count_word  = len(tmp.split(' '))
        print(count)
        print(count_word)
        if(count/count_word >= 0.38):
            print('Duyệt: ', tmp.replace('\n',''))
            en.append(tmp.replace('\n',''))
        else:
            print("Cho qua")

    dem = 0
    print('============== XỬ LÝ TIẾNG VIỆT ================')
    print(len(vi_content_tags))
    for sentence in vi_content_tags:
        tmp = sentence
        try:
            tmp = sentence.text_content()
        except:
            pass
        print()
        print('Gặp: ', tmp.replace('\n',''))
        if (tmp == '' or len(tmp) <= 5):
            continue
        break_scan = False
        for i in break_word:     
            if(i in tmp.upper()):
                break_scan = True
        if(break_scan == True):
            break

        count = 0
        for i in tmp.split(' '):
            try:
                if(detect(i) == 'vi' or langid.classify(i)[0] == 'vi'):
                    count += 1
            except:
                continue
        count_word  = len(tmp.split(' '))
        print(count)
        print(count_word)

        if(count/count_word >= 0.38):
            print('Duyệt: ', tmp.replace('\n',''))
            vi.append(tmp.replace('\n',''))
            print('đã thêm vào vi')
        else:
            print("Cho qua")

    
    min = len(vi)
    if(min > len(en)):
        min = len(en)
        vi = vi[:min]
    else:
        en = en[:min]
    return title, vi, en


def collect_document_links(url, document_links_xpath):
    if ('%' not in url):
        url = url_encode(url)
    response = requests.get(url)
 
    # get byte string
    byte_data = response.content
    # get filtered source code
    source_code = html.fromstring(byte_data)
    
    links = []
    a_tag = source_code.xpath(document_links_xpath)
    print('sô lương: ', len(a_tag))
    for i in a_tag:
        links.append(i.get("href"))
    return links


def collect_corpus_by_range_page(start, end, link_page, page_query, document_links_xpath, title_xpath, en_xpath, vi_xpath, break_word):
    links = []
    result = {}
    end+=1
    for i in range(start, end):
        page_path = link_page + page_query + str(i)
        #print(page_path)
        for j in collect_document_links(page_path, document_links_xpath):
            links.append(j)
    '''for i in links:
        print(i)'''
    for path in links:
        if ('%' not in path):
            path = url_encode(path)
        try:
            doc = ParagraphsCorpus.objects.get(link_document = path)
            title = doc.title
            en = doc.get_en()
            vi = doc.get_vi()
            print('DỮ LIỆU ĐÃ TỒN TẠI - KHÔNG CẦN CÀO NỮA')
        except:
            title, vi, en = get_corpus(path, title_xpath, en_xpath, vi_xpath, break_word)

        result[title] = {'vi': vi, 'en': en, 'link': path}
    return result

# Hàm này dùng tải dữ liệu theo danh sách trang
def collect_corpus_by_list_pages(list_pages, link_page, page_query, document_links_xpath, title_xpath, en_xpath, vi_xpath, break_word):
    links = []
    result = {}
    for i in list_pages:
        page_path = link_page + page_query + str(i)

        for j in collect_document_links(page_path, document_links_xpath):
            links.append(j)
    '''for i in links:
        print(i)'''
    for path in links:
        if ('%' not in path):
            path = url_encode(path)
        try:
            doc = ParagraphsCorpus.objects.get(link_document = path)
            title = doc.title
            en = doc.get_en()
            vi = doc.get_vi()
            print('DỮ LIỆU ĐÃ TỒN TẠI - KHÔNG CẦN CÀO NỮA')
        except:
            title, vi, en = get_corpus(path, title_xpath, en_xpath, vi_xpath, break_word)
        '''if(len(vi) != len(en)):
            continue'''
        #print(title)
        #link = 'search?path=' + path
        #print(link)
        result[title] = {'vi': vi, 'en': en, 'link': path}
    return result


def get_title(url, title_xpath):
    if ('%' not in url):
        url = url_encode(url)
    response = requests.get(url)
    byte_data = response.content
    source_code = html.fromstring(byte_data)
    
    title = source_code.xpath(title_xpath)
    title = title[0].text_content()
    return title

def collect_title_by_range_page(start, end, link_page, page_query, document_links_xpath, title_xpath):
    titles = []
    links = []
    end+=1
    for i in range(start, end):
        page_path = link_page + page_query + str(i)

        for j in collect_document_links(page_path, document_links_xpath):
            links.append(j)

    for path in links:
        if ('%' not in path):
            path = url_encode(path)
        
        title = get_title(path, title_xpath)

        titles.append(title)
    return titles

def collect_title_by_list_pages(list_pages, link_page, page_query, document_links_xpath, title_xpath):
    links = []
    titles = []
    for i in list_pages:
        page_path = link_page + page_query + str(i)

        for j in collect_document_links(page_path, document_links_xpath):
            links.append(j)

    for path in links:
        if ('%' not in path):
            path = url_encode(path)
        
        title = get_title(path, title_xpath)
        
        titles.append(title)
    return titles