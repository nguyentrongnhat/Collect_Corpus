from rest_framework.filters import BaseFilterBackend

__title__ = 'django_elasticsearch_dsl_drf.highlight'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2017-2018 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('HighlightBackend',)


class HighlightBackend(BaseFilterBackend):

    highlight_param = 'highlight'

    @classmethod
    def prepare_highlight_fields(cls, view):
        
        highlight_fields = view.highlight_fields

        for field, options in highlight_fields.items():
            if 'enabled' not in highlight_fields[field]:
                highlight_fields[field]['enabled'] = False

            if 'options' not in highlight_fields[field]:
                highlight_fields[field]['options'] = {}

        return highlight_fields


    def get_highlight_query_params(self, request):
        
        query_params = request.query_params.copy()
        return query_params.getlist(self.highlight_param, [])


    def filter_queryset(self, request, queryset, view):
        
        highlight_query_params = self.get_highlight_query_params(request)
        highlight_fields = self.prepare_highlight_fields(view)
        for __field, __options in highlight_fields.items():
            if __field in highlight_query_params or __options['enabled']:
                queryset = queryset.highlight(__field, **__options['options'])

        return queryset