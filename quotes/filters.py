import django_filters
from django import forms
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from .models import Quote, QuoteItem, QuoteAttachment, QuoteRevision, QuoteTemplate
from services.models import Service, ServiceAddOn

User = get_user_model()


class QuoteFilter(django_filters.FilterSet):
    quote_number = django_filters.CharFilter(
        field_name="quote_number",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by quote number..."}
        ),
    )

    client_name = django_filters.CharFilter(
        method="filter_client_name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by client name..."}
        ),
    )

    client_email = django_filters.CharFilter(
        field_name="client__email",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by client email..."}
        ),
    )

    service = django_filters.ModelChoiceFilter(
        queryset=Service.objects.filter(is_active=True),
        empty_label="All Services",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    status = django_filters.MultipleChoiceFilter(
        choices=Quote.QUOTE_STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
    )

    cleaning_type = django_filters.MultipleChoiceFilter(
        choices=Quote.CLEANING_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
    )

    urgency_level = django_filters.MultipleChoiceFilter(
        choices=Quote.URGENCY_LEVEL_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
    )

    is_ndis_client = django_filters.BooleanFilter(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    postcode = django_filters.CharFilter(
        field_name="postcode",
        lookup_expr="exact",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter postcode"}
        ),
    )

    state = django_filters.ChoiceFilter(
        choices=[
            ("NSW", "New South Wales"),
            ("VIC", "Victoria"),
            ("QLD", "Queensland"),
            ("WA", "Western Australia"),
            ("SA", "South Australia"),
            ("TAS", "Tasmania"),
            ("ACT", "Australian Capital Territory"),
            ("NT", "Northern Territory"),
        ],
        empty_label="All States",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    suburb = django_filters.CharFilter(
        field_name="suburb",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by suburb..."}
        ),
    )

    property_address = django_filters.CharFilter(
        field_name="property_address",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by address..."}
        ),
    )

    assigned_to = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(is_staff=True, is_active=True),
        empty_label="All Staff",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    created_at = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"type": "date", "class": "form-control"}
        )
    )

    expires_at = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"type": "date", "class": "form-control"}
        )
    )

    final_price = django_filters.RangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "Min/Max price"}
        )
    )

    number_of_rooms = django_filters.RangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "Min/Max rooms"}
        )
    )

    square_meters = django_filters.RangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "Min/Max sqm"}
        )
    )

    date_range = django_filters.ChoiceFilter(
        method="filter_date_range",
        choices=[
            ("today", "Today"),
            ("yesterday", "Yesterday"),
            ("this_week", "This Week"),
            ("last_week", "Last Week"),
            ("this_month", "This Month"),
            ("last_month", "Last Month"),
            ("this_quarter", "This Quarter"),
            ("this_year", "This Year"),
            ("last_30_days", "Last 30 Days"),
            ("last_90_days", "Last 90 Days"),
        ],
        empty_label="All Time",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    has_items = django_filters.BooleanFilter(
        method="filter_has_items",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    has_attachments = django_filters.BooleanFilter(
        method="filter_has_attachments",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    has_revisions = django_filters.BooleanFilter(
        method="filter_has_revisions",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    is_expired = django_filters.BooleanFilter(
        method="filter_is_expired",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    is_expiring_soon = django_filters.BooleanFilter(
        method="filter_is_expiring_soon",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    is_high_value = django_filters.BooleanFilter(
        method="filter_is_high_value",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    is_urgent = django_filters.BooleanFilter(
        method="filter_is_urgent",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Quote
        fields = []

    def filter_client_name(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(client__first_name__icontains=value)
                | Q(client__last_name__icontains=value)
                | Q(client__username__icontains=value)
            )
        return queryset

    def filter_date_range(self, queryset, name, value):
        now = timezone.now()

        if value == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif value == "yesterday":
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        elif value == "this_week":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif value == "last_week":
            start_date = now - timedelta(days=now.weekday() + 7)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now - timedelta(days=now.weekday() + 1)
            end_date = end_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        elif value == "this_month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif value == "last_month":
            if now.month == 1:
                start_date = now.replace(
                    year=now.year - 1,
                    month=12,
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
            else:
                start_date = now.replace(
                    month=now.month - 1,
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
            end_date = now.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(microseconds=1)
        elif value == "this_quarter":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(
                month=quarter_start_month,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            end_date = now
        elif value == "this_year":
            start_date = now.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end_date = now
        elif value == "last_30_days":
            start_date = now - timedelta(days=30)
            end_date = now
        elif value == "last_90_days":
            start_date = now - timedelta(days=90)
            end_date = now
        else:
            return queryset

        return queryset.filter(created_at__range=[start_date, end_date])

    def filter_has_items(self, queryset, name, value):
        if value is True:
            return queryset.annotate(items_count=Count("items")).filter(
                items_count__gt=0
            )
        elif value is False:
            return queryset.annotate(items_count=Count("items")).filter(items_count=0)
        return queryset

    def filter_has_attachments(self, queryset, name, value):
        if value is True:
            return queryset.annotate(attachments_count=Count("attachments")).filter(
                attachments_count__gt=0
            )
        elif value is False:
            return queryset.annotate(attachments_count=Count("attachments")).filter(
                attachments_count=0
            )
        return queryset

    def filter_has_revisions(self, queryset, name, value):
        if value is True:
            return queryset.annotate(revisions_count=Count("revisions")).filter(
                revisions_count__gt=0
            )
        elif value is False:
            return queryset.annotate(revisions_count=Count("revisions")).filter(
                revisions_count=0
            )
        return queryset

    def filter_is_expired(self, queryset, name, value):
        now = timezone.now()
        if value is True:
            return queryset.filter(expires_at__lt=now)
        elif value is False:
            return queryset.filter(Q(expires_at__gte=now) | Q(expires_at__isnull=True))
        return queryset

    def filter_is_expiring_soon(self, queryset, name, value):
        now = timezone.now()
        soon = now + timedelta(days=7)
        if value is True:
            return queryset.filter(expires_at__lte=soon, expires_at__gt=now)
        elif value is False:
            return queryset.filter(Q(expires_at__gt=soon) | Q(expires_at__isnull=True))
        return queryset

    def filter_is_high_value(self, queryset, name, value):
        if value is True:
            return queryset.filter(final_price__gte=1000)
        elif value is False:
            return queryset.filter(final_price__lt=1000)
        return queryset

    def filter_is_urgent(self, queryset, name, value):
        if value is True:
            return queryset.filter(urgency_level__gte=4)
        elif value is False:
            return queryset.filter(urgency_level__lt=4)
        return queryset


class QuoteItemFilter(django_filters.FilterSet):
    quote = django_filters.ModelChoiceFilter(
        queryset=Quote.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by item name..."}
        ),
    )

    service = django_filters.ModelChoiceFilter(
        queryset=Service.objects.filter(is_active=True),
        empty_label="All Services",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    addon = django_filters.ModelChoiceFilter(
        queryset=ServiceAddOn.objects.filter(is_active=True),
        empty_label="All Add-ons",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    item_type = django_filters.ChoiceFilter(
        choices=QuoteItem.ITEM_TYPE_CHOICES,
        empty_label="All Types",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    is_optional = django_filters.BooleanFilter(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    is_taxable = django_filters.BooleanFilter(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    unit_price = django_filters.RangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "Min/Max price"}
        )
    )

    total_price = django_filters.RangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "Min/Max total"}
        )
    )

    quantity = django_filters.RangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "Min/Max quantity"}
        )
    )

    class Meta:
        model = QuoteItem
        fields = []


class QuoteAttachmentFilter(django_filters.FilterSet):
    quote = django_filters.ModelChoiceFilter(
        queryset=Quote.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by title..."}
        ),
    )

    original_filename = django_filters.CharFilter(
        field_name="original_filename",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by filename..."}
        ),
    )

    attachment_type = django_filters.ChoiceFilter(
        choices=QuoteAttachment.ATTACHMENT_TYPE_CHOICES,
        empty_label="All Types",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    is_public = django_filters.BooleanFilter(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    uploaded_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(is_active=True),
        empty_label="All Users",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    uploaded_at = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"type": "date", "class": "form-control"}
        )
    )

    file_size = django_filters.RangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "Min/Max size (bytes)"}
        )
    )

    class Meta:
        model = QuoteAttachment
        fields = []


