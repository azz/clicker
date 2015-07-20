from django.db.models.signals import post_save
from django.dispatch import receiver

import redis
import json

from api.models import BubbleSortSwap, GameOfLifeCell, Interaction

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# TODO make the client publishing more intelligent

@receiver(post_save, sender=BubbleSortSwap, dispatch_uid="client:BubbleSortSwap#post_save")
def new_bubble_sort_swap(sender, **kwargs):
    instance = kwargs['instance']
    print "Publishing to redis:bubblesort.client"
    r.publish('bubblesort.client', json.dumps({
        'lower_index': instance.lower_index,
        'bubble_sort': instance.bubble_sort_id
    }))

@receiver(post_save, sender=GameOfLifeCell, dispatch_uid="client:GameOfLifeCell#post_save")
def save_game_of_life_cell(sender, instance, **kwargs):
    if not instance.changed:
        return

    print "Publishing to redis:gameoflife.client"
    r.publish('gameoflife.client', json.dumps({
        'row': instance.row,
        'col': instance.col,
        'alive': instance.alive,
        'game_of_life': instance.game_of_life_id
    }))

@receiver(post_save, sender=Interaction, dispatch_uid="client:Interaction#post_save")
def save_interaction(sender, instance, created, **kwargs):
    # the first save is ignored
    if created:
        return

    if instance.gameoflife:
        data = json.loads(instance.data_json)
        if 'assignments' not in data:
            return

        print "Publishing to redis:gameoflife.client"
        r.publish('gameoflife.client', instance.data_json)
