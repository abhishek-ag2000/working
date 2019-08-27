# Generated by Django 2.0.6 on 2019-08-27 13:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0004_auto_20190821_1231'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('email', models.EmailField(max_length=254)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, null=True, region=None)),
                ('industry', models.CharField(blank=True, choices=[('ADVERTISING', 'ADVERTISING'), ('AGRICULTURE', 'AGRICULTURE'), ('APPAREL & ACCESSORIES', 'APPAREL & ACCESSORIES'), ('AUTOMOTIVE', 'AUTOMOTIVE'), ('BANKING', 'BANKING'), ('BIOTECHNOLOGY', 'BIOTECHNOLOGY'), ('BUILDING MATERIALS & EQUIPMENT', 'BUILDING MATERIALS & EQUIPMENT'), ('CHEMICAL', 'CHEMICAL'), ('COMPUTER', 'COMPUTER'), ('EDUCATION', 'EDUCATION'), ('ELECTRONICS', 'ELECTRONICS'), ('ENERGY', 'ENERGY'), ('ENTERTAINMENT & LEISURE', 'ENTERTAINMENT & LEISURE'), ('FINANCE', 'FINANCE'), ('FOOD & BEVERAGE', 'FOOD & BEVERAGE'), ('GROCERY', 'GROCERY'), ('HEALTHCARE', 'HEALTHCARE'), ('INSURANCE', 'INSURANCE'), ('LEGAL', 'LEGAL'), ('MANUFACTURING', 'MANUFACTURING'), ('PUBLISHING', 'PUBLISHING'), ('REAL ESTATE', 'REAL ESTATE'), ('SERVICE', 'SERVICE'), ('SOFTWARE', 'SOFTWARE'), ('SPORTS', 'SPORTS'), ('TECHNOLOGY', 'TECHNOLOGY'), ('TELECOMMUNICATIONS', 'TELECOMMUNICATIONS'), ('TELEVISION', 'TELEVISION'), ('TRANSPORTATION', 'TRANSPORTATION'), ('VENTURE CAPITAL', 'VENTURE CAPITAL')], max_length=255, null=True, verbose_name='Industry Type')),
                ('billing_address_line', models.CharField(blank=True, max_length=255, null=True, verbose_name='Address')),
                ('billing_street', models.CharField(blank=True, max_length=55, null=True, verbose_name='Street')),
                ('billing_city', models.CharField(blank=True, max_length=255, null=True, verbose_name='City')),
                ('billing_state', models.CharField(blank=True, max_length=255, null=True, verbose_name='State')),
                ('billing_postcode', models.CharField(blank=True, max_length=64, null=True, verbose_name='Post/Zip-code')),
                ('billing_country', models.CharField(blank=True, choices=[('GB', 'United Kingdom'), ('AF', 'Afghanistan'), ('AX', 'Aland Islands'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AS', 'American Samoa'), ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AQ', 'Antarctica'), ('AG', 'Antigua and Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'), ('AW', 'Aruba'), ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BS', 'Bahamas'), ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'), ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermuda'), ('BT', 'Bhutan'), ('BO', 'Bolivia'), ('BA', 'Bosnia and Herzegovina'), ('BW', 'Botswana'), ('BV', 'Bouvet Island'), ('BR', 'Brazil'), ('IO', 'British Indian Ocean Territory'), ('BN', 'Brunei Darussalam'), ('BG', 'Bulgaria'), ('BF', 'Burkina Faso'), ('BI', 'Burundi'), ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('CV', 'Cape Verde'), ('KY', 'Cayman Islands'), ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'), ('CX', 'Christmas Island'), ('CC', 'Cocos (Keeling) Islands'), ('CO', 'Colombia'), ('KM', 'Comoros'), ('CG', 'Congo'), ('CD', 'Congo, The Democratic Republic of the'), ('CK', 'Cook Islands'), ('CR', 'Costa Rica'), ('CI', "Cote d'Ivoire"), ('HR', 'Croatia'), ('CU', 'Cuba'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'), ('GQ', 'Equatorial Guinea'), ('ER', 'Eritrea'), ('EE', 'Estonia'), ('ET', 'Ethiopia'), ('FK', 'Falkland Islands (Malvinas)'), ('FO', 'Faroe Islands'), ('FJ', 'Fiji'), ('FI', 'Finland'), ('FR', 'France'), ('GF', 'French Guiana'), ('PF', 'French Polynesia'), ('TF', 'French Southern Territories'), ('GA', 'Gabon'), ('GM', 'Gambia'), ('GE', 'Georgia'), ('DE', 'Germany'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GR', 'Greece'), ('GL', 'Greenland'), ('GD', 'Grenada'), ('GP', 'Guadeloupe'), ('GU', 'Guam'), ('GT', 'Guatemala'), ('GG', 'Guernsey'), ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HT', 'Haiti'), ('HM', 'Heard Island and McDonald Islands'), ('VA', 'Holy See (Vatican City State)'), ('HN', 'Honduras'), ('HK', 'Hong Kong'), ('HU', 'Hungary'), ('IS', 'Iceland'), ('IN', 'India'), ('ID', 'Indonesia'), ('IR', 'Iran, Islamic Republic of'), ('IQ', 'Iraq'), ('IE', 'Ireland'), ('IM', 'Isle of Man'), ('IL', 'Israel'), ('IT', 'Italy'), ('JM', 'Jamaica'), ('JP', 'Japan'), ('JE', 'Jersey'), ('JO', 'Jordan'), ('KZ', 'Kazakhstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KP', "Korea, Democratic People's Republic of"), ('KR', 'Korea, Republic of'), ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'), ('LA', "Lao People's Democratic Republic"), ('LV', 'Latvia'), ('LB', 'Lebanon'), ('LS', 'Lesotho'), ('LR', 'Liberia'), ('LY', 'Libyan Arab Jamahiriya'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('MO', 'Macao'), ('MK', 'Macedonia, The Former Yugoslav Republic of'), ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'), ('MV', 'Maldives'), ('ML', 'Mali'), ('MT', 'Malta'), ('MH', 'Marshall Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MU', 'Mauritius'), ('YT', 'Mayotte'), ('MX', 'Mexico'), ('FM', 'Micronesia, Federated States of'), ('MD', 'Moldova'), ('MC', 'Monaco'), ('MN', 'Mongolia'), ('ME', 'Montenegro'), ('MS', 'Montserrat'), ('MA', 'Morocco'), ('MZ', 'Mozambique'), ('MM', 'Myanmar'), ('NA', 'Namibia'), ('NR', 'Nauru'), ('NP', 'Nepal'), ('NL', 'Netherlands'), ('AN', 'Netherlands Antilles'), ('NC', 'New Caledonia'), ('NZ', 'New Zealand'), ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'), ('NU', 'Niue'), ('NF', 'Norfolk Island'), ('MP', 'Northern Mariana Islands'), ('NO', 'Norway'), ('OM', 'Oman'), ('PK', 'Pakistan'), ('PW', 'Palau'), ('PS', 'Palestinian Territory, Occupied'), ('PA', 'Panama'), ('PG', 'Papua New Guinea'), ('PY', 'Paraguay'), ('PE', 'Peru'), ('PH', 'Philippines'), ('PN', 'Pitcairn'), ('PL', 'Poland'), ('PT', 'Portugal'), ('PR', 'Puerto Rico'), ('QA', 'Qatar'), ('RE', 'Reunion'), ('RO', 'Romania'), ('RU', 'Russian Federation'), ('RW', 'Rwanda'), ('BL', 'Saint Barthelemy'), ('SH', 'Saint Helena'), ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'), ('MF', 'Saint Martin'), ('PM', 'Saint Pierre and Miquelon'), ('VC', 'Saint Vincent and the Grenadines'), ('WS', 'Samoa'), ('SM', 'San Marino'), ('ST', 'Sao Tome and Principe'), ('SA', 'Saudi Arabia'), ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'), ('SL', 'Sierra Leone'), ('SG', 'Singapore'), ('SK', 'Slovakia'), ('SI', 'Slovenia'), ('SB', 'Solomon Islands'), ('SO', 'Somalia'), ('ZA', 'South Africa'), ('GS', 'South Georgia and the South Sandwich Islands'), ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('SD', 'Sudan'), ('SR', 'Suriname'), ('SJ', 'Svalbard and Jan Mayen'), ('SZ', 'Swaziland'), ('SE', 'Sweden'), ('CH', 'Switzerland'), ('SY', 'Syrian Arab Republic'), ('TW', 'Taiwan, Province of China'), ('TJ', 'Tajikistan'), ('TZ', 'Tanzania, United Republic of'), ('TH', 'Thailand'), ('TL', 'Timor-Leste'), ('TG', 'Togo'), ('TK', 'Tokelau'), ('TO', 'Tonga'), ('TT', 'Trinidad and Tobago'), ('TN', 'Tunisia'), ('TR', 'Turkey'), ('TM', 'Turkmenistan'), ('TC', 'Turks and Caicos Islands'), ('TV', 'Tuvalu'), ('UG', 'Uganda'), ('UA', 'Ukraine'), ('AE', 'United Arab Emirates'), ('US', 'United States'), ('UM', 'United States Minor Outlying Islands'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VU', 'Vanuatu'), ('VE', 'Venezuela'), ('VN', 'Viet Nam'), ('VG', 'Virgin Islands, British'), ('VI', 'Virgin Islands, U.S.'), ('WF', 'Wallis and Futuna'), ('EH', 'Western Sahara'), ('YE', 'Yemen'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe')], max_length=3, null=True)),
                ('website', models.URLField(blank=True, null=True, verbose_name='Website')),
                ('description', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('is_active', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('open', 'Open'), ('close', 'Close')], default='open', max_length=64)),
                ('contact_name', models.CharField(max_length=120, verbose_name='Contact Name')),
                ('assigned_to', models.ManyToManyField(related_name='account_assigned_users', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_accounts', to='company.Company')),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('status', models.CharField(choices=[('New', 'New'), ('Assigned', 'Assigned'), ('Pending', 'Pending'), ('Closed', 'Closed'), ('Rejected', 'Rejected'), ('Duplicate', 'Duplicate')], max_length=64)),
                ('priority', models.CharField(choices=[('Low', 'Low'), ('Normal', 'Normal'), ('High', 'High'), ('Urgent', 'Urgent')], max_length=64)),
                ('case_type', models.CharField(blank=True, choices=[('Question', 'Question'), ('Incident', 'Incident'), ('Problem', 'Problem')], default='', max_length=255, null=True)),
                ('closed_on', models.DateField()),
                ('description', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('is_active', models.BooleanField(default=False)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CRM.Account')),
                ('assigned_to', models.ManyToManyField(related_name='case_assigned_users', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_cases', to='company.Company')),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255, verbose_name='First name')),
                ('last_name', models.CharField(max_length=255, verbose_name='Last name')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, null=True, region=None, unique=True)),
                ('address', models.CharField(blank=True, max_length=500, null=True, verbose_name='Address')),
                ('description', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('is_active', models.BooleanField(default=False)),
                ('assigned_to', models.ManyToManyField(related_name='contact_assigned_users', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_contacts', to='company.Company')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contact_created_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_subject', models.TextField(null=True)),
                ('message_body', models.TextField(null=True)),
                ('timezone', models.CharField(default='UTC', max_length=100)),
                ('scheduled_date_time', models.DateTimeField(null=True)),
                ('scheduled_later', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('from_email', models.EmailField(max_length=254)),
                ('rendered_message_body', models.TextField(null=True)),
                ('from_account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_email', to='CRM.Account')),
                ('recipients', models.ManyToManyField(related_name='recieved_email', to='CRM.Contact')),
            ],
        ),
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_sent', models.BooleanField(default=False)),
                ('contact', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contact_email_log', to='CRM.Contact')),
                ('email', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='email_log', to='CRM.Email')),
            ],
        ),
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='Title')),
                ('first_name', models.CharField(max_length=255, null=True, verbose_name='First name')),
                ('last_name', models.CharField(max_length=255, null=True, verbose_name='Last name')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('status', models.CharField(blank=True, choices=[('assigned', 'Assigned'), ('in process', 'In Process'), ('converted', 'Converted'), ('recycled', 'Recycled'), ('closed', 'Closed')], max_length=255, null=True, verbose_name='Status of Lead')),
                ('source', models.CharField(blank=True, choices=[('call', 'Call'), ('email', 'Email'), ('existing customer', 'Existing Customer'), ('partner', 'Partner'), ('public relations', 'Public Relations'), ('compaign', 'Campaign'), ('other', 'Other')], max_length=255, null=True, verbose_name='Source of Lead')),
                ('address_line', models.CharField(blank=True, max_length=255, null=True, verbose_name='Address')),
                ('street', models.CharField(blank=True, max_length=55, null=True, verbose_name='Street')),
                ('city', models.CharField(blank=True, max_length=255, null=True, verbose_name='City')),
                ('state', models.CharField(blank=True, max_length=255, null=True, verbose_name='State')),
                ('postcode', models.CharField(blank=True, max_length=64, null=True, verbose_name='Post/Zip-code')),
                ('country', models.CharField(blank=True, choices=[('GB', 'United Kingdom'), ('AF', 'Afghanistan'), ('AX', 'Aland Islands'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AS', 'American Samoa'), ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AQ', 'Antarctica'), ('AG', 'Antigua and Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'), ('AW', 'Aruba'), ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BS', 'Bahamas'), ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'), ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermuda'), ('BT', 'Bhutan'), ('BO', 'Bolivia'), ('BA', 'Bosnia and Herzegovina'), ('BW', 'Botswana'), ('BV', 'Bouvet Island'), ('BR', 'Brazil'), ('IO', 'British Indian Ocean Territory'), ('BN', 'Brunei Darussalam'), ('BG', 'Bulgaria'), ('BF', 'Burkina Faso'), ('BI', 'Burundi'), ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('CV', 'Cape Verde'), ('KY', 'Cayman Islands'), ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'), ('CX', 'Christmas Island'), ('CC', 'Cocos (Keeling) Islands'), ('CO', 'Colombia'), ('KM', 'Comoros'), ('CG', 'Congo'), ('CD', 'Congo, The Democratic Republic of the'), ('CK', 'Cook Islands'), ('CR', 'Costa Rica'), ('CI', "Cote d'Ivoire"), ('HR', 'Croatia'), ('CU', 'Cuba'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'), ('GQ', 'Equatorial Guinea'), ('ER', 'Eritrea'), ('EE', 'Estonia'), ('ET', 'Ethiopia'), ('FK', 'Falkland Islands (Malvinas)'), ('FO', 'Faroe Islands'), ('FJ', 'Fiji'), ('FI', 'Finland'), ('FR', 'France'), ('GF', 'French Guiana'), ('PF', 'French Polynesia'), ('TF', 'French Southern Territories'), ('GA', 'Gabon'), ('GM', 'Gambia'), ('GE', 'Georgia'), ('DE', 'Germany'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GR', 'Greece'), ('GL', 'Greenland'), ('GD', 'Grenada'), ('GP', 'Guadeloupe'), ('GU', 'Guam'), ('GT', 'Guatemala'), ('GG', 'Guernsey'), ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HT', 'Haiti'), ('HM', 'Heard Island and McDonald Islands'), ('VA', 'Holy See (Vatican City State)'), ('HN', 'Honduras'), ('HK', 'Hong Kong'), ('HU', 'Hungary'), ('IS', 'Iceland'), ('IN', 'India'), ('ID', 'Indonesia'), ('IR', 'Iran, Islamic Republic of'), ('IQ', 'Iraq'), ('IE', 'Ireland'), ('IM', 'Isle of Man'), ('IL', 'Israel'), ('IT', 'Italy'), ('JM', 'Jamaica'), ('JP', 'Japan'), ('JE', 'Jersey'), ('JO', 'Jordan'), ('KZ', 'Kazakhstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KP', "Korea, Democratic People's Republic of"), ('KR', 'Korea, Republic of'), ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'), ('LA', "Lao People's Democratic Republic"), ('LV', 'Latvia'), ('LB', 'Lebanon'), ('LS', 'Lesotho'), ('LR', 'Liberia'), ('LY', 'Libyan Arab Jamahiriya'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('MO', 'Macao'), ('MK', 'Macedonia, The Former Yugoslav Republic of'), ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'), ('MV', 'Maldives'), ('ML', 'Mali'), ('MT', 'Malta'), ('MH', 'Marshall Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MU', 'Mauritius'), ('YT', 'Mayotte'), ('MX', 'Mexico'), ('FM', 'Micronesia, Federated States of'), ('MD', 'Moldova'), ('MC', 'Monaco'), ('MN', 'Mongolia'), ('ME', 'Montenegro'), ('MS', 'Montserrat'), ('MA', 'Morocco'), ('MZ', 'Mozambique'), ('MM', 'Myanmar'), ('NA', 'Namibia'), ('NR', 'Nauru'), ('NP', 'Nepal'), ('NL', 'Netherlands'), ('AN', 'Netherlands Antilles'), ('NC', 'New Caledonia'), ('NZ', 'New Zealand'), ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'), ('NU', 'Niue'), ('NF', 'Norfolk Island'), ('MP', 'Northern Mariana Islands'), ('NO', 'Norway'), ('OM', 'Oman'), ('PK', 'Pakistan'), ('PW', 'Palau'), ('PS', 'Palestinian Territory, Occupied'), ('PA', 'Panama'), ('PG', 'Papua New Guinea'), ('PY', 'Paraguay'), ('PE', 'Peru'), ('PH', 'Philippines'), ('PN', 'Pitcairn'), ('PL', 'Poland'), ('PT', 'Portugal'), ('PR', 'Puerto Rico'), ('QA', 'Qatar'), ('RE', 'Reunion'), ('RO', 'Romania'), ('RU', 'Russian Federation'), ('RW', 'Rwanda'), ('BL', 'Saint Barthelemy'), ('SH', 'Saint Helena'), ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'), ('MF', 'Saint Martin'), ('PM', 'Saint Pierre and Miquelon'), ('VC', 'Saint Vincent and the Grenadines'), ('WS', 'Samoa'), ('SM', 'San Marino'), ('ST', 'Sao Tome and Principe'), ('SA', 'Saudi Arabia'), ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'), ('SL', 'Sierra Leone'), ('SG', 'Singapore'), ('SK', 'Slovakia'), ('SI', 'Slovenia'), ('SB', 'Solomon Islands'), ('SO', 'Somalia'), ('ZA', 'South Africa'), ('GS', 'South Georgia and the South Sandwich Islands'), ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('SD', 'Sudan'), ('SR', 'Suriname'), ('SJ', 'Svalbard and Jan Mayen'), ('SZ', 'Swaziland'), ('SE', 'Sweden'), ('CH', 'Switzerland'), ('SY', 'Syrian Arab Republic'), ('TW', 'Taiwan, Province of China'), ('TJ', 'Tajikistan'), ('TZ', 'Tanzania, United Republic of'), ('TH', 'Thailand'), ('TL', 'Timor-Leste'), ('TG', 'Togo'), ('TK', 'Tokelau'), ('TO', 'Tonga'), ('TT', 'Trinidad and Tobago'), ('TN', 'Tunisia'), ('TR', 'Turkey'), ('TM', 'Turkmenistan'), ('TC', 'Turks and Caicos Islands'), ('TV', 'Tuvalu'), ('UG', 'Uganda'), ('UA', 'Ukraine'), ('AE', 'United Arab Emirates'), ('US', 'United States'), ('UM', 'United States Minor Outlying Islands'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VU', 'Vanuatu'), ('VE', 'Venezuela'), ('VN', 'Viet Nam'), ('VG', 'Virgin Islands, British'), ('VI', 'Virgin Islands, U.S.'), ('WF', 'Wallis and Futuna'), ('EH', 'Western Sahara'), ('YE', 'Yemen'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe')], max_length=3, null=True)),
                ('website', models.CharField(blank=True, max_length=255, null=True, verbose_name='Website')),
                ('description', models.TextField(blank=True, null=True)),
                ('account_name', models.CharField(blank=True, max_length=255, null=True)),
                ('opportunity_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Opportunity Amount')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('is_active', models.BooleanField(default=False)),
                ('enquery_type', models.CharField(blank=True, max_length=255, null=True)),
                ('assigned_to', models.ManyToManyField(related_name='lead_assigned_users', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_Leads', to='company.Company')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lead_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('stage', models.CharField(choices=[('QUALIFICATION', 'QUALIFICATION'), ('NEEDS ANALYSIS', 'NEEDS ANALYSIS'), ('VALUE PROPOSITION', 'VALUE PROPOSITION'), ('ID.DECISION MAKERS', 'ID.DECISION MAKERS'), ('PERCEPTION ANALYSIS', 'PERCEPTION ANALYSIS'), ('PROPOSAL/PRICE QUOTE', 'PROPOSAL/PRICE QUOTE'), ('NEGOTIATION/REVIEW', 'NEGOTIATION/REVIEW'), ('CLOSED WON', 'CLOSED WON'), ('CLOSED LOST', 'CLOSED LOST')], max_length=64, verbose_name='Stage')),
                ('currency', models.CharField(blank=True, choices=[('AED', 'AED, Dirham'), ('AFN', 'AFN, Afghani'), ('ALL', 'ALL, Lek'), ('AMD', 'AMD, Dram'), ('ANG', 'ANG, Guilder'), ('AOA', 'AOA, Kwanza'), ('ARS', 'ARS, Peso'), ('AUD', 'AUD, Dollar'), ('AWG', 'AWG, Guilder'), ('AZN', 'AZN, Manat'), ('BAM', 'BAM, Marka'), ('BBD', 'BBD, Dollar'), ('BDT', 'BDT, Taka'), ('BGN', 'BGN, Lev'), ('BHD', 'BHD, Dinar'), ('BIF', 'BIF, Franc'), ('BMD', 'BMD, Dollar'), ('BND', 'BND, Dollar'), ('BOB', 'BOB, Boliviano'), ('BRL', 'BRL, Real'), ('BSD', 'BSD, Dollar'), ('BTN', 'BTN, Ngultrum'), ('BWP', 'BWP, Pula'), ('BYR', 'BYR, Ruble'), ('BZD', 'BZD, Dollar'), ('CAD', 'CAD, Dollar'), ('CDF', 'CDF, Franc'), ('CHF', 'CHF, Franc'), ('CLP', 'CLP, Peso'), ('CNY', 'CNY, Yuan Renminbi'), ('COP', 'COP, Peso'), ('CRC', 'CRC, Colon'), ('CUP', 'CUP, Peso'), ('CVE', 'CVE, Escudo'), ('CZK', 'CZK, Koruna'), ('DJF', 'DJF, Franc'), ('DKK', 'DKK, Krone'), ('DOP', 'DOP, Peso'), ('DZD', 'DZD, Dinar'), ('EGP', 'EGP, Pound'), ('ERN', 'ERN, Nakfa'), ('ETB', 'ETB, Birr'), ('EUR', 'EUR, Euro'), ('FJD', 'FJD, Dollar'), ('FKP', 'FKP, Pound'), ('GBP', 'GBP, Pound'), ('GEL', 'GEL, Lari'), ('GHS', 'GHS, Cedi'), ('GIP', 'GIP, Pound'), ('GMD', 'GMD, Dalasi'), ('GNF', 'GNF, Franc'), ('GTQ', 'GTQ, Quetzal'), ('GYD', 'GYD, Dollar'), ('HKD', 'HKD, Dollar'), ('HNL', 'HNL, Lempira'), ('HRK', 'HRK, Kuna'), ('HTG', 'HTG, Gourde'), ('HUF', 'HUF, Forint'), ('IDR', 'IDR, Rupiah'), ('ILS', 'ILS, Shekel'), ('INR', 'INR, Rupee'), ('IQD', 'IQD, Dinar'), ('IRR', 'IRR, Rial'), ('ISK', 'ISK, Krona'), ('JMD', 'JMD, Dollar'), ('JOD', 'JOD, Dinar'), ('JPY', 'JPY, Yen'), ('KES', 'KES, Shilling'), ('KGS', 'KGS, Som'), ('KHR', 'KHR, Riels'), ('KMF', 'KMF, Franc'), ('KPW', 'KPW, Won'), ('KRW', 'KRW, Won'), ('KWD', 'KWD, Dinar'), ('KYD', 'KYD, Dollar'), ('KZT', 'KZT, Tenge'), ('LAK', 'LAK, Kip'), ('LBP', 'LBP, Pound'), ('LKR', 'LKR, Rupee'), ('LRD', 'LRD, Dollar'), ('LSL', 'LSL, Loti'), ('LTL', 'LTL, Litas'), ('LVL', 'LVL, Lat'), ('LYD', 'LYD, Dinar'), ('MAD', 'MAD, Dirham'), ('MDL', 'MDL, Leu'), ('MGA', 'MGA, Ariary'), ('MKD', 'MKD, Denar'), ('MMK', 'MMK, Kyat'), ('MNT', 'MNT, Tugrik'), ('MOP', 'MOP, Pataca'), ('MRO', 'MRO, Ouguiya'), ('MUR', 'MUR, Rupee'), ('MVR', 'MVR, Rufiyaa'), ('MWK', 'MWK, Kwacha'), ('MXN', 'MXN, Peso'), ('MYR', 'MYR, Ringgit'), ('MZN', 'MZN, Metical'), ('NAD', 'NAD, Dollar'), ('NGN', 'NGN, Naira'), ('NIO', 'NIO, Cordoba'), ('NOK', 'NOK, Krone'), ('NPR', 'NPR, Rupee'), ('NZD', 'NZD, Dollar'), ('OMR', 'OMR, Rial'), ('PAB', 'PAB, Balboa'), ('PEN', 'PEN, Sol'), ('PGK', 'PGK, Kina'), ('PHP', 'PHP, Peso'), ('PKR', 'PKR, Rupee'), ('PLN', 'PLN, Zloty'), ('PYG', 'PYG, Guarani'), ('QAR', 'QAR, Rial'), ('RON', 'RON, Leu'), ('RSD', 'RSD, Dinar'), ('RUB', 'RUB, Ruble'), ('RWF', 'RWF, Franc'), ('SAR', 'SAR, Rial'), ('SBD', 'SBD, Dollar'), ('SCR', 'SCR, Rupee'), ('SDG', 'SDG, Pound'), ('SEK', 'SEK, Krona'), ('SGD', 'SGD, Dollar'), ('SHP', 'SHP, Pound'), ('SLL', 'SLL, Leone'), ('SOS', 'SOS, Shilling'), ('SRD', 'SRD, Dollar'), ('SSP', 'SSP, Pound'), ('STD', 'STD, Dobra'), ('SYP', 'SYP, Pound'), ('SZL', 'SZL, Lilangeni'), ('THB', 'THB, Baht'), ('TJS', 'TJS, Somoni'), ('TMT', 'TMT, Manat'), ('TND', 'TND, Dinar'), ('TOP', 'TOP, Paanga'), ('TRY', 'TRY, Lira'), ('TTD', 'TTD, Dollar'), ('TWD', 'TWD, Dollar'), ('TZS', 'TZS, Shilling'), ('UAH', 'UAH, Hryvnia'), ('UGX', 'UGX, Shilling'), ('USD', '$, Dollar'), ('UYU', 'UYU, Peso'), ('UZS', 'UZS, Som'), ('VEF', 'VEF, Bolivar'), ('VND', 'VND, Dong'), ('VUV', 'VUV, Vatu'), ('WST', 'WST, Tala'), ('XAF', 'XAF, Franc'), ('XCD', 'XCD, Dollar'), ('XOF', 'XOF, Franc'), ('XPF', 'XPF, Franc'), ('YER', 'YER, Rial'), ('ZAR', 'ZAR, Rand'), ('ZMK', 'ZMK, Kwacha'), ('ZWL', 'ZWL, Dollar')], max_length=3, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Opportunity Amount')),
                ('lead_source', models.CharField(blank=True, choices=[('NONE', 'NONE'), ('CALL', 'CALL'), ('EMAIL', ' EMAIL'), ('EXISTING CUSTOMER', 'EXISTING CUSTOMER'), ('PARTNER', 'PARTNER'), ('PUBLIC RELATIONS', 'PUBLIC RELATIONS'), ('CAMPAIGN', 'CAMPAIGN'), ('WEBSITE', 'WEBSITE'), ('OTHER', 'OTHER')], max_length=255, null=True, verbose_name='Source of Lead')),
                ('probability', models.IntegerField(blank=True, default=0, null=True)),
                ('closed_on', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('is_active', models.BooleanField(default=False)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='opportunities', to='CRM.Account')),
                ('assigned_to', models.ManyToManyField(related_name='opportunity_assigned_to', to=settings.AUTH_USER_MODEL)),
                ('closed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_Opportunity', to='company.Company')),
                ('contacts', models.ManyToManyField(to='CRM.Contact')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='opportunity_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('slug', models.CharField(blank=True, max_length=20, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='opportunity',
            name='tags',
            field=models.ManyToManyField(blank=True, to='CRM.Tags'),
        ),
        migrations.AddField(
            model_name='case',
            name='contacts',
            field=models.ManyToManyField(to='CRM.Contact'),
        ),
        migrations.AddField(
            model_name='case',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='case_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='account',
            name='contacts',
            field=models.ManyToManyField(related_name='account_contacts', to='CRM.Contact'),
        ),
        migrations.AddField(
            model_name='account',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='account_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='account',
            name='lead',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='account_leads', to='CRM.Lead'),
        ),
        migrations.AddField(
            model_name='account',
            name='tags',
            field=models.ManyToManyField(blank=True, to='CRM.Tags'),
        ),
    ]