class QuoteRevisionFilter(django_filters.FilterSet):
    quote = django_filters.ModelChoiceFilter(
        queryset=Quote.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    revision_number = django_filters.NumberFilter(
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Revision number"}
        )
    )

    revised_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(is_active=True),
        empty_label="All Users",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    created_at = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"type": "date", "class": "form-control"}
        )
    )

    previous_price = django_filters.RangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "Min/Max previous price"}
        )
    )

    new_price = django_filters.RangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "Min/Max new price"}
        )
    )

    reason = django_filters.CharFilter(
        field_name="reason",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by reason..."}
        ),
    )

    class Meta:
        model = QuoteRevision
        fields = []


class QuoteTemplateFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by template name..."}
        ),
    )

    cleaning_type = django_filters.ChoiceFilter(
        choices=Quote.CLEANING_TYPE_CHOICES,
        empty_label="All Types",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    default_service = django_filters.ModelChoiceFilter(
        queryset=Service.objects.filter(is_active=True),
        empty_label="All Services",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    default_urgency_level = django_filters.ChoiceFilter(
        choices=Quote.URGENCY_LEVEL_CHOICES,
        empty_label="All Urgency Levels",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    is_active = django_filters.BooleanFilter(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    is_ndis_template = django_filters.BooleanFilter(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    created_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(is_staff=True, is_active=True),
        empty_label="All Staff",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    created_at = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"type": "date", "class": "form-control"}
        )
    )

    usage_count = django_filters.RangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "Min/Max usage"}
        )
    )

    class Meta:
        model = QuoteTemplate
        fields = []


