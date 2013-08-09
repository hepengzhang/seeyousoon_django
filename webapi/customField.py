from django.db import models
from django.utils.translation import ugettext_lazy as _

class PositiveBigIntegerField(models.BigIntegerField):
    empty_strings_allowed = False
    description = _("Big (8 byte) positive integer")
    def db_type(self, connection):
        """
        Returns MySQL-specific column data type. Make additional checks
        to support other backends.
        """
        return 'bigint UNSIGNED'

    def formfield(self, **kwargs):
        defaults = {'min_value': 0,
                    'max_value': models.BigIntegerField.MAX_BIGINT * 2 - 1}
        defaults.update(kwargs)
        return super(PositiveBigIntegerField, self).formfield(**defaults)

class PositiveBigAutoField(models.AutoField):
    def db_type(self, connection):
        if 'mysql' in connection.__class__.__module__:
            return 'bigint UNSIGNED AUTO_INCREMENT'
        return super(PositiveBigAutoField, self).db_type(connection)
    
class BigForeignKey(models.ForeignKey):    
    def db_type(self, connection):
        rel_field = self.rel.get_related_field()
        # next lines are the "bad tooth" in the original code:
        if (isinstance(rel_field, PositiveBigAutoField) or
                (not connection.features.related_fields_match_type and
                isinstance(rel_field, PositiveBigIntegerField))):
            # because it continues here in the django code:
            # return IntegerField().db_type()
            # thereby fixing any AutoField as IntegerField
            return PositiveBigIntegerField().db_type(connection)
        return rel_field.db_type(connection)