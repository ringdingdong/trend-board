from django.contrib import admin
from .models import Question, Document

class DocumentInline(admin.StackedInline):
    model = Document

class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['subject']
    inlines = [DocumentInline]


admin.site.register(Question, QuestionAdmin)
