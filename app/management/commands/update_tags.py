from django.core.management import BaseCommand
from app.models import Tag
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Update tags'

    def handle(self, *args, **options):
        tags = Tag.objects.get_popular()
        colors = ['black', '#cd1714', 'black', '#cd1714', '#54b250', 'black', 'black', '#ff9f23', 'black', 'black']
        tags_with_colors = list(zip(tags, colors))
        cache.set('popular_tags', tags_with_colors, timeout=61)