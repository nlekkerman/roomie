from django.contrib import admin
from .models import DamageRepairReport, RepairImage

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

admin.site.register(DamageRepairReport, DamageRepairReportAdmin)

