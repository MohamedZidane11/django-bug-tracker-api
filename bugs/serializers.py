from rest_framework import serializers
from .models import BugReport

class BugReportSerializer(serializers.Serializer):
    bug_id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    severity = serializers.ChoiceField(choices=BugReport.SEVERITY_CHOICES, default='medium')
    status = serializers.ChoiceField(choices=BugReport.STATUS_CHOICES, default='open')
    reporter = serializers.CharField(max_length=100, required=False, allow_blank=True)
    assignee = serializers.CharField(max_length=100, required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        bug = BugReport(**validated_data)
        bug.save()
        return bug

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class BugStatsSerializer(serializers.Serializer):
    total_bugs = serializers.IntegerField()
    open_bugs = serializers.IntegerField()
    closed_bugs = serializers.IntegerField()
    severity_distribution = serializers.DictField()
    status_distribution = serializers.DictField()
    most_common_severity = serializers.CharField()