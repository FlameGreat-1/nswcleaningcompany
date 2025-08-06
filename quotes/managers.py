from django.db import models
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg, F, Case, When, Value
from django.db.models.functions import Coalesce
from decimal import Decimal
from datetime import timedelta


class QuoteQuerySet(models.QuerySet):
    """Custom QuerySet for Quote model with business logic methods"""

    def active(self):
        """Get active quotes (not cancelled or expired)"""
        return self.exclude(status__in=["cancelled", "expired"])

    def pending(self):
        """Get quotes pending review"""
        return self.filter(status__in=["submitted", "under_review"])

    def approved(self):
        """Get approved quotes"""
        return self.filter(status="approved")

    def expired(self):
        """Get expired quotes"""
        now = timezone.now()
        return self.filter(Q(expires_at__lt=now) | Q(status="expired"))

    def expiring_soon(self, days=7):
        """Get quotes expiring within specified days"""
        cutoff_date = timezone.now() + timedelta(days=days)
        return self.filter(
            status="approved",
            expires_at__lte=cutoff_date,
            expires_at__gt=timezone.now(),
        )

    def ndis_quotes(self):
        """Get NDIS client quotes"""
        return self.filter(is_ndis_client=True)

    def general_quotes(self):
        """Get general (non-NDIS) client quotes"""
        return self.filter(is_ndis_client=False)

    def by_cleaning_type(self, cleaning_type):
        """Filter by cleaning type"""
        return self.filter(cleaning_type=cleaning_type)

    def by_urgency_level(self, urgency_level):
        """Filter by urgency level"""
        return self.filter(urgency_level=urgency_level)

    def by_postcode(self, postcode):
        """Filter by property postcode"""
        return self.filter(postcode=postcode)

    def by_state(self, state):
        """Filter by property state"""
        return self.filter(state=state)

    def by_client(self, client):
        """Filter by client"""
        return self.filter(client=client)

    def by_date_range(self, start_date, end_date):
        """Filter by creation date range"""
        return self.filter(
            created_at__date__gte=start_date, created_at__date__lte=end_date
        )

    def high_value(self, threshold=1000):
        """Get high-value quotes above threshold"""
        return self.filter(final_price__gte=threshold)

    def urgent(self):
        """Get urgent quotes (urgency level 4 or 5)"""
        return self.filter(urgency_level__gte=4)

    def with_attachments(self):
        """Get quotes that have attachments"""
        return self.filter(attachments__isnull=False).distinct()

    def without_attachments(self):
        """Get quotes without attachments"""
        return self.filter(attachments__isnull=True)

    def assigned_to_staff(self, staff_user):
        """Get quotes assigned to specific staff member"""
        return self.filter(assigned_to=staff_user)

    def unassigned(self):
        """Get unassigned quotes"""
        return self.filter(assigned_to__isnull=True)

    def convertible(self):
        """Get quotes that can be converted to jobs"""
        return self.filter(status="approved", expires_at__gt=timezone.now())

    def with_special_requirements(self):
        """Get quotes with special requirements"""
        return self.exclude(special_requirements="")

    def recent(self, days=30):
        """Get quotes created in the last N days"""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)

    def this_month(self):
        """Get quotes created this month"""
        now = timezone.now()
        return self.filter(created_at__year=now.year, created_at__month=now.month)

    def this_year(self):
        """Get quotes created this year"""
        return self.filter(created_at__year=timezone.now().year)

    def with_pricing_breakdown(self):
        """Annotate quotes with detailed pricing breakdown"""
        return self.annotate(
            total_items_cost=Coalesce(
                Sum("items__total_price"), Value(0, output_field=models.DecimalField())
            ),
            items_count=Count("items"),
            attachments_count=Count("attachments"),
            revisions_count=Count("revisions"),
            has_special_requirements=Case(
                When(special_requirements="", then=Value(False)),
                default=Value(True),
                output_field=models.BooleanField(),
            ),
            days_since_created=Case(
                When(
                    created_at__isnull=False,
                    then=(timezone.now().date() - F("created_at__date")),
                ),
                default=Value(0),
                output_field=models.IntegerField(),
            ),
            days_until_expiry=Case(
                When(
                    expires_at__isnull=False,
                    then=(F("expires_at__date") - timezone.now().date()),
                ),
                default=Value(None),
                output_field=models.IntegerField(),
            ),
        )

    def search(self, query):
        """Search quotes by various fields"""
        if not query:
            return self

        return self.filter(
            Q(quote_number__icontains=query)
            | Q(client__first_name__icontains=query)
            | Q(client__last_name__icontains=query)
            | Q(client__email__icontains=query)
            | Q(property_address__icontains=query)
            | Q(suburb__icontains=query)
            | Q(postcode__icontains=query)
            | Q(special_requirements__icontains=query)
            | Q(ndis_participant_number__icontains=query)
        ).distinct()

    def statistics(self):
        """Get comprehensive quote statistics"""
        stats = self.aggregate(
            total_quotes=Count("id"),
            total_value=Coalesce(Sum("final_price"), Value(0)),
            average_value=Coalesce(Avg("final_price"), Value(0)),
            pending_count=Count(
                "id", filter=Q(status__in=["submitted", "under_review"])
            ),
            approved_count=Count("id", filter=Q(status="approved")),
            rejected_count=Count("id", filter=Q(status="rejected")),
            expired_count=Count("id", filter=Q(status="expired")),
            converted_count=Count("id", filter=Q(status="converted")),
            ndis_count=Count("id", filter=Q(is_ndis_client=True)),
            urgent_count=Count("id", filter=Q(urgency_level__gte=4)),
            high_value_count=Count("id", filter=Q(final_price__gte=1000)),
            with_attachments_count=Count("id", filter=Q(attachments__isnull=False)),
        )

        # Calculate conversion rate
        if stats["total_quotes"] > 0:
            stats["approval_rate"] = (
                stats["approved_count"] / stats["total_quotes"]
            ) * 100
            stats["conversion_rate"] = (
                stats["converted_count"] / stats["total_quotes"]
            ) * 100
            stats["rejection_rate"] = (
                stats["rejected_count"] / stats["total_quotes"]
            ) * 100
        else:
            stats["approval_rate"] = 0
            stats["conversion_rate"] = 0
            stats["rejection_rate"] = 0

        return stats


