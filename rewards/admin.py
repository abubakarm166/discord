from django.contrib import admin
from .models import User, Category, Reward, RedemptionLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'created_at']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'discord_id', 'key_balance', 'created_at']
    list_filter = ['created_at']
    search_fields = ['username', 'discord_id']
    readonly_fields = ['discord_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Discord Info', {
            'fields': ('discord_id', 'username', 'avatar')
        }),
        ('Keys', {
            'fields': ('key_balance',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'key_cost', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name']
    list_editable = ['is_active']
    list_select_related = ['category']


@admin.register(RedemptionLog)
class RedemptionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'reward', 'timestamp']
    list_filter = ['timestamp', 'reward']
    search_fields = ['user__username', 'reward__name']
    readonly_fields = ['user', 'reward', 'timestamp']
    date_hierarchy = 'timestamp'
