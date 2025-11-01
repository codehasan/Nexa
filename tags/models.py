from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class TagModelManager(models.Manager):
    def get_all_tags(self, model: models.Model, id: int):
        content_type = ContentType.objects.get_for_model(model)
        return TaggedItem.objects.select_related("tag").filter(
            content_type=content_type, object_id=id
        )


class Tag(models.Model):
    label = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.label


class TaggedItem(models.Model):
    objects = TagModelManager()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey()
