from django.shortcuts import render
from django.core.paginator import Paginator
# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from elasticsearch_dsl.field import Keyword
from .documents import *
from .models import *
from .CollectData import *
import json
import time

from threading import Thread
import threading

from elastic import documents
# Create your views here.

progress_download = {}
progress_save = {}
data_documents_download = {} # chứa id các document đã tải của mỗi luồng
number_document_downloaded = {} # chứa số lượng tài liệu đã tải của mỗi luồng
number_document_saved = {} # chứa số lượng tài liệu đã lu

def source_delete(request):
    link_page = request.POST['link_page']
    source_name = request.POST['source_name']
    print('LINK PAGE: ', link_page)
    print('SOURCE_NAME: ', source_name)
    try:
        source = SourcesCorpus.objects.get(pageLink = link_page)
        source.delete()
        return JsonResponse({'mess': 'successful delete'})
    except:
        return JsonResponse({'mess': 'delete failed'})

def all_doc_from_source(request):
    #print(request.POST)
    
    link_page = request.GET['link_page']

    link_page = link_page.split('?')[0]

    #print('LINK PAGE: ', link_page)

    source = SourcesCorpus.objects.get(pageLink = link_page)
    
    documents = ParagraphsCorpus.objects.filter(sourcescorpus = source)

    #print('NUMMBER OBJECT: ', documents.count())
    '''for i in documents:
        print(i.title)
        print()'''
    list_title = []
    list_doc_id = []
    corpus_sentence = 0
    view = 'search_elastic'
    try:
        source = SourcesCorpus.objects.get(pageLink = link_page)
        #print('GỌI HÀM THÀNH CÔNG')
    except:
        return JsonResponse({'Thông báo': 'xpath đã nhập có thể chưa đúng'})
    
    for i in range(len(documents)):
        corpus_sentence += len(documents[i].get_en())
        list_title.append(documents[i].title)
        list_doc_id.append('?doc_id=' + str(documents[i].id))
    list_result = zip(list_title, list_doc_id)

    paginator = Paginator(documents, 15) # Show 15 contacts per page.

    if('page' in request.GET):
        page_number = request.GET.get('page')
    else:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    #print('PAGE: ', page_number)
    #print(request.GET)
    context = {'list_result': page_obj, 'length': documents.count(), 'view': view, 'corpus_sentence': corpus_sentence, 'link_page': link_page, 'is_paging_source': True}
    return render(request, 'index/result.html', context)
    
def search(request):
    if (request.method == 'GET'):
        print(request.GET)
        doc_id = request.GET['doc_id']
        try:
            doc = ParagraphsCorpus.objects.get(id = doc_id)
            title = doc.title
            en = doc.get_en()
            vi = doc.get_vi()
            copus = zip(en, vi)
            context = {'title': title,'copus': copus, 'length': len(vi)}
            return render(request, 'index/detail.html', context)
        except:
            print('KHÔNG TÌM THẤY KẾT QUẢ')
    if (request.method == 'POST'):
        print (request.POST)
        data = request.POST['data']
        print('DATA: ', data)
        s1 = SentencesDocument.search().query("match", en_sentence = data)
        s2 = SentencesDocument.search().query("match", vi_sentence = data)
        res = []
        for i in s1:
            en_res = highlight_search(i.en_sentence, data)
            vi_res = highlight_search(i.vi_sentence, data)
            res.append([en_res, vi_res])
            
            #res.append([i.en_sentence, i.vi_sentence])
        for i in s2:
            en_res = highlight_search(i.en_sentence, data)
            vi_res = highlight_search(i.vi_sentence, data)
            res.append([en_res, vi_res])
           
            #res.append([i.en_sentence, i.vi_sentence])

    return JsonResponse({'result': res})

