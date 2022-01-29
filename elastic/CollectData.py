from distutils.command.check import check
from django_elasticsearch_dsl.search import Search
import requests
from lxml import html
import urllib
import urllib.parse
from langdetect import detect
import langid
import re
from elastic.models import ParagraphsCorpus
import nltk
import nltk.data


def url_encode(url):
    com = urllib.parse.urlparse(url)
    encoded = com.scheme + '://' + com.netloc + urllib.parse.quote(com.path)
    return encoded

def get_corpus(url, title_xpath, en_xpath, vi_xpath, break_word, continue_word):
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
    en_nltk = []
    vi = []
    vi_nltk = []
    
    for i in range(len(break_word)):
        break_word[i] = break_word[i].upper().strip()
    print(break_word)

    for i in range(len(continue_word)):
        continue_word[i] = continue_word[i].upper().strip()
    print(continue_word)
    
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
        if (tmp == '' or len(tmp.split(' ')) <= 3  or tmp.replace('\n','') in en):
            print('continue')
            continue
        break_scan = False
        continue_scan = False
        for i in break_word:     
            if(i in tmp.upper()):
                break_scan = True
        if(break_scan == True):
            print('Gặp break word')
            break
        for i in continue_word:     
            if(i in tmp.upper()):
                continue_scan = True
        if(continue_scan == True):
            print('Gặp continue word')
            continue

        ############
        print('XỬ LÝ PHÂN LOẠI NGÔN NGỮ - EN')
        try:
            de  = detect(tmp)
            cl = langid.classify(tmp)[0]
            count_vi = 0
            count_en = 0
            if(de == 'vi' or cl == 'vi'):
                count_vi += 1
            if(de == 'en' or cl == 'en'):
                count_en += 1
            #------------------------------
            if(len(tmp.split(' ')) < 15):
                lang = lang_classify(tmp, 'en')
                if (lang == 'en'):
                    tmp_split = split_sentence(tmp.replace('\n',''))
                    for sen in tmp_split:
                        en_nltk.append(sen)
                    en.append(tmp.replace('\n',''))
                    print('Duyệt')
            elif (de == 'en' and  cl == 'en'):
                tmp_split = split_sentence(tmp.replace('\n',''))
                for sen in tmp_split:
                    en_nltk.append(sen)
                en.append(tmp.replace('\n',''))
                print('Duyệt')
                print('thêm vào en - không gọi hàm phân loại')
            elif (count_vi == count_en):
                lang = lang_classify(tmp, 'en')
                print('lang: ', lang)
                if (lang == 'en'):
                    print('thêm vào en')
                    tmp_split = split_sentence(tmp.replace('\n',''))
                    for sen in tmp_split:
                        en_nltk.append(sen)
                    en.append(tmp.replace('\n',''))
                    print('Duyệt')
            elif (de != 'vi' or  cl != 'vi'):
                lang = lang_classify(tmp, 'en')
                print('lang: ', lang)
                if (lang == 'en'):
                    print('thêm vào en')
                    tmp_split = split_sentence(tmp.replace('\n',''))
                    for sen in tmp_split:
                        en_nltk.append(sen)
                    en.append(tmp.replace('\n',''))
                    print('Duyệt')
            else:
                print('Cho qua')
            ############
            print('EN:', len(en))
        except:
            print('EN:', len(en))
            print('Dính lỗi định danh')

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
        if (tmp == '' or len(tmp.split(' ')) <= 3 or tmp.replace('\n','') in vi):
            print('continue')
            continue
        
        break_scan = False
        continue_scan = False
        for i in break_word:     
            if(i in tmp.upper()):
                break_scan = True
        if(break_scan == True):
            print('Gặp break word')
            break
        for i in continue_word:     
            if(i in tmp.upper()):
                continue_scan = True
        if(continue_scan == True):
            print('Gặp continue word')
            continue

        ############
        print('XỬ LÝ PHÂN LOẠI NGÔN NGỮ - VI')
        try:
            de  = detect(tmp)
            cl = langid.classify(tmp)[0]
            count_vi = 0
            count_en = 0
            if(de == 'vi' or cl == 'vi'):
                count_vi += 1
            if(de == 'en' or cl == 'en'):
                count_en += 1
            #------------------------------
            if(len(tmp.split(' ')) < 15):
                lang = lang_classify(tmp, 'vi')
                if (lang == 'vi'):
                    tmp_split = split_sentence(tmp.replace('\n',''))
                    for sen in tmp_split:
                        vi_nltk.append(sen)
                    vi.append(tmp.replace('\n',''))
                    print('Duyệt')
            elif (de == 'vi' and  cl == 'vi'):
                tmp_split = split_sentence(tmp.replace('\n',''))
                for sen in tmp_split:
                    vi_nltk.append(sen)
                vi.append(tmp.replace('\n',''))
                print('Duyệt')
            elif (count_vi == count_en):
                lang = lang_classify(tmp, 'vi')
                if (lang == 'vi'):
                    tmp_split = split_sentence(tmp.replace('\n',''))
                    for sen in tmp_split:
                        vi_nltk.append(sen)
                    vi.append(tmp.replace('\n',''))
                    print('Duyệt')
            elif (de != 'en' or  cl != 'en'):
                lang = lang_classify(tmp, 'vi')
                if (lang == 'vi'):
                    tmp_split = split_sentence(tmp.replace('\n',''))
                    for sen in tmp_split:
                        vi_nltk.append(sen)
                    vi.append(tmp.replace('\n',''))
                    print('Duyệt')
            else:
                print('cho qua')
            ############
            print('VI:', len(vi))
        except:
            print('VI:', len(vi))
            print('Dính lỗi định danh')

    if(len(en_nltk) == len(vi_nltk)):
        vi_nltk = list(dict.fromkeys(vi_nltk))
        en_nltk = list(dict.fromkeys(en_nltk))
        ######################
        # XỬ LÝ CẮT CÂU
        if(len(vi_nltk) == 1 and len(en_nltk) == 1):
            print('XỬ LÝ CẮT CÂU')
            vi_nltk = split_sentence(vi_nltk[0])
            en_nltk = split_sentence(en_nltk[0])
            if(len(vi) != len(en)):
                nl_vi, nl_en = normalize_sentence(vi, en)
                if(len(nl_vi) == len(nl_en)):
                    vi_nltk = nl_vi
                    en_nltk = nl_en
        ######################
        check_valid = False
        print('Đang trong hàm collect')
        for l in range(len(vi_nltk)):
            len_vi = len(vi_nltk[l].split(' '))
            len_en = len(en_nltk[l].split(' '))
            print('check_len_vi: ', len_vi)
            print('check_len_en: ', len_en)
            if(len_vi < 0.35*len_en or len_en < 0.35*len_vi):
                #print('KHÔNG CHÍNH XÁC - CONTINUE')
                check_valid = True
                break
        if(check_valid == False):
            #print('KHÔNG CHÍNH XÁC - CONTINUE')
            return title, vi_nltk, en_nltk
    #else:
    vi = list(dict.fromkeys(vi))
    en = list(dict.fromkeys(en))
    
    print(len(vi))
    print(len(en))

    ######################
    # XỬ LÝ CẮT CÂU
    if(len(vi) == 1 and len(en) == 1):
        print('XỬ LÝ CẮT CÂU')
        vi = split_sentence(vi[0])
        en = split_sentence(en[0])
        if(len(vi) != len(en)):
            nl_vi, nl_en = normalize_sentence(vi, en)
            if(len(nl_vi) == len(nl_en)):
                vi = nl_vi
                en = nl_en
    ######################
    min = len(vi)
    if(min > len(en)):
        min = len(en)
        vi = vi[:min]
    else:
        en = en[:min]

    print('TITLE: ', title)
    print('EN: ', en)
    print('VI: ', vi)
    return title, vi, en

