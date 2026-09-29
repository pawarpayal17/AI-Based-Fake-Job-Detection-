from django.contrib import admin
from .models import JobPost, PredictionResult

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'user__username')

@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ('job', 'prediction', 'confidence', 'created_at')
    list_filter = ('prediction',)
