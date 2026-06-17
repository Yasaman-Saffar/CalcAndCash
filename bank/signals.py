from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Item


@receiver(post_delete, sender=Item)
def delete_item_image(sender, instance, **kwargs):
    if instance.photo:
        instance.photo.delete(save=False)


@receiver(pre_save, sender=Item)
def delete_old_image(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_image = Item.objects.get(pk=instance.pk).photo
    except Item.DoesNotExist:
        return

    new_image = instance.photo

    if old_image and old_image != new_image:
        old_image.delete(save=False)