def insert_handle(req):
    print('DA VAO THREAD')
    request = req
    thread_name = threading.currentThread().getName().split(' ')[0]
    link_page = request.POST['data[link_page]']
    link_document = request.POST['data[link_document]']
    isSave = request.POST['data[isSave]']
    if(isSave == 'true'):
        isSave = True
    else:
        isSave = False
    
    print('link_page: ', link_page)
    print('link_document: ', link_document)
    print('isSave:', isSave)

    source = SourcesCorpus.objects.get(pageLink = link_page)
    
    xpath_title = source.xpathGetTitle
    xpath_en = source.xpathGetEnContent
    xpath_vi = source.xpathGetViContent
    break_word = source.breakWord.split(',')
    
    if('' in break_word):
        break_word.remove('')
    for i in range(len(break_word)):
        break_word[i] = break_word[i].strip()

    continue_word = source.continueWord.split(',')
    
    if('' in continue_word):
        continue_word.remove('')
    for i in range(len(continue_word)):
        continue_word[i] = continue_word[i].strip()
    
    print('SAVE: ', isSave)
    print('LINK DOCUMENT: ', link_document)
    print('XPATH TITLE: ', xpath_title)
    print('XPATH EN: ', xpath_en)
    print('XPATH VI: ', xpath_vi)
    print('BREAK WORD: ', break_word)
    
    #if(bool(isSave) == True):
    global data_documents_download
    global number_document_saved
    global progress_save
    global progress_download
    global number_document_downloaded
    print('ĐỒNG Ý LƯU VÀO ELASTIC')
    try:
        # đoạn này kiểm tra trùng lặp bằng link document (lần 1)
        doc = ParagraphsCorpus.objects.get(link_document = link_document)
        title = doc.title
        en = doc.get_en()
        vi = doc.get_vi()
        print('DỮ LIỆU ĐÃ TỒN TẠI - KHÔNG CẦN CÀO NỮA')
        
        data_documents_download[thread_name] = [doc.id]

        number_document_downloaded[thread_name] = '1/1'
        number_document_saved[thread_name] = '1/1'

        progress_download[thread_name] = 100
        progress_save[thread_name] = 100
    except:
        try:
            title, vi, en = get_corpus(link_document,xpath_title,xpath_en,xpath_vi,break_word,continue_word)
            progress_download[thread_name] = 100
            number_document_downloaded[thread_name] = '1/1'
        except:
            pass
            #return JsonResponse({'Thông báo': 'xpath đã nhập hoặc link document có thể chưa đúng'})
        try:
            # đoạn này kiểm tra trùng lặp dữ liệu (lần 2) - bằng title của document
            already = ParagraphsCorpus.objects.get(title = title)
            if(already.sourcescorpus.id == source.id):
                print('DỮ LIỆU ĐÃ TỒN TẠI - KHÔNG LƯU')
                data_documents_download[thread_name] = [already.id]

                progress_download[thread_name] = 100
                progress_save[thread_name] = 100

                number_document_downloaded[thread_name] = '1/1'
                number_document_saved[thread_name] = '1/1'
        except:
            already = False
            print('DỮ LIỆU CHƯA TỒN TẠI')
            try:
                doc = ParagraphsCorpus()
                doc.set_title(title)
                doc.set_en(en)
                doc.set_vi(vi)
                doc.set_link_document(link_document)
                doc.sourcescorpus = source
                doc.save()
                data_documents_download[thread_name] = [doc.id]
                print('LƯU THÀNH CÔNG PARAGRAPH DOCUMENT')
                try:
                    num_sentence = len(vi)
                    num_loop_out = 1
                    
                    for i in range(len(vi)):
                        doc_st = SentencesCorpus(en_sentence = en[i], vi_sentence = vi[i], st_order = i)
                        print ('TẠO THÀNH CÔNG SENTENCE: ', i)
                        doc_st.paragraphscorpus = doc
                        doc_st.save()
                        print('LƯU THÀNH CÔNG SENTENCE: ', i)
                        progress_save[thread_name] = int(round(num_loop_out/num_sentence,2)*100)
                        number_document_downloaded[thread_name] = '1/1'
                        number_document_saved[thread_name] = str(num_loop_out) + '/' + str(num_sentence) + ' (sentences)'
                        num_loop_out+=1
                    if(len(vi)==0 or len(en)==0):
                        progress_save[thread_name] = 100
                        number_document_downloaded[thread_name] = '1/1'
                        number_document_saved[thread_name] = '0/0' + ' (sentences)'
                        
                except:
                    print('KHÔNG LƯU ĐƯỢC SENTENCE')
                print('LƯU THÀNH CÔNG')
            except:
                print('LƯU KHÔNG THÀNH CÔNG')
    '''else:
        print('NGƯỜI DÙNG KHÔNG LƯU DỮ LIỆU VÀO ELASTIC')
        try:
            title, vi, en = get_corpus(link_document,xpath_title,xpath_en,xpath_vi,break_word)
        except:
            return JsonResponse({'Thông báo': 'xpath đã nhập hoặc link document có thể chưa đúng'})
    copus = zip(en, vi)
    context = {'title': title,'copus': copus, 'length': len(vi)}
    return render(request, 'index/detail.html', context)'''
    #return JsonResponse({'ket qua': 'thanh cong them mot'})
