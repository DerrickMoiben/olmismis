from rest_framework import serializers
from dashboard.models import Farmer, CherryWeight, MbuniWeight
from django.db import models

"""I want to have serializer that will give me the top 10 farmers as per the weight on cherry and mbiuni"""
class TopFarmerSerializer(serializers.ModelSerializer):
    cherry_weight = serializers.SerializerMethodField()
    mbuni_weight = serializers.SerializerMethodField()

    class Meta:
        model = Farmer
        fields = ['name', 'cherry_weight', 'mbuni_weight']

    def get_cherry_weight(self, obj):
        cherry_weight = CherryWeight.objects.filter(field__farmer=obj).aggregate(total_weight=models.Sum('weight'))
        return cherry_weight['total_weight'] or 0
    
    def get_mbuni_weight(self, obj):
        mbuni_weight = MbuniWeight.objects.filter(field__farmer=obj).aggregate(total_weight=models.Sum('weight'))
        return mbuni_weight['total_weight'] or 0

        