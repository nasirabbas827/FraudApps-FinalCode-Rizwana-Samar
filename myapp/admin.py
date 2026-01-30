from django.contrib import admin
from .models import Category, Application, Review, Feedback


# ==========================
# 1. Category Admin
# ==========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


# ==========================
# 2. Application Admin
# ==========================
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'is_fraud', 'added_on')
    list_filter = ('category', 'is_fraud', 'added_on')
    search_fields = ('name', 'description', 'fraud_reason')
    readonly_fields = ('added_on',)
    ordering = ('-added_on',)


# ==========================
# 3. Review Admin
# ==========================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'application',
        'user',
        'rating',
        'sentiment',
        'sentiment_score',
        'ip_address',
        'is_fake',
        'created_at'
    )

    list_filter = (
        'rating',
        'sentiment',
        'is_fake',
        'created_at',
        'ip_address'
    )

    search_fields = (
        'text',
        'application__name',
        'user__username',
        'ip_address',
        'admin_note'
    )

    readonly_fields = (
        'sentiment',
        'sentiment_score',
        'created_at',
        'ip_address'
    )

    ordering = ('-created_at',)

    actions = ['mark_as_fake', 'mark_as_genuine']

    def mark_as_fake(self, request, queryset):
        queryset.update(
            is_fake=True,
            admin_note='Marked fake by admin'
        )
    mark_as_fake.short_description = "Mark selected reviews as fake"

    def mark_as_genuine(self, request, queryset):
        queryset.update(
            is_fake=False,
            admin_note=None
        )
    mark_as_genuine.short_description = "Mark selected reviews as genuine"


# ==========================
# 4. Feedback Admin
# ==========================
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
