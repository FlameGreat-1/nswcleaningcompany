from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import Quote, QuoteItem, QuoteAttachment, QuoteRevision, QuoteTemplate
from .validators import (
    validate_quote_number,
    validate_urgency_level,
    validate_room_count,
    validate_square_meters,
    validate_postcode,
    validate_ndis_participant_number,
    validate_phone_number,
    validate_file_size,
    validate_image_file,
    validate_preferred_date,
    validate_preferred_time,
    validate_price_amount,
    QuoteValidator,
)
from services.serializers import ServiceSerializer, ServiceAddOnSerializer
from accounts.serializers import UserSerializer

User = get_user_model()


class QuoteItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    addon_name = serializers.CharField(source="addon.name", read_only=True)
    gst_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_with_gst = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = QuoteItem
        fields = [
            "id",
            "quote",
            "service",
            "addon",
            "item_type",
            "name",
            "description",
            "quantity",
            "unit_price",
            "total_price",
            "is_optional",
            "is_taxable",
            "display_order",
            "service_name",
            "addon_name",
            "gst_amount",
            "total_with_gst",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_price", "created_at", "updated_at"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_unit_price(self, value):
        validate_price_amount(value)
        return value


class QuoteAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.get_full_name", read_only=True
    )
    file_size_mb = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )
    is_image = serializers.BooleanField(read_only=True)

    class Meta:
        model = QuoteAttachment
        fields = [
            "id",
            "quote",
            "uploaded_by",
            "file",
            "original_filename",
            "file_size",
            "file_type",
            "attachment_type",
            "title",
            "description",
            "is_public",
            "display_order",
            "uploaded_by_name",
            "file_size_mb",
            "is_image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "uploaded_by",
            "original_filename",
            "file_size",
            "file_type",
            "created_at",
            "updated_at",
        ]

    def validate_file(self, value):
        validate_file_size(value)
        validate_image_file(value)
        return value


class QuoteRevisionSerializer(serializers.ModelSerializer):
    revised_by_name = serializers.CharField(
        source="revised_by.get_full_name", read_only=True
    )
    price_change = serializers.SerializerMethodField()
    price_change_percent = serializers.SerializerMethodField()

    class Meta:
        model = QuoteRevision
        fields = [
            "id",
            "quote",
            "revised_by",
            "revision_number",
            "changes_summary",
            "previous_price",
            "new_price",
            "reason",
            "revised_by_name",
            "price_change",
            "price_change_percent",
            "created_at",
        ]
        read_only_fields = ["id", "revised_by", "revision_number", "created_at"]

    def get_price_change(self, obj):
        return obj.new_price - obj.previous_price

    def get_price_change_percent(self, obj):
        if obj.previous_price > 0:
            return ((obj.new_price - obj.previous_price) / obj.previous_price) * 100
        return 0


class QuoteTemplateSerializer(serializers.ModelSerializer):
    default_service_name = serializers.CharField(
        source="default_service.name", read_only=True
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )

    class Meta:
        model = QuoteTemplate
        fields = [
            "id",
            "name",
            "description",
            "cleaning_type",
            "default_service",
            "default_urgency_level",
            "is_active",
            "is_ndis_template",
            "usage_count",
            "default_service_name",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "usage_count",
            "created_by",
            "created_at",
            "updated_at",
        ]


class QuoteListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.get_full_name", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)
    assigned_to_name = serializers.CharField(
        source="assigned_to.get_full_name", read_only=True
    )
    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    can_be_accepted = serializers.BooleanField(read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    attachments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quote
        fields = [
            "id",
            "quote_number",
            "client",
            "client_name",
            "service",
            "service_name",
            "cleaning_type",
            "status",
            "number_of_rooms",
            "urgency_level",
            "final_price",
            "is_ndis_client",
            "assigned_to",
            "assigned_to_name",
            "is_expired",
            "days_until_expiry",
            "can_be_accepted",
            "items_count",
            "attachments_count",
            "created_at",
            "updated_at",
            "expires_at",
        ]


class QuoteDetailSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    items = QuoteItemSerializer(many=True, read_only=True)
    attachments = QuoteAttachmentSerializer(many=True, read_only=True)
    revisions = QuoteRevisionSerializer(many=True, read_only=True)

    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    can_be_accepted = serializers.BooleanField(read_only=True)
    total_items_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Quote
        fields = [
            "id",
            "quote_number",
            "client",
            "service",
            "cleaning_type",
            "property_address",
            "postcode",
            "suburb",
            "state",
            "number_of_rooms",
            "square_meters",
            "urgency_level",
            "preferred_date",
            "preferred_time",
            "special_requirements",
            "access_instructions",
            "is_ndis_client",
            "ndis_participant_number",
            "plan_manager_name",
            "plan_manager_contact",
            "support_coordinator_name",
            "support_coordinator_contact",
            "estimated_total",
            "base_price",
            "extras_cost",
            "travel_cost",
            "urgency_surcharge",
            "discount_amount",
            "gst_amount",
            "final_price",
            "status",
            "assigned_to",
            "reviewed_by",
            "admin_notes",
            "client_notes",
            "rejection_reason",
            "source",
            "conversion_rate_applied",
            "is_expired",
            "days_until_expiry",
            "can_be_accepted",
            "total_items_cost",
            "items",
            "attachments",
            "revisions",
            "created_at",
            "updated_at",
            "submitted_at",
            "reviewed_at",
            "approved_at",
            "expires_at",
        ]


class QuoteCreateSerializer(serializers.ModelSerializer):
    items = QuoteItemSerializer(many=True, required=False)

    class Meta:
        model = Quote
        fields = [
            "service",
            "cleaning_type",
            "property_address",
            "postcode",
            "suburb",
            "state",
            "number_of_rooms",
            "square_meters",
            "urgency_level",
            "preferred_date",
            "preferred_time",
            "special_requirements",
            "access_instructions",
            "items",
        ]

    def validate_postcode(self, value):
        validate_postcode(value)
        return value

    def validate_number_of_rooms(self, value):
        validate_room_count(value)
        return value

    def validate_square_meters(self, value):
        validate_square_meters(value)
        return value

    def validate_urgency_level(self, value):
        validate_urgency_level(value)
        return value

    def validate_preferred_date(self, value):
        validate_preferred_date(value)
        return value

    def validate_preferred_time(self, value):
        validate_preferred_time(value)
        return value

    def validate(self, attrs):
        QuoteValidator.validate_quote_creation(attrs)
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        request = self.context.get("request")

        validated_data["client"] = request.user
        quote = Quote.objects.create(**validated_data)

        for item_data in items_data:
            QuoteItem.objects.create(quote=quote, **item_data)

        quote.update_pricing()
        return quote


class QuoteUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quote
        fields = [
            "cleaning_type",
            "property_address",
            "postcode",
            "suburb",
            "state",
            "number_of_rooms",
            "square_meters",
            "urgency_level",
            "preferred_date",
            "preferred_time",
            "special_requirements",
            "access_instructions",
        ]

    def validate_postcode(self, value):
        validate_postcode(value)
        return value

    def validate_number_of_rooms(self, value):
        validate_room_count(value)
        return value

    def validate_square_meters(self, value):
        validate_square_meters(value)
        return value

    def validate_urgency_level(self, value):
        validate_urgency_level(value)
        return value

    def validate_preferred_date(self, value):
        validate_preferred_date(value)
        return value

    def validate_preferred_time(self, value):
        validate_preferred_time(value)
        return value

    def validate(self, attrs):
        QuoteValidator.validate_quote_update(self.instance, attrs)
        return attrs

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        instance.update_pricing()
        return instance


class QuoteStatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quote
        fields = ["status", "admin_notes", "client_notes", "rejection_reason"]

    def validate(self, attrs):
        new_status = attrs.get("status")
        if new_status and new_status != self.instance.status:
            QuoteValidator.validate_quote_update(self.instance, {"status": new_status})
        return attrs


class QuoteCalculatorSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    cleaning_type = serializers.ChoiceField(choices=Quote.CLEANING_TYPE_CHOICES)
    number_of_rooms = serializers.IntegerField(min_value=1, max_value=50)
    square_meters = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False
    )
    urgency_level = serializers.IntegerField(min_value=1, max_value=5)
    postcode = serializers.CharField(max_length=4)
    addon_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )

    def validate_postcode(self, value):
        validate_postcode(value)
        return value

    def validate_service_id(self, value):
        from services.models import Service

        try:
            service = Service.objects.get(id=value, is_active=True)
            return value
        except Service.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive service.")

    def validate_addon_ids(self, value):
        if value:
            from services.models import ServiceAddOn

            valid_addons = ServiceAddOn.objects.filter(
                id__in=value, is_active=True
            ).count()
            if valid_addons != len(value):
                raise serializers.ValidationError(
                    "One or more add-ons are invalid or inactive."
                )
        return value


class QuoteAssignmentSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(
        source="assigned_to.get_full_name", read_only=True
    )

    class Meta:
        model = Quote
        fields = ["assigned_to", "assigned_to_name", "admin_notes"]

    def validate_assigned_to(self, value):
        if value and not value.is_staff:
            raise serializers.ValidationError(
                "Only staff members can be assigned to quotes."
            )
        if value and not value.is_active:
            raise serializers.ValidationError(
                "Cannot assign quote to inactive staff member."
            )
        return value


class QuoteApprovalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quote
        fields = ["admin_notes", "client_notes", "expires_at"]

    def validate_expires_at(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future.")
        return value


class QuoteRejectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quote
        fields = ["rejection_reason", "admin_notes"]

    def validate_rejection_reason(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Rejection reason is required.")
        return value


class QuoteDuplicateSerializer(serializers.Serializer):
    include_items = serializers.BooleanField(default=True)
    include_attachments = serializers.BooleanField(default=False)
    new_cleaning_type = serializers.ChoiceField(
        choices=Quote.CLEANING_TYPE_CHOICES, required=False
    )
    new_urgency_level = serializers.IntegerField(
        min_value=1, max_value=5, required=False
    )


class BulkQuoteOperationSerializer(serializers.Serializer):
    quote_ids = serializers.ListField(
        child=serializers.UUIDField(), min_length=1, max_length=100
    )
    operation = serializers.ChoiceField(
        choices=["approve", "reject", "cancel", "assign", "export"]
    )
    assigned_to = serializers.IntegerField(required=False)
    rejection_reason = serializers.CharField(max_length=1000, required=False)
    admin_notes = serializers.CharField(max_length=2000, required=False)

    def validate(self, attrs):
        operation = attrs.get("operation")

        if operation == "assign" and not attrs.get("assigned_to"):
            raise serializers.ValidationError(
                "assigned_to is required for assign operation."
            )

        if operation == "reject" and not attrs.get("rejection_reason"):
            raise serializers.ValidationError(
                "rejection_reason is required for reject operation."
            )

        if attrs.get("assigned_to"):
            try:
                user = User.objects.get(id=attrs["assigned_to"])
                if not user.is_staff or not user.is_active:
                    raise serializers.ValidationError(
                        "Invalid staff member for assignment."
                    )
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid user for assignment.")

        return attrs


class QuoteAnalyticsSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    group_by = serializers.ChoiceField(
        choices=["status", "cleaning_type", "urgency", "state", "month"],
        default="status",
    )
    include_ndis = serializers.BooleanField(default=True)
    include_general = serializers.BooleanField(default=True)

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("start_date cannot be after end_date.")

        return attrs


class QuoteReportSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(
        choices=["summary", "detailed", "analytics", "conversion"]
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    format = serializers.ChoiceField(choices=["pdf", "excel", "csv"], default="pdf")
    include_attachments = serializers.BooleanField(default=False)
    filter_status = serializers.MultipleChoiceField(
        choices=Quote.QUOTE_STATUS_CHOICES, required=False
    )
    filter_cleaning_type = serializers.MultipleChoiceField(
        choices=Quote.CLEANING_TYPE_CHOICES, required=False
    )

    def validate(self, attrs):
        if attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError("start_date cannot be after end_date.")
        return attrs


class QuoteExportSerializer(serializers.Serializer):
    quote_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    format = serializers.ChoiceField(choices=["csv", "excel", "pdf"], default="csv")
    include_items = serializers.BooleanField(default=True)
    include_attachments = serializers.BooleanField(default=False)
    date_range = serializers.CharField(required=False)
    status_filter = serializers.MultipleChoiceField(
        choices=Quote.QUOTE_STATUS_CHOICES, required=False
    )


class QuoteSearchSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=200, required=False)
    status = serializers.MultipleChoiceField(
        choices=Quote.QUOTE_STATUS_CHOICES, required=False
    )
    cleaning_type = serializers.MultipleChoiceField(
        choices=Quote.CLEANING_TYPE_CHOICES, required=False
    )
    urgency_level = serializers.MultipleChoiceField(
        choices=Quote.URGENCY_LEVEL_CHOICES, required=False
    )
    is_ndis_client = serializers.BooleanField(required=False)
    postcode = serializers.CharField(max_length=4, required=False)
    state = serializers.CharField(max_length=3, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    price_min = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    price_max = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    assigned_to = serializers.IntegerField(required=False)

    def validate_postcode(self, value):
        if value:
            validate_postcode(value)
        return value

    def validate(self, attrs):
        date_from = attrs.get("date_from")
        date_to = attrs.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("date_from cannot be after date_to.")

        price_min = attrs.get("price_min")
        price_max = attrs.get("price_max")

        if price_min and price_max and price_min > price_max:
            raise serializers.ValidationError(
                "price_min cannot be greater than price_max."
            )

        return attrs


class QuoteStatisticsSerializer(serializers.Serializer):
    total_quotes = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_count = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    rejected_count = serializers.IntegerField()
    expired_count = serializers.IntegerField()
    converted_count = serializers.IntegerField()
    ndis_count = serializers.IntegerField()
    urgent_count = serializers.IntegerField()
    high_value_count = serializers.IntegerField()
    with_attachments_count = serializers.IntegerField()
    approval_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    rejection_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class QuoteDashboardSerializer(serializers.Serializer):
    total_quotes = serializers.IntegerField()
    pending_quotes = serializers.IntegerField()
    approved_quotes = serializers.IntegerField()
    expired_quotes = serializers.IntegerField()
    quotes_this_week = serializers.IntegerField()
    quotes_this_month = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_quote_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    urgent_quotes = serializers.IntegerField()
    ndis_quotes = serializers.IntegerField()
    expiring_soon = serializers.IntegerField()


class QuoteCalculatorResponseSerializer(serializers.Serializer):
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    extras_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    travel_cost = serializers.DecimalField(max_digits=8, decimal_places=2)
    urgency_surcharge = serializers.DecimalField(max_digits=8, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    gst_amount = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quote_valid_until = serializers.DateTimeField()
    breakdown = serializers.DictField()
    recommendations = serializers.ListField(required=False)


class QuoteItemCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuoteItem
        fields = [
            "quote",
            "service",
            "addon",
            "item_type",
            "name",
            "description",
            "quantity",
            "unit_price",
            "is_optional",
            "is_taxable",
            "display_order",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_unit_price(self, value):
        validate_price_amount(value)
        return value

    def validate(self, attrs):
        quote = attrs.get("quote")
        if quote and quote.status not in ["draft", "submitted"]:
            raise serializers.ValidationError(
                "Cannot add items to quote with current status."
            )
        return attrs


class QuoteAttachmentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuoteAttachment
        fields = [
            "quote",
            "file",
            "attachment_type",
            "title",
            "description",
            "is_public",
            "display_order",
        ]

    def validate_file(self, value):
        validate_file_size(value)
        validate_image_file(value)
        return value

    def validate(self, attrs):
        quote = attrs.get("quote")
        if quote and quote.status not in ["draft", "submitted", "under_review"]:
            raise serializers.ValidationError(
                "Cannot upload attachments to quote with current status."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["uploaded_by"] = request.user
        return super().create(validated_data)


class QuoteRevisionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuoteRevision
        fields = ["quote", "changes_summary", "previous_price", "new_price", "reason"]

    def validate(self, attrs):
        quote = attrs.get("quote")
        if quote and quote.status not in ["submitted", "under_review", "approved"]:
            raise serializers.ValidationError(
                "Cannot create revision for quote with current status."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        quote = validated_data["quote"]

        last_revision = quote.revisions.order_by("-revision_number").first()
        revision_number = (last_revision.revision_number + 1) if last_revision else 1

        validated_data["revised_by"] = request.user
        validated_data["revision_number"] = revision_number

        return super().create(validated_data)


class QuoteTemplateCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuoteTemplate
        fields = [
            "name",
            "description",
            "cleaning_type",
            "default_service",
            "default_urgency_level",
            "is_active",
            "is_ndis_template",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["created_by"] = request.user
        return super().create(validated_data)


class QuoteConversionSerializer(serializers.Serializer):
    preferred_start_date = serializers.DateField(required=False)
    preferred_start_time = serializers.TimeField(required=False)
    additional_notes = serializers.CharField(max_length=1000, required=False)

    def validate_preferred_start_date(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Start date cannot be in the past.")
        return value


class QuoteNotificationSerializer(serializers.Serializer):
    quote_id = serializers.UUIDField()
    notification_type = serializers.ChoiceField(
        choices=["submitted", "approved", "rejected", "expired", "reminder"]
    )
    recipient_type = serializers.ChoiceField(choices=["client", "staff", "both"])
    custom_message = serializers.CharField(max_length=500, required=False)
