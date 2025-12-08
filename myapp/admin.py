from django.contrib import admin
from .models import Category, Application, Review, Feedback

# 1. Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


# 2. Application
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'is_fraud', 'added_on')
    list_filter = ('category', 'is_fraud', 'added_on')
    search_fields = ('name', 'description', 'fraud_reason')
    readonly_fields = ('added_on',)
    ordering = ('-added_on',)


# 3. Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'application', 'user', 'rating', 'sentiment', 'sentiment_score', 'is_fake', 'created_at')
    list_filter = ('rating', 'sentiment', 'is_fake', 'created_at')
    search_fields = ('text', 'application__name', 'user__username', 'admin_note')
    readonly_fields = ('sentiment', 'sentiment_score', 'created_at')
    ordering = ('-created_at',)


# 4. Feedback
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
