# Generated by Django 4.1.4 on 2023-01-13 12:20

from itertools import islice
from django.db import migrations

def create_subscriptions(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Submission = apps.get_model('courses', 'Submission')
    Subscription = apps.get_model('courses', 'Subscription')

    users_with_subscriptions = Subscription.objects.all().values_list(
        'user__pk', flat=True)
    users_wo_subscriptions = User.objects.exclude(
        id__in=users_with_subscriptions).all()
    users_wo_subscriptions_ids = users_wo_subscriptions.values_list('pk', flat=True)

    submissions = Submission.objects.filter(
        user__pk__in=users_wo_subscriptions_ids).distinct('user', 'exercise__lesson__unit__track')
    
    new_subs = []
    for subm in submissions:
        user = subm.user
        track = subm.exercise.lesson.unit.track
        subs = Subscription(user=user, track=track)
        new_subs.append(subs)

    Subscription.objects.bulk_create(new_subs)


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0015_alter_subscription_unique_together'),
    ]

    operations = [
        migrations.RunPython(create_subscriptions),
    ]