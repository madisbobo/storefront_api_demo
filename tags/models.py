from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# Customer manager class
class TaggedItemManager(models.Manager):
    def get_tags_for(self, object_type, object_id):
        # First find the content_type_id for Product from db django_content_type
        content_type = ContentType.objects.get_for_model(object_type)
        # Secondly, get the tags and filter by content_type (e.g. Product) and object_id (e.g. a product with an id of 1)
        return TaggedItem.objects \
            .select_related('tag') \
            .filter(
                content_type=content_type, 
                object_id=object_id)


# Create your models here.
class Tag(models.Model):
    label = models.CharField(max_length=255)

class TaggedItem(models.Model):
    # Add attribute of an instance of a TaggedManagerItemManager
    objects = TaggedItemManager()

    # What tag applied to what object
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    # Type of an object (product, video, article)
    # The ID of an object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

