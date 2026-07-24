from django.contrib import admin
from .models import Booking, Inquiry

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'unit', 'start_date', 'end_date', 'total_price', 'status']
    list_filter = ['status', 'start_date']
    search_fields = ['user__username', 'unit__name']

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'space', 'created_at']
    search_fields = ['sender__username', 'space__name', 'message']
