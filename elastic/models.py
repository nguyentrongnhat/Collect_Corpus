from django.db import models
import json
# Create your models here.
class SourcesCorpus(models.Model):
    pageName = models.TextField()
    pageLink = models.URLField()
    pageQuery = models.TextField()
    xpathGetDocLinks = models.TextField()
    xpathGetTitle = models.TextField()
    xpathGetEnContent = models.TextField()
    xpathGetViContent = models.TextField()
    breakWord = models.TextField(blank=True)
    continueWord = models.TextField(blank=True)



class ParagraphsCorpus(models.Model):
    sourcescorpus = models.ForeignKey(SourcesCorpus, on_delete=models.CASCADE)
    title = models.TextField()
    en_content = models.TextField()
    vi_content = models.TextField()
    link_document = models.URLField(blank=True)

    def set_link_document(self, x):
        self.link_document = x

    def set_title(self, x):
        self.title = x

    def set_en(self, x):
        self.en_content = json.dumps(x, ensure_ascii=False)

    def get_en(self):
        return json.loads(self.en_content)

    def set_vi(self, x):
        self.vi_content = json.dumps(x, ensure_ascii=False)

    def get_vi(self):
        return json.loads(self.vi_content)


class SentencesCorpus(models.Model):
    paragraphscorpus = models.ForeignKey(ParagraphsCorpus, on_delete=models.CASCADE)
    en_sentence = models.TextField()
    vi_sentence = models.TextField()
    st_order = models.IntegerField()
    
    def set_data_en(self, x):
        self.en_sentence = json.dumps(x, ensure_ascii=False)

    def get_data_en(self):
        return json.loads(self.en_sentence)

    def set_data_vi(self, x):
        self.vi_sentence = json.dumps(x, ensure_ascii=False)

    def get_data_vi(self):
        return json.loads(self.vi_sentence)