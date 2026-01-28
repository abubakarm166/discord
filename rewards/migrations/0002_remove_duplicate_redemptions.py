# Generated manually to remove duplicate redemptions

from django.db import migrations


def remove_duplicates(apps, schema_editor):
    """Remove duplicate redemptions, keeping only the first one for each user-reward pair"""
    RedemptionLog = apps.get_model('rewards', 'RedemptionLog')
    
    # Get all redemptions grouped by user and reward
    seen = set()
    duplicates = []
    
    for redemption in RedemptionLog.objects.all().order_by('timestamp'):
        key = (redemption.user_id, redemption.reward_id)
        if key in seen:
            duplicates.append(redemption.id)
        else:
            seen.add(key)
    
    # Delete duplicates
    if duplicates:
        RedemptionLog.objects.filter(id__in=duplicates).delete()


def reverse_remove_duplicates(apps, schema_editor):
    """Reverse migration - nothing to do"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('rewards', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_duplicates, reverse_remove_duplicates),
    ]