class QuoteManager(models.Manager):
    """Custom manager for Quote model"""

    def get_queryset(self):
        return QuoteQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def pending(self):
        return self.get_queryset().pending()

    def approved(self):
        return self.get_queryset().approved()

    def expired(self):
        return self.get_queryset().expired()

    def expiring_soon(self, days=7):
        return self.get_queryset().expiring_soon(days)

    def ndis_quotes(self):
        return self.get_queryset().ndis_quotes()

    def general_quotes(self):
        return self.get_queryset().general_quotes()

    def urgent(self):
        return self.get_queryset().urgent()

    def high_value(self, threshold=1000):
        return self.get_queryset().high_value(threshold)

    def recent(self, days=30):
        return self.get_queryset().recent(days)

    def this_month(self):
        return self.get_queryset().this_month()

    def this_year(self):
        return self.get_queryset().this_year()

    def search(self, query):
        return self.get_queryset().search(query)

    def statistics(self):
        return self.get_queryset().statistics()

    def create_from_calculator(self, client, service, calculator_data):
        """Create quote from calculator data"""
        quote = self.create(
            client=client,
            service=service,
            cleaning_type=calculator_data.get("cleaning_type", "general"),
            property_address=calculator_data.get("property_address", ""),
            postcode=calculator_data.get("postcode", ""),
            suburb=calculator_data.get("suburb", ""),
            state=calculator_data.get("state", ""),
            number_of_rooms=calculator_data.get("number_of_rooms", 1),
            square_meters=calculator_data.get("square_meters"),
            urgency_level=calculator_data.get("urgency_level", 2),
            preferred_date=calculator_data.get("preferred_date"),
            preferred_time=calculator_data.get("preferred_time"),
            special_requirements=calculator_data.get("special_requirements", ""),
            status="draft",
        )

        # Calculate initial pricing
        quote.update_pricing()

        return quote
    
    def get_dashboard_data(self, user=None):
        queryset = self.get_queryset()
        if user and not user.is_staff:
            queryset = queryset.filter(client=user)
        
        now = timezone.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        dashboard_data = {
            'total_quotes': queryset.count(),
            'pending_quotes': queryset.filter(status__in=['submitted', 'under_review']).count(),
            'approved_quotes': queryset.filter(status='approved').count(),
            'expired_quotes': queryset.expired().count(),
            'quotes_this_week': queryset.filter(created_at__date__gte=week_ago).count(),
            'quotes_this_month': queryset.filter(created_at__date__gte=month_ago).count(),
            'total_value': queryset.aggregate(total=Sum('final_price'))['total'] or 0,
            'average_quote_value': queryset.aggregate(avg=Avg('final_price'))['avg'] or 0,
            'urgent_quotes': queryset.filter(urgency_level__gte=4).count(),
            'ndis_quotes': queryset.filter(is_ndis_client=True).count(),
            'expiring_soon': queryset.expiring_soon(7).count(),
        }
        
        return dashboard_data
    
    def get_analytics_data(self, start_date=None, end_date=None):
        queryset = self.get_queryset()
        
        if start_date and end_date:
            queryset = queryset.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )
        
        analytics = {
            'quotes_by_status': queryset.values('status').annotate(
                count=Count('id'),
                total_value=Sum('final_price')
            ).order_by('-count'),
            
            'quotes_by_cleaning_type': queryset.values('cleaning_type').annotate(
                count=Count('id'),
                avg_value=Avg('final_price')
            ).order_by('-count'),
            
            'quotes_by_urgency': queryset.values('urgency_level').annotate(
                count=Count('id'),
                avg_value=Avg('final_price')
            ).order_by('urgency_level'),
            
            'quotes_by_state': queryset.values('state').annotate(
                count=Count('id'),
                total_value=Sum('final_price')
            ).order_by('-count'),
            
            'monthly_trends': queryset.extra(
                select={'month': "DATE_FORMAT(created_at, '%%Y-%%m')"}
            ).values('month').annotate(
                count=Count('id'),
                total_value=Sum('final_price'),
                avg_value=Avg('final_price')
            ).order_by('month'),
            
            'conversion_funnel': {
                'submitted': queryset.filter(status='submitted').count(),
                'under_review': queryset.filter(status='under_review').count(),
                'approved': queryset.filter(status='approved').count(),
                'converted': queryset.filter(status='converted').count(),
                'rejected': queryset.filter(status='rejected').count(),
            }
        }
        
        return analytics


