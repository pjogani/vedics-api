from django.db import migrations

def create_nominatim_service(apps, schema_editor):
    Service = apps.get_model('conduit', 'Service')
    Endpoint = apps.get_model('conduit', 'Endpoint')

    # Create Nominatim Service
    nominatim_service = Service.objects.create(
        name='nominatim',
        base_url='https://nominatim.openstreetmap.org',
    )

    # Create Search Endpoint
    Endpoint.objects.create(
        service=nominatim_service,
        name='search',
        path='/search.php',
        method='GET',
        description='Geocode addresses to coordinates'
    )

def reverse_nominatim_service(apps, schema_editor):
    Service = apps.get_model('conduit', 'Service')
    Service.objects.filter(name='nominatim').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('conduit', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_nominatim_service, reverse_nominatim_service),
    ]