def insert(request):
    try:
        t1 = Thread(target=insert_handle, kwargs={'req': request})
        thread_name = t1.getName().split(' ')[0]

        global progress_download
        progress_download[thread_name] = 0

        global progress_save
        progress_save[thread_name] = 0

        global number_document_downloaded
        number_document_downloaded[thread_name] = 0

        global number_document_saved
        number_document_saved[thread_name] = 0
        t1.start()
    except:
        print ("error")
    return JsonResponse({'Thread name': thread_name})

def range_insert_handle (req):
    request = req

    print('RANGE INSERT')
    print(request.POST)
    start = int(request.POST['from'])
    end = int(request.POST['to'])
    link_page = request.POST['link_page']
    isSave = request.POST['isSave']
    if(isSave == 'true'):
        isSave = True
    else:
        isSave = False
    
    source = SourcesCorpus.objects.get(pageLink = link_page)

    print('ĐANG TẢI DỮ LIỆU TỪ NGUỒN: ', source.pageName)
    thread_name = threading.currentThread().getName().split(' ')[0]
    #print('ĐÃ TẢI XONG CHO NGUỒN:', source.pageName)
    
    source = SourcesCorpus.objects.get(pageLink = link_page)
    
    xpath_doc_links = source.xpathGetDocLinks
    xpath_title = source.xpathGetTitle
    xpath_en = source.xpathGetEnContent
    xpath_vi = source.xpathGetViContent
    page_query = source.pageQuery
    link_page = source.pageLink
    break_word = source.breakWord.split(',')
    
    if('' in break_word):
        break_word.remove('')
    for i in range(len(break_word)):
        break_word[i] = break_word[i].strip()

    continue_word = source.continueWord.split(',')
    
    if('' in continue_word):
        continue_word.remove('')
    for i in range(len(continue_word)):
        continue_word[i] = continue_word[i].strip()
    
    print('SAVE: ', isSave)
    print('LINK PAGE: ', link_page)
    print('PAGE QUERY: ', page_query)
    print('XPATH DOC LINK: ', xpath_doc_links)
    print('XPATH TITLE: ', xpath_title)
    print('XPATH EN: ', xpath_en)
    print('XPATH VI: ', xpath_vi)
    print('BREAK WORD: ', break_word)
    print('START: ', start)
    print('END: ', end)
    
    list_doc_id = []
    view = 'search_elastic'
    #if(bool(isSave) == True):
    print('ĐỒNG Ý LƯU VÀO ELASTIC')
    try:
        result = collect_corpus_by_range_page(thread_name, start, end, link_page, page_query, xpath_doc_links, xpath_title, xpath_en, xpath_vi, break_word, continue_word)
        print('GỌI HÀM THÀNH CÔNG')
    except:
        return JsonResponse({'Thông báo': 'xpath đã nhập có thể chưa đúng'})
    
    documents_count = len(result)
    num_loop_out=1
    for i in result:
        try:
            already = ParagraphsCorpus.objects.get(title = i)
            if(already.sourcescorpus.id == source.id):
                list_doc_id.append(already.id)
                print('DỮ LIỆU ĐÃ TỒN TẠI - KHÔNG LƯU: ', already.title)
        except:
            already = False
            print('DỮ LIỆU CHƯA TỒN TẠI')
            try:
                doc = ParagraphsCorpus()
                doc.set_title(i)
                doc.set_en(result[i]['en'])
                doc.set_vi(result[i]['vi'])
                doc.set_link_document(result[i]['link'])
                doc.sourcescorpus = source
                doc.save()
                list_doc_id.append(doc.id)
                print('LƯU THÀNH CÔNG PARAGRAPH DOCUMENT')
                try:
                    for j in range(len(result[i]['vi'])):
                        try:
                            doc_st = SentencesCorpus(en_sentence = result[i]['en'][j], vi_sentence = result[i]['vi'][j], st_order = j)
                            print ('TẠO THÀNH CÔNG SENTENCE: ', i)
                            doc_st.paragraphscorpus = doc
                            doc_st.save()
                            print('LƯU THÀNH CÔNG SENTENCE: ', i)
                        except:
                            continue
                except:
                    print('KHÔNG LƯU ĐƯỢC SENTENCE')
                print('LƯU THÀNH CÔNG')
            except:
                print('LƯU KHÔNG THÀNH CÔNG')
        global progress_save
        progress_save[thread_name] = int(round(num_loop_out/documents_count,2)*100)

        global number_document_saved
        number_document_saved[thread_name] = str(num_loop_out) + '/' + str(documents_count)

        num_loop_out+=1
    global data_documents_download
    data_documents_download[thread_name] = list_doc_id 
    '''else:
        print('NGƯỜI DÙNG KHÔNG LƯU VÀO ELASTIC')
        try:
            titles = collect_title_by_range_page(start, end, link_page, page_query, xpath_doc_links, xpath_title)
            print('titles: ', titles)
            context = {'titles': titles, 'length': len(titles)}
            return render(request, 'index/result.html', context)
        except:
            return JsonResponse({'Thông báo': 'xpath để lấy title hoặc xpath để lấy link docment chưa đúng'})
    #print('NGƯỜI DÙNG KHÔNG LƯU DỮ LIỆU')
    #return JsonResponse({'Thông báo': 'Chức năng này chỉ hoạt động khi bạn tick vào mục "Lưu vào elastic search"'})'''

