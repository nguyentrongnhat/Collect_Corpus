from django_elasticsearch_dsl.search import Search
import requests
from lxml import html
import urllib
import urllib.parse
from langdetect import detect
import langid
import re
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
        break_word[i] = break_word[i].upper().strip()
    print(break_word)
    
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
        if (tmp == '' or len(tmp) <= 5 or tmp[-1] == ':' or tmp.replace('\n','') in en):
            print('continue')
            continue
        break_scan = False
        for i in break_word:     
            if(i in tmp.upper()):
                break_scan = True
        if(break_scan == True):
            print('Gặp break word')
            break

        ############
        print('XỬ LÝ PHÂN LOẠI NGÔN NGỮ - EN')
        if (detect(tmp) == 'en' or  langid.classify(tmp)[0] == 'en'):
            print('Duyệt')
            en.append(tmp.replace('\n',''))
            print('thêm vào en - không gọi hàm phân loại')
        elif (detect(tmp) != 'vi' or  langid.classify(tmp)[0] != 'vi'):
            lang = lang_classify(tmp, 'en')
            print('lang: ', lang)
            if (lang == 'en'):
                print('thêm vào en')
                en.append(tmp.replace('\n',''))
        else:
            print('Cho qua')
        ############
        print('EN:', len(en))

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
        if (tmp == '' or len(tmp) <= 5 or tmp[-1] == ':' or tmp.replace('\n','') in vi):
            print('continue')
            continue
        break_scan = False
        for i in break_word:     
            if(i in tmp.upper()):
                break_scan = True
        if(break_scan == True):
            print('Gặp break word')
            break

        ############
        print('XỬ LÝ PHÂN LOẠI NGÔN NGỮ - VI')
        if (detect(tmp) == 'vi' or  langid.classify(tmp)[0] == 'vi'):
            print('Duyệt')
            vi.append(tmp.replace('\n',''))
        elif (detect(tmp) != 'en' or  langid.classify(tmp)[0] != 'en'):
            lang = lang_classify(tmp, 'vi')
            if (lang == 'vi'):
                vi.append(tmp.replace('\n',''))
        else:
            print('cho qua')
        ############
        print('VI:', len(vi))

    vi = list(dict.fromkeys(vi))
    en = list(dict.fromkeys(en))
    
    print(len(vi))
    print(len(en))

    min = len(vi)
    if(min > len(en)):
        min = len(en)
        vi = vi[:min]
    else:
        en = en[:min]

    
    return title, vi, en


def lang_classify(text, lang):
    print('vao ham: ', text)
    if(lang == 'vi'):
        other_lang = 'en'
    elif(lang == 'en'):
        other_lang = 'vi'
    count = 0
    for i in text.split(' '):
        try:
            de = detect(i)
            cl = langid.classify(i)[0]
            if(de == lang or cl == lang):
                count += 1
            if(de == other_lang or cl == other_lang):
                count -= 1
        except:
            print('DÍNH LỖI')
            continue
    count_word  = len(text.split(' '))
    print(lang,': ',count)
    print('total: ', count_word)

    if(count/count_word >= 0.25):
        print('Duyệt: ', text.replace('\n',''))
        return lang
    else:
        print("Cho qua")
        return other_lang


def collect_document_links(url, document_links_xpath):
    links = []

    '''if ('%' not in url):
        url = url_encode(url)'''
    try:
        print('đã gọi: ', url)
        response = requests.get(url)
    
        # get byte string
        byte_data = response.content
        # get filtered source code
        source_code = html.fromstring(byte_data)
        
        a_tag = source_code.xpath(document_links_xpath)
        print('sô lương: ', len(a_tag))
        for i in a_tag:
            links.append(i.get("href"))
    except:
        pass
    return links


def collect_corpus_by_range_page(start, end, link_page, page_query, document_links_xpath, title_xpath, en_xpath, vi_xpath, break_word):
    links = []
    result = {}
    end+=1
    '''print('ĐÃ VÀO HÀM')
    print('START: ', start)
    print('END: ', end)'''
    for i in range(start, end):
        page_path = link_page + page_query + str(i)
        print(page_path)
        for j in collect_document_links(page_path, document_links_xpath):
            links.append(j)
    for i in links:
        print(i)
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
        if(len(vi)!= 0 and len(en)!=0):
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
        if(len(vi)!= 0 and len(en)!=0):
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

def highlight_search(text, search):
    insensitive = re.compile(re.escape(search), re.IGNORECASE)
    dem = 1
    list_group = []
    while(len(re.findall(search, text, re.IGNORECASE)) > 0):
        print('lan: ',dem)
        y = re.search(search, text, re.IGNORECASE)
        print(y.group(), y.span())
        list_group.append(y.group())
        text = insensitive.sub('<span class="highlight">{}</span>'.format('/&*replace*&/'), text, 1)
        #print(x)
        dem+=1
    print(list_group)
    insensitive = re.compile(re.escape('/&*replace*&/'), re.IGNORECASE)
    for i in list_group:
        text = insensitive.sub(i, text, 1)
    return text