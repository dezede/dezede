from django.db.models.signals import pre_save
from django.dispatch import receiver

from db_search.models import SearchVectorAbstractModel


@receiver(pre_save)
def update_search_vector(sender, **kwargs):
    if not issubclass(sender, SearchVectorAbstractModel):
        return

    instance = kwargs['instance']
    instance.set_search_vectors()
