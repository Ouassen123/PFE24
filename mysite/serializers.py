from rest_framework import serializers
from mysite.models import PostJob, UserProfile, Apply_job
from django.contrib.auth.models import User

class PostJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostJob
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
class CandidateSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    name = serializers.CharField()
    score = serializers.FloatField()