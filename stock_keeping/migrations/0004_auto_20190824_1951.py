# Generated by Django 2.0.6 on 2019-08-24 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stock_keeping', '0003_auto_20190822_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salevoucher',
            name='doc_ledger',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='sale_ledger', to='accounting_entry.LedgerMaster'),
        ),
    ]
