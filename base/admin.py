from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.contrib.gis.geos import Point
from geopy.geocoders import Nominatim
from django.db.models import Count
from django.utils.html import format_html

from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.contrib import messages







@admin.register(Organization)
class OrganizationAdmin(GISModelAdmin):
    list_display = ('name', 'location_status', 'geofence_radius', 'get_intern_count')
    list_editable = ('geofence_radius',)
    actions = ['geocode_selected']
    fieldsets = (
        (None, {
            'fields': ('name', 'address')
        }),
        ('Location Settings', {
            'fields': ('location', 'geofence_radius', 'location_source'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('location_source',)

    def location_status(self, obj):
        if obj.location:
            return format_html(
                '<a href="https://maps.google.com/?q={},{}" target="_blank">📍 View Map</a>',
                obj.location.y, obj.location.x
            )
        return "❌ Not located" if obj.address else "—"
    location_status.short_description = "Location"

    def get_intern_count(self, obj):
        return obj.internprofile_set.count()
    get_intern_count.short_description = "Interns"

    def geocode_selected(self, request, queryset):
        for org in queryset:
            if org.address and not org.location:
                if org.geocode_from_address():
                    org.save()
                    self.message_user(
                        request, 
                        f"Successfully geocoded {org.name}", 
                        messages.SUCCESS
                    )
                else:
                    self.message_user(
                        request,
                        f"Failed to geocode {org.name}",
                        messages.ERROR
                    )
    geocode_selected.short_description = "Geocode selected organizations"

    def save_model(self, request, obj, form, change):
        if not obj.location and obj.address:
            obj.location_source = 'geocode'
        super().save_model(request, obj, form, change)




# Location Log Admin
@admin.register(LocationLog)
class LocationLogAdmin(GISModelAdmin):
    list_display = ('intern', 'timestamp', 'status', 'address_short', 'accuracy')
    search_fields = ('intern__user__username', 'address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

    def status(self, obj):
        color = 'green' if obj.is_inside_geofence else 'red'
        text = 'Inside' if obj.is_inside_geofence else 'Outside'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, text
        )
    status.short_description = "Geofence Status"

    def address_short(self, obj):
        return obj.address[:50] + '...' if obj.address else ''
    address_short.short_description = "Address"

    def save_model(self, request, obj, form, change):
        # Auto-set organization location if not set
        if not obj.intern.organization.location:
            obj.intern.organization.location = obj.point
            obj.intern.organization.location_source = 'first_checkin'
            obj.intern.organization.save()
        super().save_model(request, obj, form, change)


from django.contrib import admin
from django.utils.html import format_html

# ====================== CORE MODELS ======================



@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'website')
    search_fields = ('name', 'location')
    list_filter = ('location',)
    ordering = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'current_headcount', 'budget', 'active')
    list_filter = ('active', 'established_date')
    search_fields = ('name', 'code')
    readonly_fields = ('current_headcount', 'budget_utilization', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),

        ('Operations', {
            'fields': ('location', 'floor', 'budget', 'headcount', 'active')
        }),
        ('Contact', {
            'fields': ('phone_extension', 'internal_email'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('mission_statement', 'established_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def current_headcount(self, obj):
        return obj.current_headcount
    current_headcount.short_description = 'Employees'



@admin.register(Intern)
class InternAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'university',
        'department',
        'internship_status',
        'days_remaining',
        'mentor',
        'display_image'
        
    )
    list_filter = (
        'status',
        'department',
        'university',
        'internship_start_date'
    )
    search_fields = (
        'first_name',
        'last_name',
        'personal_email',
        'university__name'
    )
    readonly_fields = (
        'age',
        'internship_duration',
        'days_remaining',
        'created_at',
        'updated_at'
    )
    fieldsets = (
        ('Personal Information', {
            'fields': (
                ('first_name', 'last_name'),
                'date_of_birth',
                'gender',
                'image'
            )
        }),
        ('Contact Information', {
            'fields': (
                'personal_email',
                'phone_number',
                'address',
                ('emergency_contact_name', 'emergency_contact_phone')
            )
        }),
        ('Academic Information', {
            'fields': (
                'university',
                'degree_program',
                'current_year',
                'expected_graduation',
                'transcript'
            )
        }),
        ('Internship Details', {
            'fields': (
                'department',
                ('internship_start_date', 'internship_end_date'),
                'mentor',
                'status',
                'resume'
            )
        }),
        ('HR Administration', {
            'fields': (
                ('stipend_amount', 'bank_account_number'),
                'bank_name'
            ),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def internship_status(self, obj):
        return obj.get_status_display()
    internship_status.short_description = 'Status'

    def display_image(self, obj):
        if obj.image:  
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit:cover;" />', obj.image.url)
        return "No Image"



    display_image.short_description = 'Image' 

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_id', 'get_department', 'position', 'hire_date', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id', 'department__name', 'position')
    list_filter = ('department', 'position', 'is_active', 'employee_id')
    date_hierarchy = 'hire_date'
    exclude = ('user',) 

    
    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else '-'
    get_name.short_description = 'Name'
    
    def get_department(self, obj):
        return obj.department.name if obj.department else '-'
    get_department.short_description = 'Department'

# ====================== ATTENDANCE & LEAVE ======================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'date')
    list_filter = ('status', 'date')
    
    def get_employee_name(self, obj):
        return f"{obj.employee.user.first_name} {obj.employee.user.last_name}" if obj.employee.user else '-'
    get_employee_name.short_description = 'Employee'

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('get_employee_name', 'start_date', 'end_date', 'status', 'duration')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'reason')
    list_filter = ('status', 'start_date')
    
    def get_employee_name(self, obj):
        return f"{obj.employee.user.first_name} {obj.employee.user.last_name}" if obj.employee.user else '-'
    get_employee_name.short_description = 'Employee'
    
    def duration(self, obj):
        return (obj.end_date - obj.start_date).days + 1
    duration.short_description = 'Days'

# ====================== PAYROLL & BENEFITS ======================
@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('get_employee_name', 'month', 'basic_salary', 'bonuses', 'deductions', 'net_salary')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'month')
    list_filter = ('month',)
    
    def get_employee_name(self, obj):
        return f"{obj.employee.user.first_name} {obj.employee.user.last_name}" if obj.employee.user else '-'
    get_employee_name.short_description = 'Employee'

@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short')
    search_fields = ('name', 'description')
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

@admin.register(EmployeeBenefit)
class EmployeeBenefitAdmin(admin.ModelAdmin):
    list_display = ('employee', 'benefit', 'enrollment_date')
    list_filter = ('benefit', 'enrollment_date')

# ====================== PERFORMANCE ======================
@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ('get_employee_name', 'get_reviewer_name', 'date', 'rating', 'summary')
    search_fields = ('employee__user__first_name', 'reviewer__first_name', 'comments')
    list_filter = ('rating', 'date')
    
    def get_employee_name(self, obj):
        return f"{obj.employee.user.first_name} {obj.employee.user.last_name}" if obj.employee.user else '-'
    get_employee_name.short_description = 'Employee'
    
    def get_reviewer_name(self, obj):
        return f"{obj.reviewer.first_name} {obj.reviewer.last_name}" if obj.reviewer else '-'
    get_reviewer_name.short_description = 'Reviewer'
    
    def summary(self, obj):
        return obj.comments[:100] + '...' if len(obj.comments) > 100 else obj.comments
    summary.short_description = 'Summary'

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_count')
    search_fields = ('name',)
    
    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = 'Employees'

@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ('employee', 'skill', 'proficiency')
    list_filter = ('skill', 'proficiency')

# ====================== RECRUITMENT ======================
@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_department', 'posted_date', 'is_active')
    search_fields = ('title', 'department__name', 'description')
    list_filter = ('department', 'is_active')
    
    def get_department(self, obj):
        return obj.department.name if obj.department else '-'
    get_department.short_description = 'Department'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant_name', 'get_job_title', 'status', 'created_at')
    search_fields = ('applicant_name', 'job__title', 'status')
    list_filter = ('status', 'job__department')
    readonly_fields = ('created_at',)  # Add this if you have auto_now_add in your model
    
    def get_job_title(self, obj):
        return obj.job.title if obj.job else '-'
    get_job_title.short_description = 'Job Title'

# ====================== NOTIFICATIONS & COMPANY ======================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'message_short', 'is_read', 'created_at')
    search_fields = ('user__first_name', 'message')
    list_filter = ('is_read',)
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else '-'
    get_user_name.short_description = 'User'
    
    def message_short(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_short.short_description = 'Message'

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone', 'logo_preview')
    readonly_fields = ('logo_preview',)
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="100" style="border-radius: 5px;" />', obj.logo.url)
        return "No logo uploaded"
    logo_preview.short_description = 'Logo Preview'

