from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
#from .documents import *
from .models import *
from .CollectData import *
import json
# Create your views here.

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
    return JsonResponse({'Kết quả':' Xem chi tiết'})

def insert(request):
    print(request.POST)
    link_page = request.POST['source']

    source = SourcesCorpus.objects.get(pageLink = link_page)
    
    link_document = request.POST['link_document']
    xpath_title = source.xpathGetTitle
    xpath_en = source.xpathGetEnContent
    xpath_vi = source.xpathGetViContent
    break_word = source.breakWord.split(',')
    
    if('' in break_word):
        break_word.remove('')
    for i in range(len(break_word)):
        break_word[i] = break_word[i].strip()
    if('save' in request.POST):
        isSave = request.POST['save']
    else:
        isSave = False
    
    print('SAVE: ', isSave)
    print('LINK DOCUMENT: ', link_document)
    print('XPATH TITLE: ', xpath_title)
    print('XPATH EN: ', xpath_en)
    print('XPATH VI: ', xpath_vi)
    print('BREAK WORD: ', break_word)
    
    if(bool(isSave) == True):
        print('ĐỒNG Ý LƯU VÀO ELASTIC')
        try:
            title, vi, en = get_corpus(link_document,xpath_title,xpath_en,xpath_vi,break_word)
        except:
            return JsonResponse({'Thông báo': 'xpath đã nhập hoặc link document có thể chưa đúng'})
        try:
            already = ParagraphsCorpus.objects.get(title = title)
            if(already.sourcescorpus.id == source.id):
                print(already)
                print('DỮ LIỆU ĐÃ TỒN TẠI - KHÔNG LƯU')
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
                print('LƯU THÀNH CÔNG PARAGRAPH DOCUMENT')
                try:
                    for i in range(len(vi)):
                        doc_st = SentencesCorpus(en_sentence = en[i], vi_sentence = vi[i], st_order = i)
                        print ('TẠO THÀNH CÔNG SENTENCE: ', i)
                        doc_st.paragraphscorpus = doc
                        doc_st.save()
                        print('LƯU THÀNH CÔNG SENTENCE: ', i)
                except:
                    print('KHÔNG LƯU ĐƯỢC SENTENCE')
                print('LƯU THÀNH CÔNG')
            except:
                print('LƯU KHÔNG THÀNH CÔNG')
    else:
        print('NGƯỜI DÙNG KHÔNG LƯU DỮ LIỆU VÀO ELASTIC')
        try:
            title, vi, en = get_corpus(link_document,xpath_title,xpath_en,xpath_vi,break_word)
        except:
            return JsonResponse({'Thông báo': 'xpath đã nhập hoặc link document có thể chưa đúng'})
    copus = zip(en, vi)
    context = {'title': title,'copus': copus, 'length': len(vi)}
    return render(request, 'index/detail.html', context)
    #return JsonResponse({'ket qua': 'thanh cong them mot'})

def range_inserts(request):
    print(request.POST)
    start = int(request.POST['from'])
    end = int(request.POST['to'])
    link_page = request.POST['source']
    
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
    if('save' in request.POST):
        isSave = request.POST['save']
    else:
        isSave = False
    
    print('SAVE: ', isSave)
    print('LINK PAGE: ', link_page)
    print('PAGE QUERY: ', page_query)
    print('XPATH DOC LINK: ', xpath_doc_links)
    print('XPATH TITLE: ', xpath_title)
    print('XPATH EN: ', xpath_en)
    print('XPATH VI: ', xpath_vi)
    print('BREAK WORD: ', break_word)
    
    list_title = []
    list_doc_id = []
    corpus_sentence = 0
    view = 'search_elastic'
    if(bool(isSave) == True):
        print('ĐỒNG Ý LƯU VÀO ELASTIC')
        try:
            result = collect_corpus_by_range_page(start, end, link_page, page_query, xpath_doc_links, xpath_title, xpath_en, xpath_vi, break_word)
        except:
            return JsonResponse({'Thông báo': 'xpath đã nhập có thể chưa đúng'})
        
        for i in result:
            corpus_sentence += len(result[i]['vi'])
            list_title.append(i)
            try:
                already = ParagraphsCorpus.objects.get(title = i)
                if(already.sourcescorpus.id == source.id):
                    list_doc_id.append('?doc_id=' + str(already.id))
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
                    list_doc_id.append('?doc_id=' + str(doc.id))
                    print('LƯU THÀNH CÔNG PARAGRAPH DOCUMENT')
                    try:
                        for j in range(len(result[i]['vi'])):
                            doc_st = SentencesCorpus(en_sentence = result[i]['en'][j], vi_sentence = result[i]['vi'][j], st_order = j)
                            print ('TẠO THÀNH CÔNG SENTENCE: ', i)
                            doc_st.paragraphscorpus = doc
                            doc_st.save()
                            print('LƯU THÀNH CÔNG SENTENCE: ', i)
                    except:
                        print('KHÔNG LƯU ĐƯỢC SENTENCE')
                    print('LƯU THÀNH CÔNG')
                except:
                    print('LƯU KHÔNG THÀNH CÔNG')
        list_result = zip(list_title, list_doc_id)
        context = {'list_result': list_result, 'length': len(result), 'view': view, 'corpus_sentence': corpus_sentence}
        return render(request, 'index/result.html', context)
    else:
        print('NGƯỜI DÙNG KHÔNG LƯU VÀO ELASTIC')
        try:
            titles = collect_title_by_range_page(start, end, link_page, page_query, xpath_doc_links, xpath_title)
            print('titles: ', titles)
            context = {'titles': titles, 'length': len(titles)}
            return render(request, 'index/result.html', context)
        except:
            return JsonResponse({'Thông báo': 'xpath để lấy title hoặc xpath để lấy link docment chưa đúng'})
    #print('NGƯỜI DÙNG KHÔNG LƯU DỮ LIỆU')
    #return JsonResponse({'Thông báo': 'Chức năng này chỉ hoạt động khi bạn tick vào mục "Lưu vào elastic search"'})

