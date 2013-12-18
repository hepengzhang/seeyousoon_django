from rest_framework import mixins
from django.http.request import QueryDict

class scopeUpdateModelMixin(mixins.UpdateModelMixin):
    
    updateScope = []
    
    def update(self, request, *args, **kwargs):
        request._data = dict((k, v) for k, v in request.DATA.iteritems() if k in self.updateScope)
        kwargs['partial'] = True
        return mixins.UpdateModelMixin.update(self, request, *args, **kwargs)
    
class OverrideCreateModelMixin(mixins.CreateModelMixin):
    
    createScope = []
    
    def create(self, request, override, *args, **kwargs):
        request._data = dict((k, v) for k, v in request.DATA.iteritems() if k in self.createScope)
        if type(request.DATA) == QueryDict : request.DATA._mutable = True
        request.DATA.update(override)
        return mixins.CreateModelMixin.create(self, request, *args, **kwargs)