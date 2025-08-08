from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import (
    Service,
    ServiceCategory,
    ServiceArea,
    NDISServiceCode,
    ServiceAddOn,
    ServiceAvailability,
    ServicePricing,
)
from .validators import (
    validate_postcode,
    validate_service_duration,
    validate_ndis_service_code,
    validate_pricing,
    validate_service_name,
    validate_service_description,
    validate_hourly_rate,
    validate_room_count,
    validate_square_meters,
)

User = get_user_model()


class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = [
            "name",
            "slug",
            "category_type",
            "description",
            "icon",
            "is_active",
            "is_ndis_eligible",
            "display_order",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter category name"}
            ),
            "slug": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "category-slug"}
            ),
            "category_type": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter category description",
                }
            ),
            "icon": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "fa-icon-name"}
            ),
            "display_order": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_ndis_eligible": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name:
            validate_service_name(name)
        return name

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if description:
            validate_service_description(description)
        return description

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        if slug:
            if (
                ServiceCategory.objects.filter(slug=slug)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise ValidationError("A category with this slug already exists.")
        return slug


class NDISServiceCodeForm(forms.ModelForm):
    class Meta:
        model = NDISServiceCode
        fields = [
            "code",
            "name",
            "description",
            "unit_type",
            "standard_rate",
            "is_active",
            "effective_from",
            "effective_to",
        ]
        widgets = {
            "code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "XX_XXX_XXXX_X_X"}
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter service code name",
                }
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "unit_type": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., Hour, Each, Day"}
            ),
            "standard_rate": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0.01"}
            ),
            "effective_from": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "effective_to": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if code:
            validate_ndis_service_code(code)
            if (
                NDISServiceCode.objects.filter(code=code)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise ValidationError(
                    "An NDIS service code with this code already exists."
                )
        return code

    def clean_standard_rate(self):
        rate = self.cleaned_data.get("standard_rate")
        if rate:
            validate_pricing(rate)
        return rate

    def clean(self):
        cleaned_data = super().clean()
        effective_from = cleaned_data.get("effective_from")
        effective_to = cleaned_data.get("effective_to")

        if effective_from and effective_to:
            if effective_to <= effective_from:
                raise ValidationError("Effective end date must be after start date.")

        return cleaned_data


class ServiceAreaForm(forms.ModelForm):
    class Meta:
        model = ServiceArea
        fields = [
            "suburb",
            "postcode",
            "state",
            "is_active",
            "travel_time_minutes",
            "travel_cost",
            "service_radius_km",
            "priority_level",
        ]
        widgets = {
            "suburb": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter suburb name"}
            ),
            "postcode": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "0000"}
            ),
            "state": forms.Select(attrs={"class": "form-select"}),
            "travel_time_minutes": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "travel_cost": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0.00"}
            ),
            "service_radius_km": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "priority_level": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 5}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_postcode(self):
        postcode = self.cleaned_data.get("postcode")
        if postcode:
            validate_postcode(postcode)
        return postcode

    def clean(self):
        cleaned_data = super().clean()
        suburb = cleaned_data.get("suburb")
        postcode = cleaned_data.get("postcode")
        state = cleaned_data.get("state")

        if suburb and postcode and state:
            existing = ServiceArea.objects.filter(
                suburb=suburb, postcode=postcode, state=state
            ).exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError(
                    "A service area with this combination already exists."
                )

        return cleaned_data