def range_inserts(request):
    try:
        t1 = Thread(target=range_insert_handle, kwargs={'req': request})
        thread_name = t1.getName().split(' ')[0]

        global progress_download
        progress_download[thread_name] = 0

        global progress_save
        progress_save[thread_name] = 0

        global number_document_downloaded
        number_document_downloaded[thread_name] = 0

        global number_document_saved
        number_document_saved[thread_name] = 0
        t1.start()
    except:
        print ("error")
    return JsonResponse({'Thread name': thread_name})

def multipage_insert_handle (req):
    request = req

    list_pages = request.POST['list_pages']
    list_pages = list_pages.split(',')
    
    for i in range(len(list_pages)):
        list_pages[i] = list_pages[i].strip()
    
    link_page = request.POST['link_page']

    isSave = request.POST['isSave']
    if(isSave == 'true'):
        isSave = True
    else:
        isSave = False
    
    source = SourcesCorpus.objects.get(pageLink = link_page)

    print('ĐANG TẢI DỮ LIỆU TỪ NGUỒN: ', source.pageName)
    thread_name = threading.currentThread().getName().split(' ')[0]

    #print('ĐÃ TẢI XONG CHO NGUỒN:', source.pageName)
    xpath_doc_links = source.xpathGetDocLinks
    xpath_title = source.xpathGetTitle
    xpath_en = source.xpathGetEnContent
    xpath_vi = source.xpathGetViContent
    page_query = source.pageQuery
    link_page = source.pageLink
    break_word = source.breakWord.split(',')
    
    if('' in break_word):
        break_word.remove('')
    for i in range(len(break_word)):
        break_word[i] = break_word[i].strip()

    continue_word = source.continueWord.split(',')
    
    if('' in continue_word):
        continue_word.remove('')
    for i in range(len(continue_word)):
        continue_word[i] = continue_word[i].strip()
    
    print('SAVE: ', isSave)
    print('LINK PAGE: ', link_page)
    print('PAGE QUERY: ', page_query)
    print('XPATH DOC LINK: ', xpath_doc_links)
    print('XPATH TITLE: ', xpath_title)
    print('XPATH EN: ', xpath_en)
    print('XPATH VI: ', xpath_vi)
    print('BREAK WORD: ', break_word)
    
    list_doc_id = []

    view = 'search_elastic'
    #if(bool(isSave) == True):
    print('ĐỒNG Ý LƯU VÀO ELASTIC')
    try:
        result = collect_corpus_by_list_pages(thread_name, list_pages, link_page, page_query, xpath_doc_links, xpath_title, xpath_en, xpath_vi, break_word, continue_word)
    except:
        return JsonResponse({'Thông báo': 'xpath đã nhập có thể chưa đúng'})
    
    documents_count = len(result)
    num_loop_out=1
    for i in result:
        try:
            already = ParagraphsCorpus.objects.get(title = i)
            if(already.sourcescorpus.id == source.id):
                list_doc_id.append(already.id)
                print('DỮ LIỆU ĐÃ TỒN TẠI - KHÔNG LƯU: ', already.title)
        except:
            already = False
            print('DỮ LIỆU CHƯA TỒN TẠI')
            try:
                doc = ParagraphsCorpus()
                doc.set_title(i)
                doc.set_en(result[i]['en'])
                doc.set_vi(result[i]['vi'])
                doc.set_link_document(result[i]['link'])
                doc.sourcescorpus = source
                doc.save()
                list_doc_id.append(doc.id)
                print('LƯU THÀNH CÔNG PARAGRAPH DOCUMENT')
                try:
                    for j in range(len(result[i]['vi'])):
                        try:
                            doc_st = SentencesCorpus(en_sentence = result[i]['en'][j], vi_sentence = result[i]['vi'][j], st_order = j)
                            print ('TẠO THÀNH CÔNG SENTENCE: ', i)
                            doc_st.paragraphscorpus = doc
                            doc_st.save()
                            print('LƯU THÀNH CÔNG SENTENCE: ', i)
                        except:
                            pass
                except:
                    print('KHÔNG LƯU ĐƯỢC SENTENCE')
                print('LƯU THÀNH CÔNG')
            except:
                print('LƯU KHÔNG THÀNH CÔNG')
        
        global progress_save
        progress_save[thread_name] = int(round(num_loop_out/documents_count,2)*100)

        global number_document_saved
        number_document_saved[thread_name] = str(num_loop_out) + '/' + str(documents_count)

        num_loop_out+=1
    global data_documents_download
    data_documents_download[thread_name] = list_doc_id
    '''else:
        print('NGƯỜI DÙNG KHÔNG LƯU VÀO ELASTIC')
        try:
            titles = collect_title_by_list_pages(list_pages, link_page, page_query, xpath_doc_links, xpath_title)
            print('titles: ', titles)
            context = {'titles': titles, 'length': len(titles)}
            return render(request, 'index/result.html', context)
        except:
            return JsonResponse({'Thông báo': 'xpath để lấy title hoặc xpath để lấy link docment chưa đúng'})
    #print('NGƯỜI DÙNG KHÔNG LƯU DỮ LIỆU')
    #return JsonResponse({'Thông báo': 'Chức năng này chỉ hoạt động khi bạn tick vào mục "Lưu vào elastic search"'})'''

