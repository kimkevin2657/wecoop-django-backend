from django.db import models


class BaseManagerMixin:
    def get_queryset(self):
        super(BaseManagerMixin, self).get_queryset().filter(is_deleted=False)


class BaseManager(models.Manager, BaseManagerMixin):
    pass


class BaseModelMixin:
    objects = BaseManager()
    is_deleted = models.BooleanField(verbose_name='삭제여부', default=False)
    created = models.DateTimeField(verbose_name='생성일시', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='수정일시', auto_now=True)
    deleted = models.DateTimeField(verbose_name='삭제일시', null=True, blank=True)

    class Meta:
        abstract = True


class BaseModel(models.Model):
    objects = BaseManager()
    is_deleted = models.BooleanField(verbose_name='삭제여부', default=False)
    created = models.DateTimeField(verbose_name='생성일시', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='수정일시', auto_now=True)
    deleted = models.DateTimeField(verbose_name='삭제일시', null=True, blank=True)

    class Meta:
        abstract = True
