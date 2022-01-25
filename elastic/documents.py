from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import *#Doclist

@registry.register_document
class SourceCorpusDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = 'sources_corpus'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = SourcesCorpus # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'pageName',
            'pageLink',
            'pageQuery',
            'breakWord',
            'continueWord',
            'xpathGetDocLinks',
            'xpathGetTitle',
            'xpathGetEnContent',
            'xpathGetViContent',
        ]


@registry.register_document
class ParagraphsDocument(Document):
    sourcescorpus = fields.ObjectField(properties={
        'pageName' : fields.TextField(),
        'pageLink' : fields.TextField(),
        'xpathGetDocLinks' : fields.TextField(),
        'xpathGetTitle' : fields.TextField(),
        'xpathGetEnContent' : fields.TextField(),
        'xpathGetViContent' : fields.TextField(),
    })

    class Index:
        # Name of the Elasticsearch index
        name = 'paragraphs_corpus'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = ParagraphsCorpus # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'link_document',
            'title',
            'en_content',
            'vi_content',
        ]
        related_models = [SourcesCorpus]  # Optional: to ensure the Car will be re-saved when Manufacturer or Ad is updated

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, SourcesCorpus):
            return related_instance.paragraphscorpus_set.all()

@registry.register_document
class SentencesDocument(Document):
    paragraphscorpus = fields.ObjectField(properties={
        'title' : fields.TextField(),
        #'en_content' : fields.TextField(),
        #'vi_content' : fields.TextField(),
    })

    class Index:
        # Name of the Elasticsearch index
        name = 'sentences_corpus'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = SentencesCorpus # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'en_sentence',
            'vi_sentence',
            'st_order',
        ]
        related_models = [ParagraphsCorpus]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, ParagraphsCorpus):
            return related_instance.sentencescorpus_set.all()