class QuoteItemQuerySet(models.QuerySet):
    
    def services(self):
        return self.filter(item_type='service')
    
    def addons(self):
        return self.filter(item_type='addon')
    
    def extras(self):
        return self.filter(item_type='extra')
    
    def materials(self):
        return self.filter(item_type='material')
    
    def taxable(self):
        return self.filter(is_taxable=True)
    
    def non_taxable(self):
        return self.filter(is_taxable=False)
    
    def optional(self):
        return self.filter(is_optional=True)
    
    def required(self):
        return self.filter(is_optional=False)
    
    def by_quote(self, quote):
        return self.filter(quote=quote)
    
    def total_value(self):
        return self.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
    
    def total_gst(self):
        return self.filter(is_taxable=True).aggregate(
            gst=Sum(F('total_price') * Decimal('0.10'))
        )['gst'] or Decimal('0.00')
    
    def with_totals(self):
        return self.annotate(
            gst_amount=Case(
                When(is_taxable=True, then=F('total_price') * Decimal('0.10')),
                default=Value(0),
                output_field=models.DecimalField(max_digits=10, decimal_places=2)
            ),
            total_with_gst=F('total_price') + F('gst_amount')
        )


class QuoteItemManager(models.Manager):
    
    def get_queryset(self):
        return QuoteItemQuerySet(self.model, using=self._db)
    
    def services(self):
        return self.get_queryset().services()
    
    def addons(self):
        return self.get_queryset().addons()
    
    def extras(self):
        return self.get_queryset().extras()
    
    def materials(self):
        return self.get_queryset().materials()
    
    def taxable(self):
        return self.get_queryset().taxable()
    
    def optional(self):
        return self.get_queryset().optional()
    
    def required(self):
        return self.get_queryset().required()
    
    def create_service_item(self, quote, service, quantity=1):
        return self.create(
            quote=quote,
            service=service,
            item_type='service',
            name=service.name,
            description=service.description,
            quantity=quantity,
            unit_price=service.base_price,
            is_taxable=True,
            is_optional=False
        )
    
    def create_addon_item(self, quote, addon, quantity=1):
        return self.create(
            quote=quote,
            addon=addon,
            item_type='addon',
            name=addon.name,
            description=addon.description,
            quantity=quantity,
            unit_price=addon.price,
            is_taxable=True,
            is_optional=addon.is_optional
        )
    
    def create_custom_item(self, quote, name, price, item_type='extra', **kwargs):
        return self.create(
            quote=quote,
            item_type=item_type,
            name=name,
            unit_price=price,
            quantity=kwargs.get('quantity', 1),
            description=kwargs.get('description', ''),
            is_taxable=kwargs.get('is_taxable', True),
            is_optional=kwargs.get('is_optional', False)
        )


