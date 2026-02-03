from django.contrib import admin
from .models import Bill


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'bill_type', 'amount', 'paid_amount', 'payment_status', 'bill_date')
    list_filter = ('payment_status', 'bill_type', 'bill_date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'bill_date')
    fieldsets = (
        ('Patient & Appointment', {
            'fields': ('patient', 'appointment')
        }),
        ('Bill Details', {
            'fields': ('bill_type', 'description', 'amount', 'tax', 'discount')
        }),
        ('Payment', {
            'fields': ('payment_status', 'paid_amount', 'paid_date', 'due_date')
        }),
        ('Notes & Timestamps', {
            'fields': ('notes', 'bill_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