class AdvancedQuoteFilter(QuoteFilter):
    search = django_filters.CharFilter(
        method="filter_search",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search quotes, clients, addresses...",
            }
        ),
    )

    has_special_requirements = django_filters.BooleanFilter(
        method="filter_has_special_requirements",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    has_access_instructions = django_filters.BooleanFilter(
        method="filter_has_access_instructions",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    has_preferred_date = django_filters.BooleanFilter(
        method="filter_has_preferred_date",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    has_preferred_time = django_filters.BooleanFilter(
        method="filter_has_preferred_time",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    ndis_participant_number = django_filters.CharFilter(
        field_name="ndis_participant_number",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "NDIS participant number..."}
        ),
    )

    plan_manager_name = django_filters.CharFilter(
        field_name="plan_manager_name",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Plan manager name..."}
        ),
    )

    support_coordinator_name = django_filters.CharFilter(
        field_name="support_coordinator_name",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Support coordinator name...",
            }
        ),
    )

    rejection_reason = django_filters.CharFilter(
        field_name="rejection_reason",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search rejection reason..."}
        ),
    )

    admin_notes = django_filters.CharFilter(
        field_name="admin_notes",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search admin notes..."}
        ),
    )

    submitted_at = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"type": "date", "class": "form-control"}
        )
    )

    approved_at = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"type": "date", "class": "form-control"}
        )
    )

    reviewed_at = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"type": "date", "class": "form-control"}
        )
    )

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(quote_number__icontains=value)
                | Q(client__first_name__icontains=value)
                | Q(client__last_name__icontains=value)
                | Q(client__email__icontains=value)
                | Q(property_address__icontains=value)
                | Q(suburb__icontains=value)
                | Q(service__name__icontains=value)
                | Q(special_requirements__icontains=value)
                | Q(access_instructions__icontains=value)
            )
        return queryset

    def filter_has_special_requirements(self, queryset, name, value):
        if value is True:
            return queryset.exclude(special_requirements__isnull=True).exclude(
                special_requirements=""
            )
        elif value is False:
            return queryset.filter(
                Q(special_requirements__isnull=True) | Q(special_requirements="")
            )
        return queryset

    def filter_has_access_instructions(self, queryset, name, value):
        if value is True:
            return queryset.exclude(access_instructions__isnull=True).exclude(
                access_instructions=""
            )
        elif value is False:
            return queryset.filter(
                Q(access_instructions__isnull=True) | Q(access_instructions="")
            )
        return queryset

    def filter_has_preferred_date(self, queryset, name, value):
        if value is True:
            return queryset.exclude(preferred_date__isnull=True)
        elif value is False:
            return queryset.filter(preferred_date__isnull=True)
        return queryset

    def filter_has_preferred_time(self, queryset, name, value):
        if value is True:
            return queryset.exclude(preferred_time__isnull=True)
        elif value is False:
            return queryset.filter(preferred_time__isnull=True)
        return queryset


