# Generated manually for MaturityLevel field addition

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grc', '0007_compliance'),
    ]

    operations = [
        migrations.AddField(
            model_name='compliance',
            name='MaturityLevel',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Initial', 'Initial'),
                    ('Developing', 'Developing'),
                    ('Defined', 'Defined'),
                    ('Managed', 'Managed'),
                    ('Optimizing', 'Optimizing')
                ],
                default='Initial',
                max_length=50,
                null=True
            ),
        ),
    ] 