class QuoteAttachmentQuerySet(models.QuerySet):
    
    def images(self):
        return self.filter(attachment_type='image')
    
    def documents(self):
        return self.filter(attachment_type='document')
    
    def floor_plans(self):
        return self.filter(attachment_type='floor_plan')
    
    def references(self):
        return self.filter(attachment_type='reference')
    
    def public(self):
        return self.filter(is_public=True)
    
    def private(self):
        return self.filter(is_public=False)
    
    def by_quote(self, quote):
        return self.filter(quote=quote)
    
    def by_user(self, user):
        return self.filter(uploaded_by=user)
    
    def recent(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)
    
    def large_files(self, size_mb=5):
        size_bytes = size_mb * 1024 * 1024
        return self.filter(file_size__gte=size_bytes)


class QuoteAttachmentManager(models.Manager):
    
    def get_queryset(self):
        return QuoteAttachmentQuerySet(self.model, using=self._db)
    
    def images(self):
        return self.get_queryset().images()
    
    def documents(self):
        return self.get_queryset().documents()
    
    def public(self):
        return self.get_queryset().public()
    
    def private(self):
        return self.get_queryset().private()
    
    def recent(self, days=30):
        return self.get_queryset().recent(days)


class QuoteRevisionQuerySet(models.QuerySet):
    
    def by_quote(self, quote):
        return self.filter(quote=quote)
    
    def by_user(self, user):
        return self.filter(revised_by=user)
    
    def recent(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)
    
    def price_increases(self):
        return self.filter(new_price__gt=F('previous_price'))
    
    def price_decreases(self):
        return self.filter(new_price__lt=F('previous_price'))
    
    def with_price_changes(self):
        return self.annotate(
            price_change=F('new_price') - F('previous_price'),
            price_change_percent=Case(
                When(previous_price__gt=0, then=
                    (F('new_price') - F('previous_price')) / F('previous_price') * 100
                ),
                default=Value(0),
                output_field=models.DecimalField(max_digits=5, decimal_places=2)
            )
        )


class QuoteRevisionManager(models.Manager):
    
    def get_queryset(self):
        return QuoteRevisionQuerySet(self.model, using=self._db)
    
    def by_quote(self, quote):
        return self.get_queryset().by_quote(quote)
    
    def recent(self, days=30):
        return self.get_queryset().recent(days)
    
    def price_increases(self):
        return self.get_queryset().price_increases()
    
    def price_decreases(self):
        return self.get_queryset().price_decreases()


class QuoteTemplateQuerySet(models.QuerySet):
    
    def active(self):
        return self.filter(is_active=True)
    
    def ndis_templates(self):
        return self.filter(is_ndis_template=True)
    
    def general_templates(self):
        return self.filter(is_ndis_template=False)
    
    def by_cleaning_type(self, cleaning_type):
        return self.filter(cleaning_type=cleaning_type)
    
    def popular(self, limit=10):
        return self.order_by('-usage_count')[:limit]
    
    def recent(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)


class QuoteTemplateManager(models.Manager):
    
    def get_queryset(self):
        return QuoteTemplateQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def ndis_templates(self):
        return self.get_queryset().ndis_templates()
    
    def general_templates(self):
        return self.get_queryset().general_templates()
    
    def popular(self, limit=10):
        return self.get_queryset().popular(limit)
    
    def for_cleaning_type(self, cleaning_type):
        return self.get_queryset().by_cleaning_type(cleaning_type).active()

