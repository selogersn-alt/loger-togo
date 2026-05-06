from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nom")
    slug = models.SlugField(max_length=70, unique=True, blank=True)

    class Meta:
        verbose_name = "Mot-clé"
        verbose_name_plural = "Mots-clés"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Brouillon'),
        ('PUBLISHED', 'Publié'),
    )

    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Auteur")
    featured_image = models.ImageField(upload_to='blog/posts/%Y/%m/', verbose_name="Image à la une", blank=True, null=True)
    content = models.TextField(verbose_name="Contenu (Texte ou HTML)")
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts', verbose_name="Catégorie")
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts', verbose_name="Mots-clés")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT', verbose_name="Statut")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Vues")
    
    is_trending = models.BooleanField(default=False, verbose_name="En tendance")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
