from django.shortcuts import render
from django.http import HttpResponse
from elastic.documents import *
import nltk
import nltk.data
# Create your views here.

def index(request):
    #try:
    nltk.download('punkt')
    sent_text = nltk.sent_tokenize('hello. name is')
    print(sent_text, " ", len(sent_text))
    #except:
        #print('Khong tao duoc session')

    source_link = []
    page_name = []
    try:
        #s = SourceCorpusDocument.search()
        s = SourcesCorpus.objects.all()
        for hit in s:
            #print ('PAGE LINK: ', hit.pageLink)
            #print ('PAGE NAME: ', hit.pageName)
            source_link.append(hit.pageLink)
            page_name.append(hit.pageName)
        print('ĐỘ DÀI PHẦN TỬ: ', len(source_link))
    except:
        print('KHÔNG CÓ DỮ LIỆU CẦN TÌM')

    #s = SourcesCorpus.objects.get(pageName='TOMMVA')
    #print(s.pageLink)
    try:
        para = ParagraphsCorpus(title='test', en_content='test_en', vi_content='test_vi')
        para.sourcescorpus = s
        print('TẠO THÀNH CÔNG ĐỐI TƯỢNG PARAGRAPH')
        pk = para.sourcescorpus.id
        print('IN RA id KHÓA NGOẠI: ', pk)
    except:
        print('KHÔNG TẠO THÀNH CÔNG ĐỐI TƯỢNG PARAGRAPH')  
    num_docs = ParagraphsCorpus.objects.all().count()
    num_sents = SentencesCorpus.objects.all().count()  
    source_data = zip(source_link, page_name)
    context = {'source_data': source_data, 'num_docs': num_docs, 'num_sents': num_sents}
    return render(request, 'index/index.html', context)

def search_page(request):
    return render(request, 'index/search.html')