from django.contrib import admin
from .models import Amenity, CoWorkingSpace, WorkspaceUnit

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_class']

class WorkspaceUnitInline(admin.TabularInline):
    model = WorkspaceUnit
    extra = 1

@admin.register(CoWorkingSpace)
class CoWorkingSpaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'owner', 'created_at']
    search_fields = ['name', 'city', 'address']
    list_filter = ['city', 'amenities']
    inlines = [WorkspaceUnitInline]

@admin.register(WorkspaceUnit)
class WorkspaceUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'space', 'type', 'seating_capacity', 'price_per_day', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'space__name']
