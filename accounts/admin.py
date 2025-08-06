from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from .models import User, ClientProfile, Address, UserSession, EmailVerification, PasswordReset


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'user_type', 'client_type')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number', 
                 'user_type', 'client_type', 'is_active', 'is_staff', 'is_verified')

    def clean_password(self):
        return self.initial["password"]


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('address_type', 'street_address', 'suburb', 'state', 'postcode', 'is_primary')
    readonly_fields = ('created_at', 'updated_at')


class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    can_delete = False
    verbose_name_plural = 'Client Profile'
    fields = (
        ('ndis_number', 'plan_manager'),
        ('support_coordinator', 'accessibility_needs'),
        ('emergency_contact_name', 'emergency_contact_phone'),
        'preferred_communication',
        'special_instructions'
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    
    list_display = ('email', 'full_name', 'user_type', 'client_type', 'is_verified', 
                   'is_active', 'date_joined', 'last_login_display')
    list_filter = ('user_type', 'client_type', 'is_active', 'is_verified', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('User Classification', {'fields': ('user_type', 'client_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Groups & Permissions', {'fields': ('groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'user_type', 'client_type', 
                      'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    inlines = [ClientProfileInline, AddressInline]
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'
    
    def last_login_display(self, obj):
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M')
        return 'Never'
    last_login_display.short_description = 'Last Login'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client_profile')
    
    def get_inlines(self, request, obj):
        if obj and obj.is_client:
            return [ClientProfileInline, AddressInline]
        return [AddressInline]


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_full_name', 'ndis_number', 'accessibility_needs', 
                   'preferred_communication', 'created_at')
    list_filter = ('accessibility_needs', 'preferred_communication', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'ndis_number')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('NDIS Information', {
            'fields': ('ndis_number', 'plan_manager', 'support_coordinator')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Accessibility & Preferences', {
            'fields': ('accessibility_needs', 'preferred_communication', 'special_instructions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def user_full_name(self, obj):
        return obj.user.full_name
    user_full_name.short_description = 'Full Name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'address_type', 'suburb', 'state', 'postcode', 'is_primary')
    list_filter = ('address_type', 'state', 'is_primary', 'created_at')
    search_fields = ('user__email', 'street_address', 'suburb', 'postcode')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Address Details', {
            'fields': ('address_type', 'street_address', 'suburb', 'state', 'postcode', 'country')
        }),
        ('Settings', {
            'fields': ('is_primary', 'access_instructions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'session_key_short', 'ip_address', 'is_active', 
                   'created_at', 'last_activity')
    list_filter = ('is_active', 'created_at', 'last_activity')
    search_fields = ('user__email', 'session_key', 'ip_address')
    readonly_fields = ('session_key', 'created_at', 'last_activity')
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'session_key', 'ip_address', 'is_active')
        }),
        ('Browser Information', {
            'fields': ('user_agent',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_activity')
        })
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def session_key_short(self, obj):
        return f"{obj.session_key[:8]}..."
    session_key_short.short_description = 'Session Key'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'token_short', 'created_at', 'expires_at', 'is_used', 'status')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at', 'expires_at')
    
    fieldsets = (
        ('Verification Information', {
            'fields': ('user', 'token', 'is_used')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at')
        })
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def token_short(self, obj):
        return f"{obj.token[:12]}..."
    token_short.short_description = 'Token'
    
    def status(self, obj):
        if obj.is_used:
            return format_html('<span style="color: green;">Used</span>')
        elif obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        else:
            return format_html('<span style="color: orange;">Pending</span>')
    status.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'token_short', 'ip_address', 'created_at', 'expires_at', 
                   'is_used', 'status')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'token', 'ip_address')
    readonly_fields = ('token', 'created_at', 'expires_at')
    
    fieldsets = (
        ('Reset Information', {
            'fields': ('user', 'token', 'ip_address', 'is_used')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at')
        })
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def token_short(self, obj):
        return f"{obj.token[:12]}..."
    token_short.short_description = 'Token'
    
    def status(self, obj):
        if obj.is_used:
            return format_html('<span style="color: green;">Used</span>')
        elif obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        else:
            return format_html('<span style="color: orange;">Active</span>')
    status.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


admin.site.site_header = 'Cleaning Service Administration'
admin.site.site_title = 'Cleaning Service Admin'
admin.site.index_title = 'Welcome to Cleaning Service Administration'