class ServiceForm(forms.ModelForm):
    service_area_ids = forms.ModelMultipleChoiceField(
        queryset=ServiceArea.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        label="Service Areas",
    )

    addon_ids = forms.ModelMultipleChoiceField(
        queryset=ServiceAddOn.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        label="Available Add-ons",
    )

    class Meta:
        model = Service
        fields = [
            "name",
            "slug",
            "category",
            "service_type",
            "description",
            "short_description",
            "pricing_type",
            "base_price",
            "hourly_rate",
            "minimum_charge",
            "estimated_duration",
            "duration_unit",
            "is_active",
            "is_featured",
            "is_ndis_eligible",
            "requires_quote",
            "ndis_service_code",
            "minimum_rooms",
            "maximum_rooms",
            "equipment_required",
            "special_requirements",
            "display_order",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter service name"}
            ),
            "slug": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "service-slug"}
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "service_type": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "short_description": forms.Textarea(
                attrs={"class": "form-control", "rows": 2}
            ),
            "pricing_type": forms.Select(attrs={"class": "form-select"}),
            "base_price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0.01"}
            ),
            "hourly_rate": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0.01"}
            ),
            "minimum_charge": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0.00"}
            ),
            "estimated_duration": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "duration_unit": forms.Select(attrs={"class": "form-select"}),
            "ndis_service_code": forms.Select(attrs={"class": "form-select"}),
            "minimum_rooms": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "maximum_rooms": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "equipment_required": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "special_requirements": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "display_order": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_ndis_eligible": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "requires_quote": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["ndis_service_code"].queryset = NDISServiceCode.objects.filter(
            is_active=True
        ).order_by("code")

        if self.instance.pk:
            self.fields["service_area_ids"].initial = self.instance.service_areas.all()
            self.fields["addon_ids"].initial = self.instance.addons.all()

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name:
            validate_service_name(name)
        return name

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if description:
            validate_service_description(description)
        return description

    def clean_base_price(self):
        price = self.cleaned_data.get("base_price")
        if price:
            validate_pricing(price)
        return price

    def clean_hourly_rate(self):
        rate = self.cleaned_data.get("hourly_rate")
        if rate:
            validate_hourly_rate(rate)
        return rate

    def clean_estimated_duration(self):
        duration = self.cleaned_data.get("estimated_duration")
        if duration:
            validate_service_duration(duration)
        return duration

    def clean_minimum_rooms(self):
        rooms = self.cleaned_data.get("minimum_rooms")
        if rooms:
            validate_room_count(rooms)
        return rooms

    def clean_maximum_rooms(self):
        rooms = self.cleaned_data.get("maximum_rooms")
        if rooms:
            validate_room_count(rooms)
        return rooms
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            if Service.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
                raise ValidationError("A service with this slug already exists.")
        return slug
    
    def clean(self):
        cleaned_data = super().clean()
        pricing_type = cleaned_data.get('pricing_type')
        hourly_rate = cleaned_data.get('hourly_rate')
        minimum_rooms = cleaned_data.get('minimum_rooms')
        maximum_rooms = cleaned_data.get('maximum_rooms')
        is_ndis_eligible = cleaned_data.get('is_ndis_eligible')
        ndis_service_code = cleaned_data.get('ndis_service_code')
        
        if pricing_type == 'hourly' and not hourly_rate:
            raise ValidationError("Hourly rate is required for hourly pricing type.")
        
        if minimum_rooms and maximum_rooms and maximum_rooms < minimum_rooms:
            raise ValidationError("Maximum rooms cannot be less than minimum rooms.")
        
        if is_ndis_eligible and not ndis_service_code:
            raise ValidationError("NDIS service code is required for NDIS eligible services.")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        
        if commit:
            service_areas = self.cleaned_data.get('service_area_ids')
            if service_areas:
                instance.service_areas.set(service_areas)
            
            addons = self.cleaned_data.get('addon_ids')
            if addons:
                instance.addons.set(addons)
        
        return instance


class ServiceAddOnForm(forms.ModelForm):
    class Meta:
        model = ServiceAddOn
        fields = [
            'name', 'addon_type', 'description', 'price',
            'is_active', 'is_optional'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter add-on name'
            }),
            'addon_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_optional': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price:
            validate_pricing(price)
        return price


class ServiceAvailabilityForm(forms.ModelForm):
    class Meta:
        model = ServiceAvailability
        fields = [
            'service', 'day_of_week', 'start_time', 'end_time',
            'is_available', 'max_bookings'
        ]
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-select'
            }),
            'day_of_week': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'max_bookings': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError("End time must be after start time.")
        
        return cleaned_data