def update_progress_download(request):
    thread_name = request.POST['thread_name']
    global progress_download
    progress = progress_download[thread_name]

    global number_document_downloaded
    documents_downloaded = number_document_downloaded[thread_name]
     
    return JsonResponse({'progress': progress, 'downloaded': documents_downloaded})

def update_progress_save(request):
    thread_name = request.POST['thread_name']
    global progress_save
    progress = progress_save[thread_name]

    global number_document_saved
    num_of_saved = number_document_saved[thread_name]
    return JsonResponse({'progress': progress, 'saved': num_of_saved})

def multipage_inserts(request):
    try:
        t1 = Thread(target=multipage_insert_handle, kwargs={'req': request})
        thread_name = t1.getName().split(' ')[0]

        global progress_download
        progress_download[thread_name] = 0

        global progress_save
        progress_save[thread_name] = 0

        global number_document_downloaded
        number_document_downloaded[thread_name] = 0

        global number_document_saved
        number_document_saved[thread_name] = 0
        t1.start()

    except:
        print ("error")
    return JsonResponse({'Thread name': thread_name})

def result_list_document(request):
    print(request.GET)
    thread_name = request.GET['thread_name']
    print('THREAD NAME: ', thread_name)
    documents = []
    global data_documents_download
    list_doc_downloaded_id = data_documents_download[thread_name]
    for i in list_doc_downloaded_id:
        try:
            doc = ParagraphsCorpus.objects.get(id = i)
            documents.append(doc)
        except:
            continue
    print('NUMMBER OBJECT: ', len(documents))

    list_title = []
    list_doc_id = []
    corpus_sentence = 0
    view = 'search_elastic'
    
    for i in range(len(documents)):
        corpus_sentence += len(documents[i].get_en())
        list_title.append(documents[i].title)
        list_doc_id.append('?doc_id=' + str(documents[i].id))
    list_result = zip(list_title, list_doc_id)

    paginator = Paginator(documents, 15) # Show 15 contacts per page.

    if('page' in request.GET):
        page_number = request.GET.get('page')
    else:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    context = {'list_result': page_obj, 'length': len(documents), 'view': view, 'corpus_sentence': corpus_sentence,'is_paging_result': True, 'thread_name': thread_name}
    return render(request, 'index/result.html', context)    