# Hạm này dùng để phân câu cho một đoạn
def split_sentence(text):
    nltk.download('punkt')
    sent_text = nltk.sent_tokenize(text)
    return sent_text

# Hàm này sẽ 'cố gắng' sữa lỗi chia subtitle theo câu không đồng nhất
# Vì trong thực tế việc dịch thuật không đồng nhất giữa những người dịch dẫn đến việc dữ liệu không khớp nhau về cách chia câu
# Ví dụ: 1 câu ở Tiếng Anh. Lại được dịch nhiều câu ở Tiếng việt và ngược lại
def normalize_sentence(doc1, doc2):
    length1 = 0
    length2 = 0
    min = 0
    max = 0
    i = 0
    while(i < len(doc1) and i < len(doc2)):
        if (len(doc1) == len(doc2)):
            break
        doc1[i] = doc1[i].replace('  ',' ')
        doc2[i] = doc2[i].replace('  ',' ')
        length1 = len(doc1[i].split(' '))
        length2 = len(doc2[i].split(' '))
        #print(length1, ':', doc1[i])
        
        #print(length2, ':', doc2[i])
        max = length1
        min = length2
        if(length1 < length2):
            max = length2
            min = length1
        error = float(min/max)
        #print(error)
        if (error <= 65):
            #print(doc1[i])
            #print(doc2[i])
            #print('trung error:[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]')
            try:
                if(length1 < length2 and i < len(doc1)-1):
                    doc1[i] = doc1[i] + ' ' + doc1[i+1]
                    del doc1[i+1]
                    i+=1
                if(length1 > length2 and i < len(doc2)-1):
                    doc2[i] = doc2[i] + doc2[i+1]
                    del doc2[i+1]
                    i+=1
            except:
                break
        #print('=====================================================================')
        i+=1
    return doc1, doc2

# Hàm này dùng để phân loại ngôn ngữ theo thành phần chữ cái
def lang_classify(text, lang):
    print('vao ham: ', text)
    if(lang == 'vi'):
        other_lang = 'en'
    elif(lang == 'en'):
        other_lang = 'vi'
    count_lang = 0
    count_other_lang = 0
    for i in text.split(' '):
        try:
            de = detect(i)
            cl = langid.classify(i)[0]
            if(de == lang or cl == lang):
                count_lang += 1
            if(de == other_lang or cl == other_lang):
                count_other_lang += 1
        except:
            continue
    count_word  = len(text.split(' '))

    if(count_other_lang < count_lang):
        print('Duyệt xử lý thứ cấp: ', text.replace('\n',''))
        return lang
    else:
        print("Cho qua")
        return other_lang


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


