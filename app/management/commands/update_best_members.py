from django.core.management import BaseCommand
from app.models import Profile
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Update tags'

    def handle(self, *args, **options):
        users = Profile.objects.get_best()
        cache.set('best_members', users, timeout=3800)