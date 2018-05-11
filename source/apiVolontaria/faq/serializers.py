from rest_framework import serializers

from . import models


class FaqCategorySerializer(serializers.ModelSerializer):
    faqs = serializers.RelatedField(many=True, read_only=True)

    class Meta:
        model = models.FaqCategory

        read_only_fields = [
            'id',
            'title',
            'faqs',
        ]

        fields = read_only_fields

    def to_representation(self, instance):
        data = dict()
        data['id'] = instance.id
        data['title'] = instance.title
        data['faqs'] = list()
        for faq in instance.faqs.all():
            data['faqs'].append(
                FaqSerializer(
                    faq
                ).to_representation(faq)
            )
        return data


class FaqSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Faq

        read_only_fields = [
            'id',
            'title',
            'content',
        ]

        fields = read_only_fields