def delete_doc(request):
    docId = request.POST['docId']
    print(docId)
    doc = ParagraphsCorpus.objects.get(id=docId)#.delete()
    try:
        doc.delete()
        return JsonResponse({'mess': 'successful delete'})
    except:
        return JsonResponse({'mess': 'delete failed'})

##################################################################################################
# Hàm này dùng để crawl link các tài liệu cần thu thập từ trang chính
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

# Hàm này dùng để crawl dữ liệu song ngữ theo khoản trang
def collect_corpus_by_range_page(thread_name, start, end, link_page, page_query, document_links_xpath, title_xpath, en_xpath, vi_xpath, break_word, continue_word):
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
    '''for i in links:
        print(i)'''
    
    global progress_download
    global number_document_downloaded
    
    links_document_count = len(links)
    num_loop = 1
    for path in links:
        progress_download[thread_name] = int(round(num_loop/links_document_count,2)*100)          
        number_document_downloaded[thread_name] = str(num_loop) + '/' + str(links_document_count)
        num_loop+=1
        if ('%' not in path):
            path = url_encode(path)
        try:
            doc = ParagraphsCorpus.objects.get(link_document = path)
            title = doc.title
            en = doc.get_en()
            vi = doc.get_vi()
            print('DỮ LIỆU ĐÃ TỒN TẠI - KHÔNG CẦN CÀO NỮA')

        except:
            try:
                title, vi, en = get_corpus(path, title_xpath, en_xpath, vi_xpath, break_word, continue_word)

                check_continue = False
                for l in range(len(vi)):
                    len_vi = len(vi[l].split(' '))
                    len_en = len(en[l].split(' '))
                    print('check_len_vi: ', len_vi)
                    print('check_len_en: ', len_en)
                    if(len_vi < 0.25*len_en or len_en < 0.25*len_vi):
                        print('KHÔNG CHÍNH XÁC - CONTINUE')
                        check_continue = True
                        break
                if(check_continue == True):
                    print('KHÔNG CHÍNH XÁC - CONTINUE')
                    continue
            except:
                continue
        if(len(vi)!= 0 and len(en)!=0):
            result[title] = {'vi': vi, 'en': en, 'link': path}

    return result

# Hàm này dùng tải dữ liệu song ngữ theo danh sách trang
def collect_corpus_by_list_pages(thread_name, list_pages, link_page, page_query, document_links_xpath, title_xpath, en_xpath, vi_xpath, break_word, continue_word):
    links = []
    result = {}
    for i in list_pages:
        page_path = link_page + page_query + str(i)

        for j in collect_document_links(page_path, document_links_xpath):
            links.append(j)
    '''for i in links:
        print(i)'''
    
    global progress_download
    global number_document_downloaded

    links_document_count = len(links)
    num_loop = 1
    for path in links:
        progress_download[thread_name] = int(round(num_loop/links_document_count,2)*100)
        number_document_downloaded[thread_name] = str(num_loop) + '/' + str(links_document_count)
        num_loop+=1
        if ('%' not in path):
            path = url_encode(path)
        try:
            doc = ParagraphsCorpus.objects.get(link_document = path)
            title = doc.title
            en = doc.get_en()
            vi = doc.get_vi()
            print('DỮ LIỆU ĐÃ TỒN TẠI - KHÔNG CẦN CÀO NỮA')

        except:
            try:
                title, vi, en = get_corpus(path, title_xpath, en_xpath, vi_xpath, break_word, continue_word)
                
                check_continue = False
                for l in range(len(vi)):
                    len_vi = len(vi[l].split(' '))
                    len_en = len(en[l].split(' '))
                    print('check_len_vi: ', len_vi)
                    print('check_len_en: ', len_en)
                    if(len_vi < 0.25*len_en or len_en < 0.25*len_vi):
                        print('KHÔNG CHÍNH XÁC - CONTINUE')
                        check_continue = True
                        break
                if(check_continue == True):
                    print('KHÔNG CHÍNH XÁC - CONTINUE')
                    continue
            except:
                continue

        if(len(vi) != len(en)):
            continue
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
