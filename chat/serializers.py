from rest_framework import serializers
from .models import Conversation, Message
from users.serializers import UserMiniSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_name', 'content', 'is_read', 'created_at', 'is_me']
        read_only_fields = ['sender', 'is_read', 'is_me']

    def get_is_me(self, obj):
        request = self.context.get('request')
        if request:
            return obj.sender == request.user
        return False

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserMiniSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    topic_display = serializers.CharField(source='get_topic_display', read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'topic', 'topic_display', 'related_property', 'created_at', 'updated_at', 'last_message']

    from drf_spectacular.utils import extend_schema_field

    @extend_schema_field(MessageSerializer)
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None
