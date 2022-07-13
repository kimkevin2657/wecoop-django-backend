from django.db import models

from app.common.models import BaseModel


class Conference(BaseModel):
    room = models.CharField(verbose_name='방', max_length=16, unique=True, db_index=True)

