from django.db import models


class CommunityManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)