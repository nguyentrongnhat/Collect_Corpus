from django.contrib import admin

# Register your models here.
from .models import *

class SourcesCorpusAdmin(admin.ModelAdmin):
    list_display = ('pageName','pageLink','pageQuery','xpathGetDocLinks','xpathGetTitle','xpathGetEnContent','xpathGetViContent','breakWord', 'continueWord')


class ParagraphsCorpusAdmin(admin.ModelAdmin):
    list_display = ('title', 'en_content', 'vi_content')


class SentencesCorpusAdmin(admin.ModelAdmin):
    list_display = ('st_order','en_sentence','vi_sentence')

admin.site.register(SourcesCorpus, SourcesCorpusAdmin)
admin.site.register(ParagraphsCorpus, ParagraphsCorpusAdmin)
admin.site.register(SentencesCorpus, SentencesCorpusAdmin)