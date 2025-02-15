from django.contrib import admin
from .models import DamageRepairReport, RepairImage, Notification

class RepairImageInline(admin.TabularInline):
    model = RepairImage  # ✅ Directly use the RepairImage model
    extra = 1  # Show one extra blank field for adding new images

class DamageRepairReportAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'description', 'status', 'reported_at', 'resolved_at')
    list_filter = ('status', 'property', 'tenant')
    search_fields = ('description', 'property__street', 'tenant__username')
    list_editable = ('status',)
    ordering = ('-reported_at',)

    # Register the inline
    inlines = [RepairImageInline]  # ✅ Corrected inline usage

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('receiver', 'sender', 'message_preview', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('receiver__username', 'sender__username', 'message')

    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message

    message_preview.short_description = "Message"


admin.site.register(Notification, NotificationAdmin)

admin.site.register(DamageRepairReport, DamageRepairReportAdmin)

