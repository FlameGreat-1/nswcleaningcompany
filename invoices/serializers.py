from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Invoice, InvoiceItem
from accounts.serializers import UserSerializer
from quotes.serializers import QuoteSerializer

User = get_user_model()


class InvoiceItemSerializer(serializers.ModelSerializer):
    gst_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_with_gst = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = InvoiceItem
        fields = [
            "id",
            "description",
            "quantity",
            "unit_price",
            "total_price",
            "is_taxable",
            "gst_amount",
            "total_with_gst",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_price", "created_at", "updated_at"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price cannot be negative")
        return value


class InvoiceSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    quote = QuoteSerializer(read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    client_id = serializers.UUIDField(write_only=True)
    quote_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    client_full_name = serializers.ReadOnlyField()
    balance_due = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)

    pdf_url = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "client",
            "client_id",
            "quote",
            "quote_id",
            "status",
            "status_display",
            "invoice_date",
            "due_date",
            "billing_address",
            "service_address",
            "is_ndis_invoice",
            "participant_name",
            "ndis_number",
            "service_start_date",
            "service_end_date",
            "subtotal",
            "gst_amount",
            "total_amount",
            "balance_due",
            "payment_terms",
            "notes",
            "pdf_file",
            "pdf_url",
            "email_sent",
            "email_sent_at",
            "is_overdue",
            "days_overdue",
            "client_full_name",
            "items",
            "created_at",
            "updated_at",
            "created_by",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "subtotal",
            "gst_amount",
            "total_amount",
            "pdf_file",
            "email_sent",
            "email_sent_at",
            "created_at",
            "updated_at",
        ]

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
        return None

    def validate_client_id(self, value):
        try:
            client = User.objects.get(id=value)
            if not client.is_client:
                raise serializers.ValidationError("Selected user is not a client")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Client does not exist")

    def validate_quote_id(self, value):
        if value:
            from quotes.models import Quote

            try:
                quote = Quote.objects.get(id=value)
                if quote.status != "approved":
                    raise serializers.ValidationError(
                        "Quote must be approved to create invoice"
                    )
                return value
            except Quote.DoesNotExist:
                raise serializers.ValidationError("Quote does not exist")
        return value

    def validate(self, attrs):
        if attrs.get("service_start_date") and attrs.get("service_end_date"):
            if attrs["service_start_date"] > attrs["service_end_date"]:
                raise serializers.ValidationError(
                    {"service_end_date": "Service end date must be after start date"}
                )

        if attrs.get("is_ndis_invoice"):
            if not attrs.get("participant_name"):
                raise serializers.ValidationError(
                    {
                        "participant_name": "Participant name is required for NDIS invoices"
                    }
                )
            if not attrs.get("ndis_number"):
                raise serializers.ValidationError(
                    {"ndis_number": "NDIS number is required for NDIS invoices"}
                )

        return attrs

    def create(self, validated_data):
        client_id = validated_data.pop("client_id")
        quote_id = validated_data.pop("quote_id", None)

        client = User.objects.get(id=client_id)
        quote = None

        if quote_id:
            from quotes.models import Quote

            quote = Quote.objects.get(id=quote_id)

        invoice = Invoice.objects.create(
            client=client,
            quote=quote,
            created_by=self.context["request"].user,
            **validated_data
        )

        return invoice


class InvoiceCreateFromQuoteSerializer(serializers.Serializer):
    quote_id = serializers.UUIDField()

    def validate_quote_id(self, value):
        from quotes.models import Quote

        try:
            quote = Quote.objects.get(id=value)
            if quote.status != "approved":
                raise serializers.ValidationError(
                    "Quote must be approved to create invoice"
                )
            if hasattr(quote, "invoice"):
                raise serializers.ValidationError(
                    "Invoice already exists for this quote"
                )
            return value
        except Quote.DoesNotExist:
            raise serializers.ValidationError("Quote does not exist")

    def create(self, validated_data):
        from quotes.models import Quote

        quote = Quote.objects.get(id=validated_data["quote_id"])

        invoice = Invoice.create_from_quote(
            quote=quote, created_by=self.context["request"].user
        )

        return invoice


class InvoiceListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.full_name", read_only=True)
    client_email = serializers.CharField(source="client.email", read_only=True)
    client_full_name = serializers.ReadOnlyField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    balance_due = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    items_count = serializers.SerializerMethodField()
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "client_name",
            "client_email",
            "client_full_name",
            "status",
            "status_display",
            "invoice_date",
            "due_date",
            "total_amount",
            "subtotal",
            "gst_amount",
            "balance_due",
            "is_ndis_invoice",
            "participant_name",
            "ndis_number",
            "service_start_date",
            "service_end_date",
            "billing_address",
            "service_address",
            "email_sent",
            "is_overdue",
            "days_overdue",
            "items_count",
            "items",
            "pdf_file",
            "created_at",
        ]

    def get_items_count(self, obj):
        return obj.items.count()


class InvoiceActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=["generate_pdf", "send_email", "mark_as_sent"]
    )

    def validate_action(self, value):
        invoice = self.context.get("invoice")

        if value == "mark_as_sent" and invoice.status != "draft":
            raise serializers.ValidationError("Can only mark draft invoices as sent")

        if value == "send_email" and not invoice.client.email:
            raise serializers.ValidationError(
                "Client email is required to send invoice"
            )

        return value


class NDISInvoiceSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.full_name", read_only=True)
    client_full_name = serializers.ReadOnlyField()
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "client_name",
            "client_full_name",
            "participant_name",
            "ndis_number",
            "service_start_date",
            "service_end_date",
            "subtotal",
            "gst_amount",
            "total_amount",
            "items",
            "invoice_date",
            "due_date",
        ]
class ClientInvoiceListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.full_name", read_only=True)
    client_email = serializers.CharField(source="client.email", read_only=True)
    client_full_name = serializers.ReadOnlyField()
    balance_due = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    items_count = serializers.SerializerMethodField()
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "client_name",
            "client_email",
            "client_full_name",
            "invoice_date",
            "due_date",
            "total_amount",
            "subtotal",
            "gst_amount",
            "balance_due",
            "is_ndis_invoice",
            "participant_name",
            "ndis_number",
            "service_start_date",
            "service_end_date",
            "billing_address",
            "service_address",
            "is_overdue",
            "days_overdue",
            "items_count",
            "items",
            "pdf_file",
            "created_at",
        ]

    def get_items_count(self, obj):
        return obj.items.count()
