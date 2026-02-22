from django.db import models
from django.conf import settings


class Credit(models.Model):
    """Credit/collab entry for about page. Image stored locally in static."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="credit",
    )
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True, blank=True, null=True)  # For URL when no user
    about = models.TextField(blank=True)
    role = models.CharField(max_length=64, blank=True)
    image = models.ImageField(upload_to="credits/%Y/%m/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def get_url_identifier(self):
        """Return user_id or slug for URL."""
        if self.user_id:
            return str(self.user_id)
        return self.slug or str(self.pk)
