import uuid
from typing import ClassVar

from django.db import models, transaction
from django.db.models.options import Options
from django.utils.timezone import now


class SoftDeleteManager(models.Manager):  # noqa: R0903
    """Manager to retrieve only non-deleted objects."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class BaseModel(models.Model):  # noqa: R0903
    """Base model with Soft Delete support and cascade restoration."""

    _meta: ClassVar[Options]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()  # Only shows active objects
    all_objects = models.Manager()  # Shows all objects, including deleted ones

    @property
    def is_deleted(self):
        """Determines if the instance is considered deleted."""
        return self.deleted_at is not None

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):  # noqa: A003
        """Marks the object as deleted and handles relationships accordingly."""
        if self.is_deleted:
            return

        self.deleted_at = now()
        self.save()

        self.handle_foreign_keys()
        self.handle_many_to_many()
        self.handle_cascade_delete()

    def restore(self):
        """Restores the deleted object and cascades restoration."""
        if not self.is_deleted:
            return  # Avoid redundant restorations

        self.deleted_at = None
        self.save()

        self.handle_cascade_restore()

    def handle_foreign_keys(self):
        """Manages ForeignKey and OneToOneField based on their on_delete behavior."""
        for field in self._meta.fields:
            if isinstance(field, (models.OneToOneField, models.ForeignKey)):
                related_object = getattr(self, field.name, None)
                if related_object and hasattr(field, "remote_field"):
                    if not hasattr(field.remote_field, "on_delete"):
                        if field.null:
                            setattr(self, field.name, None)
                        continue

                    on_delete = field.remote_field.on_delete

                    if on_delete is models.SET_NULL and field.null:
                        setattr(self, field.name, None)
                    elif on_delete is models.CASCADE:
                        related_object.delete()
        self.save()

    def handle_many_to_many(self):
        """Removes ManyToMany relationships without deleting related objects."""
        for field in self._meta.many_to_many:
            getattr(self, field.name).clear()

    def handle_cascade_delete(self):
        """Finds dependent objects and deletes them in cascade."""
        for relation in self._meta.related_objects:
            if not hasattr(relation, "on_delete"):
                if relation.field.null:
                    related_name = relation.related_name or relation.name + "_set"
                    related_objects = getattr(self, related_name).all()
                    for obj in related_objects:
                        setattr(obj, relation.field.name, None)
                        obj.save()
                continue

            if relation.on_delete is models.CASCADE:
                related_name = relation.related_name or relation.name + "_set"
                related_objects = getattr(self, related_name).all()
                for obj in related_objects:
                    obj.delete()

    def handle_cascade_restore(self):
        """Restores in cascade the objects that depend on this one."""
        for relation in self._meta.related_objects:
            if not hasattr(relation, "on_delete"):
                continue

            if relation.on_delete is models.CASCADE:
                related_model = relation.related_model
                related_objects = related_model.all_objects.filter(
                    **{relation.field.name: self}, deleted_at__isnull=False
                ).iterator()
                for obj in related_objects:
                    obj.restore()

    class Meta:  # noqa: R0903
        abstract = True
