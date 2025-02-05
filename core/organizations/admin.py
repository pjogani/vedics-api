from django.contrib import admin
from .models import Organization, Team, TeamMembership

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subscription_plan', 'seats', 'is_deleted')
    search_fields = ('name',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'is_deleted')
    search_fields = ('name', 'organization__name')

@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'user', 'role', 'is_deleted')
    search_fields = ('team__name', 'user__username', 'role')
