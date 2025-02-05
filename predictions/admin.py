from django.contrib import admin
from .models import Prediction

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'prediction_type', 'created_at')
    search_fields = ('user__username', 'prediction_type')