class ServicePricingForm(forms.ModelForm):
    class Meta:
        model = ServicePricing
        fields = [
            'service', 'tier', 'price', 'description',
            'is_active', 'effective_from', 'effective_to'
        ]
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter pricing description'
            }),
            'effective_from': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'effective_to': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price:
            validate_pricing(price)
        return price
    
    def clean(self):
        cleaned_data = super().clean()
        effective_from = cleaned_data.get('effective_from')
        effective_to = cleaned_data.get('effective_to')
        
        if effective_from and effective_to:
            if effective_to <= effective_from:
                raise ValidationError("Effective end date must be after start date.")
        
        return cleaned_data


class ServiceQuoteRequestForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Service'
    )
    
    rooms = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 50
        }),
        label='Number of Rooms'
    )
    
    square_meters = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01'
        }),
        label='Square Meters (Optional)'
    )
    
    hours = forms.IntegerField(
        min_value=1,
        max_value=12,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 12
        }),
        label='Hours (For Hourly Services)'
    )
    
    postcode = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0000'
        }),
        label='Postcode'
    )
    
    addons = forms.ModelMultipleChoiceField(
        queryset=ServiceAddOn.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label='Add-ons'
    )
    
    special_requests = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special requirements or requests...'
        }),
        label='Special Requests'
    )
    
    preferred_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Preferred Date'
    )
    
    preferred_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        label='Preferred Time'
    )
    
    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')
        if postcode:
            validate_postcode(postcode)
        return postcode
    
    def clean_square_meters(self):
        square_meters = self.cleaned_data.get('square_meters')
        if square_meters:
            validate_square_meters(square_meters)
        return square_meters
    
    def clean_preferred_date(self):
        preferred_date = self.cleaned_data.get('preferred_date')
        if preferred_date and preferred_date < timezone.now().date():
            raise ValidationError("Preferred date cannot be in the past.")
        return preferred_date
    
    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        postcode = cleaned_data.get('postcode')
        addons = cleaned_data.get('addons')
        
        if service and postcode:
            if not service.is_available_in_area(postcode):
                raise ValidationError("Selected service is not available in the specified area.")
        
        if service and addons:
            invalid_addons = addons.exclude(services=service)
            if invalid_addons.exists():
                raise ValidationError("Some selected add-ons are not available for this service.")
        
        return cleaned_data


class ServiceSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search services...'
        }),
        label='Search'
    )
    
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Category'
    )
    
    service_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Service.SERVICE_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Service Type'
    )
    
    postcode = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0000'
        }),
        label='Postcode'
    )
    
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01'
        }),
        label='Min Price'
    )
    
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01'
        }),
        label='Max Price'
    )
    
    is_ndis_eligible = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='NDIS Eligible Only'
    )
    
    requires_quote = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Requires Quote'
    )
    
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Featured Services Only'
    )
    
    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')
        if postcode:
            validate_postcode(postcode)
        return postcode
    
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise ValidationError("Minimum price cannot be greater than maximum price.")
        
        return cleaned_data


class BulkServiceActionForm(forms.Form):
    ACTION_CHOICES = [
        ('activate', 'Activate'),
        ('deactivate', 'Deactivate'),
        ('feature', 'Feature'),
        ('unfeature', 'Remove from Featured'),
        ('delete', 'Delete'),
    ]
    
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Select Services'
    )
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Action'
    )
    
    def clean_services(self):
        services = self.cleaned_data.get('services')
        if not services:
            raise ValidationError("Please select at least one service.")
        if len(services) > 100:
            raise ValidationError("Cannot perform bulk action on more than 100 services at once.")
        return services


class ServiceFilterForm(forms.Form):
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Active Only'
    )
    
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Featured Only'
    )
    
    is_ndis_eligible = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='NDIS Eligible Only'
    )
    
    requires_quote = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Requires Quote'
    )
    
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Category'
    )
    
    service_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Service.SERVICE_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Service Type'
    )
    
    pricing_type = forms.ChoiceField(
        choices=[('', 'All Pricing Types')] + Service.PRICING_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Pricing Type'
    )


class ServiceImportForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        label='CSV File',
        help_text='Upload a CSV file with service data'
    )
    
    update_existing = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Update Existing Services',
        help_text='Update services if they already exist (based on slug)'
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise ValidationError("File must be a CSV file.")
            if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("File size cannot exceed 5MB.")
        return csv_file