def multipage_inserts(request):
    print(request.POST)
    list_pages = request.POST['list_pages']
    list_pages = list_pages.split(',')
    
    for i in range(len(list_pages)):
        list_pages[i] = list_pages[i].strip()
    
    link_page = request.POST['source']
    
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
    if('save' in request.POST):
        isSave = request.POST['save']
    else:
        isSave = False
    
    print('SAVE: ', isSave)
    print('LINK PAGE: ', link_page)
    print('PAGE QUERY: ', page_query)
    print('XPATH DOC LINK: ', xpath_doc_links)
    print('XPATH TITLE: ', xpath_title)
    print('XPATH EN: ', xpath_en)
    print('XPATH VI: ', xpath_vi)
    print('BREAK WORD: ', break_word)
    
    list_title = []
    list_doc_id = []
    corpus_sentence = 0
    view = 'search_elastic'
    if(bool(isSave) == True):
        print('ĐỒNG Ý LƯU VÀO ELASTIC')
        try:
            result = collect_corpus_by_list_pages(list_pages, link_page, page_query, xpath_doc_links, xpath_title, xpath_en, xpath_vi, break_word)
        except:
            return JsonResponse({'Thông báo': 'xpath đã nhập có thể chưa đúng'})
        for i in result:
            list_title.append(i)
            corpus_sentence += len(result[i]['vi'])
            try:
                already = ParagraphsCorpus.objects.get(title = i)
                if(already.sourcescorpus.id == source.id):
                    list_doc_id.append('?doc_id=' + str(already.id))
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
                    list_doc_id.append('?doc_id=' + str(doc.id))
                    print('LƯU THÀNH CÔNG PARAGRAPH DOCUMENT')
                    try:
                        for j in range(len(result[i]['vi'])):
                            doc_st = SentencesCorpus(en_sentence = result[i]['en'][j], vi_sentence = result[i]['vi'][j], st_order = j)
                            print ('TẠO THÀNH CÔNG SENTENCE: ', i)
                            doc_st.paragraphscorpus = doc
                            doc_st.save()
                            print('LƯU THÀNH CÔNG SENTENCE: ', i)
                    except:
                        print('KHÔNG LƯU ĐƯỢC SENTENCE')
                    print('LƯU THÀNH CÔNG')
                except:
                    print('LƯU KHÔNG THÀNH CÔNG')
        list_result = zip(list_title, list_doc_id)
        context = {'list_result': list_result, 'length': len(result), 'view': view, 'corpus_sentence': corpus_sentence}
        return render(request, 'index/result.html', context)
    else:
        print('NGƯỜI DÙNG KHÔNG LƯU VÀO ELASTIC')
        try:
            titles = collect_title_by_list_pages(list_pages, link_page, page_query, xpath_doc_links, xpath_title)
            print('titles: ', titles)
            context = {'titles': titles, 'length': len(titles)}
            return render(request, 'index/result.html', context)
        except:
            return JsonResponse({'Thông báo': 'xpath để lấy title hoặc xpath để lấy link docment chưa đúng'})
    #print('NGƯỜI DÙNG KHÔNG LƯU DỮ LIỆU')
    #return JsonResponse({'Thông báo': 'Chức năng này chỉ hoạt động khi bạn tick vào mục "Lưu vào elastic search"'})



