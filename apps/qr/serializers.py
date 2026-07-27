from rest_framework import serializers


class EventSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        return dict(data)

    def to_representation(self, instance):
        return instance


class DisplayEventSerializer(serializers.Serializer):
    event_id = serializers.UUIDField(required=False)
    event_type = serializers.ChoiceField(
        choices=["DISPLAY_STARTED", "DISPLAY_ENDED", "FALLBACK_ACTIVATED"]
    )
    qr_mode = serializers.ChoiceField(choices=["GENERAL", "DYNAMIC"])
    fallback_reason = serializers.CharField(required=False, max_length=40)
