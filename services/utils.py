from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Tuple
import logging
from .models import (
    Service,
    ServiceArea,
    ServiceAddOn,
    ServiceAvailability,
    ServicePricing,
)

logger = logging.getLogger(__name__)


def calculate_service_quote(
    service: Service,
    user,
    rooms: int = 1,
    square_meters: Optional[Decimal] = None,
    hours: Optional[int] = None,
    postcode: str = "",
    addon_ids: List[int] = None,
    special_requests: str = "",
    preferred_date: Optional[datetime] = None,
    **kwargs,
) -> Dict[str, Any]:
    try:
        if not service.is_available_in_area(postcode):
            raise ValidationError(f"Service not available in postcode {postcode}")

        base_price = service.calculate_price(
            rooms=rooms, hours=hours, square_meters=square_meters
        )

        travel_cost = calculate_travel_cost(service, postcode)

        addon_cost = Decimal("0.00")
        selected_addons = []
        if addon_ids:
            addons = ServiceAddOn.objects.filter(
                id__in=addon_ids, services=service, is_active=True
            )
            for addon in addons:
                addon_cost += addon.price
                selected_addons.append(
                    {"id": addon.id, "name": addon.name, "price": float(addon.price)}
                )

        subtotal = base_price + addon_cost + travel_cost

        gst_rate = Decimal("0.10")
        gst_amount = (subtotal * gst_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        total_price = subtotal + gst_amount

        urgency_multiplier = calculate_urgency_multiplier(preferred_date)
        if urgency_multiplier > 1:
            urgency_fee = (subtotal * (urgency_multiplier - 1)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            total_price += urgency_fee
        else:
            urgency_fee = Decimal("0.00")

        discount_amount = calculate_user_discount(user, service, subtotal)
        if discount_amount > 0:
            total_price -= discount_amount

        quote_data = {
            "service_id": service.id,
            "service_name": service.name,
            "base_price": float(base_price),
            "travel_cost": float(travel_cost),
            "addon_cost": float(addon_cost),
            "selected_addons": selected_addons,
            "subtotal": float(subtotal),
            "gst_amount": float(gst_amount),
            "urgency_fee": float(urgency_fee),
            "discount_amount": float(discount_amount),
            "total_price": float(total_price),
            "quote_valid_until": (timezone.now() + timedelta(days=7)).isoformat(),
            "estimated_duration": service.estimated_duration,
            "duration_unit": service.duration_unit,
            "parameters": {
                "rooms": rooms,
                "square_meters": float(square_meters) if square_meters else None,
                "hours": hours,
                "postcode": postcode,
                "special_requests": special_requests,
            },
            "is_ndis_eligible": service.is_ndis_eligible,
            "requires_quote_approval": service.requires_quote,
        }

        logger.info(f"Quote calculated for service {service.id}: ${total_price}")
        return quote_data

    except Exception as e:
        logger.error(f"Error calculating quote for service {service.id}: {str(e)}")
        raise


def calculate_travel_cost(service: Service, postcode: str) -> Decimal:
    try:
        service_area = service.service_areas.filter(
            postcode=postcode, is_active=True
        ).first()

        if service_area:
            return service_area.travel_cost

        return Decimal("0.00")

    except Exception as e:
        logger.error(f"Error calculating travel cost: {str(e)}")
        return Decimal("0.00")


def calculate_urgency_multiplier(preferred_date: Optional[datetime]) -> Decimal:
    if not preferred_date:
        return Decimal("1.00")

    now = timezone.now()
    if preferred_date.date() <= now.date():
        return Decimal("1.00")

    days_ahead = (preferred_date.date() - now.date()).days

    if days_ahead <= 1:
        return Decimal("1.50")
    elif days_ahead <= 3:
        return Decimal("1.25")
    elif days_ahead <= 7:
        return Decimal("1.10")
    else:
        return Decimal("1.00")


def calculate_user_discount(user, service: Service, subtotal: Decimal) -> Decimal:
    discount_amount = Decimal("0.00")

    try:
        if hasattr(user, "client_profile") and user.client_profile:
            profile = user.client_profile

            if user.client_type == "ndis" and service.is_ndis_eligible:
                discount_amount = subtotal * Decimal("0.05")

            if hasattr(profile, "loyalty_tier"):
                if profile.loyalty_tier == "gold":
                    discount_amount = max(discount_amount, subtotal * Decimal("0.10"))
                elif profile.loyalty_tier == "silver":
                    discount_amount = max(discount_amount, subtotal * Decimal("0.05"))

        if user.date_joined and (timezone.now() - user.date_joined).days <= 30:
            new_customer_discount = subtotal * Decimal("0.15")
            discount_amount = max(discount_amount, new_customer_discount)

        return discount_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    except Exception as e:
        logger.error(f"Error calculating user discount: {str(e)}")
        return Decimal("0.00")


def get_available_time_slots(
    service: Service, date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    try:
        if not date:
            date = timezone.now().date()

        day_of_week = date.weekday()

        availability_slots = ServiceAvailability.objects.filter(
            service=service, day_of_week=day_of_week, is_available=True
        ).order_by("start_time")

        available_slots = []
        for slot in availability_slots:
            current_time = slot.start_time
            end_time = slot.end_time

            while current_time < end_time:
                next_time = (
                    datetime.combine(date, current_time) + timedelta(hours=1)
                ).time()
                if next_time > end_time:
                    break

                slot_datetime = datetime.combine(date, current_time)

                if slot_datetime > timezone.now():
                    available_slots.append(
                        {
                            "time": current_time.strftime("%H:%M"),
                            "datetime": slot_datetime.isoformat(),
                            "available": True,
                            "max_bookings": slot.max_bookings,
                        }
                    )

                current_time = next_time

        return available_slots

    except Exception as e:
        logger.error(f"Error getting available time slots: {str(e)}")
        return []


def validate_service_request(service: Service, user, **kwargs) -> Tuple[bool, str]:
    try:
        if not service.is_active:
            return False, "Service is not currently active"

        if service.is_ndis_eligible and user.user_type == "client":
            if user.client_type != "ndis":
                return False, "This service is only available to NDIS clients"

            if (
                not hasattr(user, "client_profile")
                or not user.client_profile.ndis_number
            ):
                return False, "NDIS number is required for this service"

        postcode = kwargs.get("postcode")
        if postcode and not service.is_available_in_area(postcode):
            return False, f"Service is not available in postcode {postcode}"

        rooms = kwargs.get("rooms", 1)
        if rooms < service.minimum_rooms:
            return False, f"Minimum {service.minimum_rooms} rooms required"

        if service.maximum_rooms and rooms > service.maximum_rooms:
            return False, f"Maximum {service.maximum_rooms} rooms allowed"

        preferred_date = kwargs.get("preferred_date")
        if preferred_date and preferred_date.date() < timezone.now().date():
            return False, "Preferred date cannot be in the past"

        return True, "Service request is valid"

    except Exception as e:
        logger.error(f"Error validating service request: {str(e)}")
        return False, "Error validating service request"


def get_service_recommendations(user, limit: int = 10) -> List[Service]:
    try:
        if user.user_type == "client" and user.client_type == "ndis":
            base_queryset = Service.objects.ndis_eligible()
        else:
            base_queryset = Service.objects.general_services()

        if hasattr(user, "addresses") and user.addresses.exists():
            primary_address = user.addresses.filter(is_primary=True).first()
            if not primary_address:
                primary_address = user.addresses.first()

            if primary_address:
                base_queryset = base_queryset.filter(
                    service_areas__postcode=primary_address.postcode,
                    service_areas__is_active=True,
                ).distinct()

        featured_services = base_queryset.filter(is_featured=True)[: limit // 2]

        remaining_limit = limit - len(featured_services)
        if remaining_limit > 0:
            other_services = base_queryset.exclude(
                id__in=[s.id for s in featured_services]
            ).order_by("display_order", "name")[:remaining_limit]

            return list(featured_services) + list(other_services)

        return list(featured_services)

    except Exception as e:
        logger.error(f"Error getting service recommendations: {str(e)}")
        return []


def calculate_service_metrics(service: Service) -> Dict[str, Any]:
    try:
        metrics = {
            "service_id": service.id,
            "service_name": service.name,
            "is_active": service.is_active,
            "is_featured": service.is_featured,
            "is_ndis_eligible": service.is_ndis_eligible,
            "requires_quote": service.requires_quote,
            "base_price": float(service.base_price),
            "estimated_duration": service.estimated_duration,
            "service_areas_count": service.service_areas.filter(is_active=True).count(),
            "addons_count": service.addons.filter(is_active=True).count(),
            "availability_slots": service.availability.filter(
                is_available=True
            ).count(),
            "pricing_tiers": service.pricing_tiers.filter(is_active=True).count(),
        }

        return metrics

    except Exception as e:
        logger.error(f"Error calculating service metrics: {str(e)}")
        return {}


def format_service_price(service: Service, tier: str = "standard") -> str:
    try:
        pricing = (
            service.pricing_tiers.filter(
                tier=tier, is_active=True, effective_from__lte=timezone.now().date()
            )
            .filter(
                Q(effective_to__isnull=True)
                | Q(effective_to__gte=timezone.now().date())
            )
            .first()
        )

        if pricing:
            price = pricing.price
        else:
            price = service.base_price

        if service.pricing_type == "fixed":
            return f"${price:.2f}"
        elif service.pricing_type == "hourly":
            return f"${price:.2f}/hour"
        elif service.pricing_type == "per_room":
            return f"${price:.2f}/room"
        elif service.pricing_type == "per_sqm":
            return f"${price:.2f}/sqm"
        elif service.pricing_type == "ndis_rate":
            return f"NDIS Rate: ${price:.2f}"

        return f"${price:.2f}"

    except Exception as e:
        logger.error(f"Error formatting service price: {str(e)}")
        return "Price on request"


def get_service_availability_summary(service: Service) -> Dict[str, Any]:
    try:
        availability = service.availability.filter(is_available=True)

        days_available = []
        for day_num in range(7):
            day_slots = availability.filter(day_of_week=day_num)
            if day_slots.exists():
                day_name = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ][day_num]
                earliest = day_slots.order_by("start_time").first().start_time
                latest = day_slots.order_by("-end_time").first().end_time

                days_available.append(
                    {
                        "day": day_name,
                        "day_number": day_num,
                        "earliest_time": earliest.strftime("%H:%M"),
                        "latest_time": latest.strftime("%H:%M"),
                        "slots_count": day_slots.count(),
                    }
                )

        return {
            "service_id": service.id,
            "total_availability_slots": availability.count(),
            "days_available": days_available,
            "is_available_today": availability.filter(
                day_of_week=timezone.now().weekday()
            ).exists(),
        }

    except Exception as e:
        logger.error(f"Error getting service availability summary: {str(e)}")
        return {}

def generate_service_slug(name: str, service_id: Optional[int] = None) -> str:
    try:
        import re
        from django.utils.text import slugify
        
        base_slug = slugify(name.lower())
        
        if not base_slug:
            base_slug = 'service'
        
        base_slug = re.sub(r'[^a-z0-9\-]', '', base_slug)
        base_slug = re.sub(r'-+', '-', base_slug)
        base_slug = base_slug.strip('-')
        
        if len(base_slug) < 3:
            base_slug = f"service-{base_slug}"
        
        queryset = Service.objects.filter(slug=base_slug)
        if service_id:
            queryset = queryset.exclude(id=service_id)
        
        if not queryset.exists():
            return base_slug
        
        counter = 1
        while True:
            new_slug = f"{base_slug}-{counter}"
            if not Service.objects.filter(slug=new_slug).exclude(id=service_id if service_id else 0).exists():
                return new_slug
            counter += 1
            
    except Exception as e:
        logger.error(f"Error generating service slug: {str(e)}")
        return f"service-{timezone.now().timestamp()}"


def bulk_update_service_prices(service_ids: List[int], price_adjustment: Decimal, adjustment_type: str = 'percentage') -> Dict[str, Any]:
    try:
        services = Service.objects.filter(id__in=service_ids, is_active=True)
        updated_count = 0
        errors = []
        
        for service in services:
            try:
                if adjustment_type == 'percentage':
                    new_price = service.base_price * (1 + price_adjustment / 100)
                elif adjustment_type == 'fixed':
                    new_price = service.base_price + price_adjustment
                else:
                    errors.append(f"Invalid adjustment type for service {service.id}")
                    continue
                
                if new_price < Decimal('0.01'):
                    errors.append(f"Price too low for service {service.id}")
                    continue
                
                service.base_price = new_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                service.save()
                updated_count += 1
                
            except Exception as e:
                errors.append(f"Error updating service {service.id}: {str(e)}")
        
        return {
            'updated_count': updated_count,
            'total_services': len(service_ids),
            'errors': errors,
            'success': updated_count > 0
        }
        
    except Exception as e:
        logger.error(f"Error in bulk price update: {str(e)}")
        return {
            'updated_count': 0,
            'total_services': len(service_ids),
            'errors': [str(e)],
            'success': False
        }


def export_service_data(service_ids: Optional[List[int]] = None) -> Dict[str, Any]:
    try:
        if service_ids:
            services = Service.objects.filter(id__in=service_ids)
        else:
            services = Service.objects.all()
        
        export_data = []
        for service in services:
            service_data = {
                'id': service.id,
                'name': service.name,
                'slug': service.slug,
                'category': service.category.name,
                'service_type': service.service_type,
                'description': service.description,
                'pricing_type': service.pricing_type,
                'base_price': float(service.base_price),
                'hourly_rate': float(service.hourly_rate) if service.hourly_rate else None,
                'minimum_charge': float(service.minimum_charge),
                'estimated_duration': service.estimated_duration,
                'duration_unit': service.duration_unit,
                'is_active': service.is_active,
                'is_featured': service.is_featured,
                'is_ndis_eligible': service.is_ndis_eligible,
                'requires_quote': service.requires_quote,
                'minimum_rooms': service.minimum_rooms,
                'maximum_rooms': service.maximum_rooms,
                'service_areas': [area.full_location for area in service.service_areas.all()],
                'addons': [addon.name for addon in service.addons.filter(is_active=True)],
                'created_at': service.created_at.isoformat(),
                'updated_at': service.updated_at.isoformat()
            }
            export_data.append(service_data)
        
        return {
            'services': export_data,
            'total_count': len(export_data),
            'export_timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error exporting service data: {str(e)}")
        return {
            'services': [],
            'total_count': 0,
            'export_timestamp': timezone.now().isoformat(),
            'error': str(e)
        }


def validate_service_area_coverage(service: Service) -> Dict[str, Any]:
    try:
        total_areas = service.service_areas.count()
        active_areas = service.service_areas.filter(is_active=True).count()
        
        states_covered = service.service_areas.filter(is_active=True).values_list('state', flat=True).distinct()
        
        high_priority_areas = service.service_areas.filter(
            is_active=True,
            priority_level__gte=4
        ).count()
        
        coverage_analysis = {
            'service_id': service.id,
            'service_name': service.name,
            'total_areas': total_areas,
            'active_areas': active_areas,
            'inactive_areas': total_areas - active_areas,
            'states_covered': list(states_covered),
            'states_count': len(states_covered),
            'high_priority_areas': high_priority_areas,
            'coverage_percentage': (active_areas / total_areas * 100) if total_areas > 0 else 0,
            'recommendations': []
        }
        
        if active_areas == 0:
            coverage_analysis['recommendations'].append("No active service areas - service cannot be booked")
        elif active_areas < 5:
            coverage_analysis['recommendations'].append("Limited service area coverage - consider expanding")
        
        if high_priority_areas == 0:
            coverage_analysis['recommendations'].append("No high-priority areas - consider marking key areas as high priority")
        
        return coverage_analysis
        
    except Exception as e:
        logger.error(f"Error validating service area coverage: {str(e)}")
        return {}


def get_service_competition_analysis(service: Service) -> Dict[str, Any]:
    try:
        similar_services = Service.objects.filter(
            category=service.category,
            service_type=service.service_type,
            is_active=True
        ).exclude(id=service.id)
        
        price_comparison = similar_services.aggregate(
            avg_price=Avg('base_price'),
            min_price=Min('base_price'),
            max_price=Max('base_price'),
            count=Count('id')
        )
        
        service_position = 'unknown'
        if price_comparison['avg_price']:
            if service.base_price < price_comparison['avg_price']:
                service_position = 'below_average'
            elif service.base_price > price_comparison['avg_price']:
                service_position = 'above_average'
            else:
                service_position = 'average'
        
        analysis = {
            'service_id': service.id,
            'service_name': service.name,
            'service_price': float(service.base_price),
            'competitors_count': price_comparison['count'],
            'market_avg_price': float(price_comparison['avg_price']) if price_comparison['avg_price'] else 0,
            'market_min_price': float(price_comparison['min_price']) if price_comparison['min_price'] else 0,
            'market_max_price': float(price_comparison['max_price']) if price_comparison['max_price'] else 0,
            'price_position': service_position,
            'competitive_advantages': [],
            'improvement_suggestions': []
        }
        
        if service.is_featured and similar_services.filter(is_featured=True).count() < 3:
            analysis['competitive_advantages'].append("Featured service with limited competition")
        
        if service.is_ndis_eligible and similar_services.filter(is_ndis_eligible=True).count() < 5:
            analysis['competitive_advantages'].append("NDIS eligible with limited NDIS competition")
        
        if service_position == 'above_average':
            analysis['improvement_suggestions'].append("Consider price adjustment to be more competitive")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in competition analysis: {str(e)}")
        return {}


def calculate_service_profitability(service: Service, cost_per_hour: Decimal = Decimal('25.00')) -> Dict[str, Any]:
    try:
        if service.pricing_type == 'hourly':
            revenue_per_hour = service.hourly_rate or service.base_price
            profit_per_hour = revenue_per_hour - cost_per_hour
            profit_margin = (profit_per_hour / revenue_per_hour * 100) if revenue_per_hour > 0 else 0
        else:
            estimated_hours = Decimal(service.estimated_duration) / 60 if service.duration_unit == 'minutes' else Decimal(service.estimated_duration)
            total_cost = cost_per_hour * estimated_hours
            profit = service.base_price - total_cost
            profit_margin = (profit / service.base_price * 100) if service.base_price > 0 else 0
        
        profitability = {
            'service_id': service.id,
            'service_name': service.name,
            'base_price': float(service.base_price),
            'estimated_cost': float(total_cost if 'total_cost' in locals() else cost_per_hour),
            'estimated_profit': float(profit if 'profit' in locals() else profit_per_hour),
            'profit_margin_percentage': float(profit_margin),
            'profitability_rating': 'high' if profit_margin > 30 else 'medium' if profit_margin > 15 else 'low',
            'recommendations': []
        }
        
        if profit_margin < 15:
            profitability['recommendations'].append("Low profit margin - consider price increase or cost reduction")
        elif profit_margin > 50:
            profitability['recommendations'].append("High profit margin - opportunity for competitive pricing")
        
        return profitability
        
    except Exception as e:
        logger.error(f"Error calculating service profitability: {str(e)}")
        return {}


def optimize_service_display_order(category_id: Optional[int] = None) -> Dict[str, Any]:
    try:
        if category_id:
            services = Service.objects.filter(category_id=category_id, is_active=True)
        else:
            services = Service.objects.filter(is_active=True)
        
        featured_services = services.filter(is_featured=True).order_by('name')
        regular_services = services.filter(is_featured=False).order_by('name')
        
        display_order = 1
        updated_count = 0
        
        for service in featured_services:
            if service.display_order != display_order:
                service.display_order = display_order
                service.save(update_fields=['display_order'])
                updated_count += 1
            display_order += 1
        
        for service in regular_services:
            if service.display_order != display_order:
                service.display_order = display_order
                service.save(update_fields=['display_order'])
                updated_count += 1
            display_order += 1
        
        return {
            'updated_count': updated_count,
            'total_services': services.count(),
            'featured_services': featured_services.count(),
            'regular_services': regular_services.count(),
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error optimizing service display order: {str(e)}")
        return {
            'updated_count': 0,
            'total_services': 0,
            'success': False,
            'error': str(e)
        }


def generate_service_report(service_ids: Optional[List[int]] = None) -> Dict[str, Any]:
    try:
        if service_ids:
            services = Service.objects.filter(id__in=service_ids)
        else:
            services = Service.objects.all()
        
        total_services = services.count()
        active_services = services.filter(is_active=True).count()
        featured_services = services.filter(is_featured=True).count()
        ndis_services = services.filter(is_ndis_eligible=True).count()
        quote_required_services = services.filter(requires_quote=True).count()
        
        pricing_stats = services.aggregate(
            avg_price=Avg('base_price'),
            min_price=Min('base_price'),
            max_price=Max('base_price')
        )
        
        service_types = services.values('service_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        categories = services.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        report = {
            'report_generated_at': timezone.now().isoformat(),
            'summary': {
                'total_services': total_services,
                'active_services': active_services,
                'inactive_services': total_services - active_services,
                'featured_services': featured_services,
                'ndis_services': ndis_services,
                'quote_required_services': quote_required_services,
                'instant_booking_services': total_services - quote_required_services
            },
            'pricing_analysis': {
                'average_price': float(pricing_stats['avg_price']) if pricing_stats['avg_price'] else 0,
                'minimum_price': float(pricing_stats['min_price']) if pricing_stats['min_price'] else 0,
                'maximum_price': float(pricing_stats['max_price']) if pricing_stats['max_price'] else 0
            },
            'service_types_breakdown': list(service_types),
            'categories_breakdown': list(categories),
            'recommendations': []
        }
        
        if active_services < total_services * 0.8:
            report['recommendations'].append("High number of inactive services - review and activate or remove")
        
        if featured_services < 5:
            report['recommendations'].append("Consider featuring more services to improve visibility")
        
        if ndis_services < total_services * 0.3:
            report['recommendations'].append("Consider expanding NDIS service offerings")
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating service report: {str(e)}")
        return {
            'report_generated_at': timezone.now().isoformat(),
            'error': str(e)
        }


def cleanup_inactive_services(days_inactive: int = 90) -> Dict[str, Any]:
    try:
        cutoff_date = timezone.now() - timedelta(days=days_inactive)
        
        inactive_services = Service.objects.filter(
            is_active=False,
            updated_at__lt=cutoff_date
        )
        
        services_to_cleanup = []
        for service in inactive_services:
            if not hasattr(service, 'bookings') or service.bookings.count() == 0:
                services_to_cleanup.append({
                    'id': service.id,
                    'name': service.name,
                    'last_updated': service.updated_at.isoformat()
                })
        
        cleanup_count = len(services_to_cleanup)
        
        return {
            'cleanup_candidates': services_to_cleanup,
            'cleanup_count': cleanup_count,
            'cutoff_date': cutoff_date.isoformat(),
            'recommendation': f"Consider removing {cleanup_count} inactive services with no bookings"
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup analysis: {str(e)}")
        return {
            'cleanup_candidates': [],
            'cleanup_count': 0,
            'error': str(e)
        }