class QuoteAnalyticsFilter(django_filters.FilterSet):
    group_by = django_filters.ChoiceFilter(
        method="filter_group_by",
        choices=[
            ("status", "By Status"),
            ("cleaning_type", "By Cleaning Type"),
            ("urgency", "By Urgency Level"),
            ("month", "By Month"),
            ("state", "By State"),
            ("service", "By Service"),
            ("assigned_to", "By Assigned Staff"),
        ],
        empty_label="No Grouping",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    metric = django_filters.ChoiceFilter(
        method="filter_metric",
        choices=[
            ("count", "Quote Count"),
            ("total_value", "Total Value"),
            ("average_value", "Average Value"),
            ("conversion_rate", "Conversion Rate"),
        ],
        empty_label="All Metrics",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def filter_group_by(self, queryset, name, value):
        return queryset

    def filter_metric(self, queryset, name, value):
        return queryset

    class Meta:
        model = Quote
        fields = []

class QuoteReportFilter(django_filters.FilterSet):
    report_type = django_filters.ChoiceFilter(
        method='filter_report_type',
        choices=[
            ('summary', 'Summary Report'),
            ('detailed', 'Detailed Report'),
            ('analytics', 'Analytics Report'),
            ('conversion', 'Conversion Report'),
            ('performance', 'Performance Report')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    time_period = django_filters.ChoiceFilter(
        method='filter_time_period',
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    include_ndis = django_filters.BooleanFilter(
        method='filter_include_ndis',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_general = django_filters.BooleanFilter(
        method='filter_include_general',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def filter_report_type(self, queryset, name, value):
        return queryset
    
    def filter_time_period(self, queryset, name, value):
        return queryset
    
    def filter_include_ndis(self, queryset, name, value):
        if value is True:
            return queryset.filter(is_ndis_client=True)
        return queryset
    
    def filter_include_general(self, queryset, name, value):
        if value is True:
            return queryset.filter(is_ndis_client=False)
        return queryset
    
    class Meta:
        model = Quote
        fields = []


class QuoteDashboardFilter(django_filters.FilterSet):
    dashboard_view = django_filters.ChoiceFilter(
        method='filter_dashboard_view',
        choices=[
            ('overview', 'Overview'),
            ('pending', 'Pending Quotes'),
            ('urgent', 'Urgent Quotes'),
            ('expiring', 'Expiring Soon'),
            ('high_value', 'High Value'),
            ('ndis', 'NDIS Quotes'),
            ('recent', 'Recent Activity')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    time_frame = django_filters.ChoiceFilter(
        method='filter_time_frame',
        choices=[
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('quarter', 'This Quarter'),
            ('year', 'This Year')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def filter_dashboard_view(self, queryset, name, value):
        now = timezone.now()
        
        if value == 'pending':
            return queryset.filter(status__in=['submitted', 'under_review'])
        elif value == 'urgent':
            return queryset.filter(urgency_level__gte=4)
        elif value == 'expiring':
            soon = now + timedelta(days=7)
            return queryset.filter(expires_at__lte=soon, expires_at__gt=now)
        elif value == 'high_value':
            return queryset.filter(final_price__gte=1000)
        elif value == 'ndis':
            return queryset.filter(is_ndis_client=True)
        elif value == 'recent':
            recent = now - timedelta(days=7)
            return queryset.filter(created_at__gte=recent)
        
        return queryset
    
    def filter_time_frame(self, queryset, name, value):
        now = timezone.now()
        
        if value == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(created_at__gte=start_date)
        elif value == 'week':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(created_at__gte=start_date)
        elif value == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(created_at__gte=start_date)
        elif value == 'quarter':
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(created_at__gte=start_date)
        elif value == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(created_at__gte=start_date)
        
        return queryset
    
    class Meta:
        model = Quote
        fields = []


class QuoteExportFilter(django_filters.FilterSet):
    export_format = django_filters.ChoiceFilter(
        method='filter_export_format',
        choices=[
            ('csv', 'CSV'),
            ('excel', 'Excel'),
            ('pdf', 'PDF'),
            ('json', 'JSON')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    include_items = django_filters.BooleanFilter(
        method='filter_include_items',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_attachments = django_filters.BooleanFilter(
        method='filter_include_attachments',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_revisions = django_filters.BooleanFilter(
        method='filter_include_revisions',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def filter_export_format(self, queryset, name, value):
        return queryset
    
    def filter_include_items(self, queryset, name, value):
        return queryset
    
    def filter_include_attachments(self, queryset, name, value):
        return queryset
    
    def filter_include_revisions(self, queryset, name, value):
        return queryset
    
    class Meta:
        model = Quote
        fields = []


def get_quote_filter_class(filter_type='basic', user=None):
    filter_classes = {
        'basic': QuoteFilter,
        'advanced': AdvancedQuoteFilter,
        'analytics': QuoteAnalyticsFilter,
        'report': QuoteReportFilter,
        'dashboard': QuoteDashboardFilter,
        'export': QuoteExportFilter,
        'item': QuoteItemFilter,
        'attachment': QuoteAttachmentFilter,
        'revision': QuoteRevisionFilter,
        'template': QuoteTemplateFilter
    }
    
    return filter_classes.get(filter_type, QuoteFilter)


def apply_user_permissions_to_filter(filter_instance, user):
    if not user.is_staff:
        if hasattr(filter_instance, 'form'):
            if 'assigned_to' in filter_instance.form.fields:
                del filter_instance.form.fields['assigned_to']
            
            if 'admin_notes' in filter_instance.form.fields:
                del filter_instance.form.fields['admin_notes']
    
    return filter_instance


def get_filter_choices_for_user(user):
    base_choices = {
        'status': Quote.QUOTE_STATUS_CHOICES,
        'cleaning_type': Quote.CLEANING_TYPE_CHOICES,
        'urgency_level': Quote.URGENCY_LEVEL_CHOICES,
        'state': Quote.STATE_CHOICES
    }
    
    if user.is_staff:
        base_choices['assigned_to'] = [
            (u.id, u.get_full_name()) 
            for u in User.objects.filter(is_staff=True, is_active=True)
        ]
    
    return base_choices


def build_dynamic_filter(filter_params, user=None):
    filter_class = get_quote_filter_class('advanced', user)
    
    class DynamicQuoteFilter(filter_class):
        pass
    
    if user and not user.is_staff:
        DynamicQuoteFilter.base_filters = {
            k: v for k, v in DynamicQuoteFilter.base_filters.items()
            if k not in ['assigned_to', 'admin_notes']
        }
    
    return DynamicQuoteFilter


class QuoteFilterMixin:
    def get_filtered_queryset(self, queryset, filter_params, user=None):
        filter_class = get_quote_filter_class('basic', user)
        filter_instance = filter_class(filter_params, queryset=queryset)
        
        if user:
            filter_instance = apply_user_permissions_to_filter(filter_instance, user)
        
        return filter_instance.qs
    
    def get_filter_form(self, filter_type='basic', user=None):
        filter_class = get_quote_filter_class(filter_type, user)
        filter_instance = filter_class()
        
        if user:
            filter_instance = apply_user_permissions_to_filter(filter_instance, user)
        
        return filter_instance.form
    
    def validate_filter_params(self, filter_params, user=None):
        errors = []
        
        if 'final_price' in filter_params:
            try:
                price_range = filter_params['final_price']
                if price_range and any(float(p) < 0 for p in price_range if p):
                    errors.append("Price values cannot be negative")
            except (ValueError, TypeError):
                errors.append("Invalid price range format")
        
        if 'created_at' in filter_params:
            try:
                date_range = filter_params['created_at']
                if date_range and len(date_range) == 2:
                    start_date, end_date = date_range
                    if start_date and end_date and start_date > end_date:
                        errors.append("Start date cannot be later than end date")
            except (ValueError, TypeError):
                errors.append("Invalid date range format")
        
        return errors


quote_filter_mixin = QuoteFilterMixin()


def get_default_quote_filters():
    return {
        'status': ['submitted', 'under_review', 'approved'],
        'is_active': True,
        'ordering': ['-created_at']
    }


def get_user_specific_filters(user):
    filters = get_default_quote_filters()
    
    if not user.is_staff:
        filters['client'] = user
    
    return filters


def optimize_filter_queryset(queryset, filter_params):
    if 'status' in filter_params:
        queryset = queryset.select_related('client', 'service', 'assigned_to')
    
    if any(param in filter_params for param in ['has_items', 'has_attachments', 'has_revisions']):
        queryset = queryset.prefetch_related('items', 'attachments', 'revisions')
    
    return queryset


class QuoteFilterRegistry:
    _filters = {}
    
    @classmethod
    def register(cls, name, filter_class):
        cls._filters[name] = filter_class
    
    @classmethod
    def get(cls, name):
        return cls._filters.get(name)
    
    @classmethod
    def get_all(cls):
        return cls._filters.copy()


QuoteFilterRegistry.register('basic', QuoteFilter)
QuoteFilterRegistry.register('advanced', AdvancedQuoteFilter)
QuoteFilterRegistry.register('analytics', QuoteAnalyticsFilter)
QuoteFilterRegistry.register('report', QuoteReportFilter)
QuoteFilterRegistry.register('dashboard', QuoteDashboardFilter)
QuoteFilterRegistry.register('export', QuoteExportFilter)
QuoteFilterRegistry.register('item', QuoteItemFilter)
QuoteFilterRegistry.register('attachment', QuoteAttachmentFilter)
QuoteFilterRegistry.register('revision', QuoteRevisionFilter)
QuoteFilterRegistry.register('template', QuoteTemplateFilter)
