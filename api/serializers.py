import re

from django.contrib.auth.models import User, Group
from rest_framework import serializers

from . import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class InteractionTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.InteractionType
        extra_kwargs = {'url': {'view_name': 'type-detail'}}
        fields = ('url', 'slug_name', 'long_name', 'interactions')


class BubbleSortSwapSerializer(serializers.HyperlinkedModelSerializer):
    def validate(self, data):
        if data['lower_index'] < 0 or data['lower_index'] >= data[
            'bubble_sort'].get_list_size:
            raise serializers.ValidationError(
                {'lower_index': 'Must be a valid index'})
        return data

    class Meta:
        model = models.BubbleSortSwap


class BubbleSortSerializer(serializers.HyperlinkedModelSerializer):
    list_size = serializers.IntegerField(source='get_list_size', read_only=True)
    sorted_list = serializers.CharField(source='get_list_sorted',
                                        read_only=True)
    current_list = serializers.ListField(source='get_list_current',
                                         read_only=True)
    swaps_lower_index = serializers.SlugRelatedField(many=True,
                                                     slug_field='lower_index',
                                                     source='swaps',
                                                     read_only=True)
    description = serializers.CharField(source='get_info', read_only=True)

    class Meta:
        model = models.BubbleSort


class GameOfLifeCellSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.GameOfLifeCell
        exclude = ('changed',)
        unique_together = ('game_of_life', 'cell_name')


class GameOfLifeSerializer(serializers.HyperlinkedModelSerializer):
    serialized = serializers.CharField(source='__unicode__', read_only=True)
    cells = serializers.HyperlinkedRelatedField(
        view_name='gameoflifecell-detail', read_only=True, many=True)
    description = serializers.CharField(source='get_info', read_only=True)

    class Meta:
        model = models.GameOfLife


class RegressionPlotPointSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RegressionPlotItem


class RegressionEstimateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RegressionEstimate


class RegressionSerializer(serializers.HyperlinkedModelSerializer):
    estimates = serializers.HyperlinkedRelatedField(
        view_name='regressionestimate-detail', read_only=True, many=True)
    plot_items = serializers.HyperlinkedRelatedField(
        view_name='regressionplotitem-detail', read_only=True, many=True)

    class Meta:
        model = models.Regression


class GraphParticipationRulesSerializer(serializers.HyperlinkedModelSerializer):
    interaction_type = InteractionTypeSerializer(read_only=True)
    creator = serializers.SlugRelatedField(slug_field='username',
                                           read_only=True,
                                           source='creator.user')

    class Meta:
        model = models.GraphParticipationRules
        extra_kwargs = {'url': {'view_name': 'graphrules-detail'}}


class GraphVertexSerializer(serializers.HyperlinkedModelSerializer):
    assigned_to = serializers.HyperlinkedRelatedField(
        view_name='connect-detail',
        queryset=models.RegisteredDevice.objects.all())

    def validate_label(self, label):
        matches = self.instance.graph.vertices.filter(label=label)

        actual = models.GraphVertex.objects.get(id=self.instance.id)

        if actual.label == label:
            raise serializers.ValidationError('No change')

        if len(matches) and matches[0].id != self.instance.id:
            raise serializers.ValidationError('This label already exists')
        return label

    class Meta:
        model = models.GraphVertex


class GraphEdgeSerializer(serializers.HyperlinkedModelSerializer):
    def validate(self, data):
        source = data['source']
        target = data['target']
        graph = data['graph']
        rules = graph.rules

        if rules.is_multi_graph:
            return

        matches = models.GraphEdge.objects.filter(graph=graph,
                                                  source=source,
                                                  target=target)

        rev_matches = models.GraphEdge.objects.filter(graph=graph,
                                                      source=target,
                                                      target=source)

        if len(matches) or (not rules.is_directed and len(rev_matches)):
            raise serializers.ValidationError('This edge already exists')

        #    raise serializers.ValidationError(
        #        {'target': 'Must be a valid index'})
        return data

    class Meta:
        model = models.GraphEdge


class GraphSerializer(serializers.HyperlinkedModelSerializer):
    rules = GraphParticipationRulesSerializer(read_only=True)
    vertices = GraphVertexSerializer(read_only=True, many=True)
    edges = GraphEdgeSerializer(read_only=True, many=True)

    class Meta:
        model = models.Graph



class InteractionGeneratorSerializer(serializers.HyperlinkedModelSerializer):
    class_name = serializers.SlugRelatedField(slug_field='class_name',
                                              source='clicker_class',
                                              queryset=models.ClickerClass.objects.all())

    _interaction_type = models.InteractionType.objects
    interaction_slug = serializers.SlugRelatedField(slug_field='slug_name',
                                                    source='interaction_type',
                                                    queryset=_interaction_type.all())

    class Meta:
        fields = ('class_name', 'interaction_slug')
        model = models.Interaction


class CreatorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = models.Creator


# noinspection PyAbstractClass
class CreatorNameSerializer(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, models.Creator):
            return value.user.username
        else:
            raise Exception('Unexpected type of related field')


class InteractionSerializer(serializers.HyperlinkedModelSerializer):
    clicker_class = serializers.HyperlinkedRelatedField(
        view_name='class-detail', read_only=True)
    bubblesort = BubbleSortSerializer(read_only=True)
    gameoflife = GameOfLifeSerializer(read_only=True)
    creator = CreatorNameSerializer(read_only=True)
    interaction_slug = serializers.SlugRelatedField(source='interaction_type',
                                                    slug_field='slug_name',
                                                    queryset=models.Interaction.objects.all())
    long_name = serializers.SlugRelatedField(source='interaction_type',
                                             slug_field='long_name',
                                             queryset=models.Interaction.objects.all())

    state_name = serializers.CharField(read_only=True)
    instance_url = serializers.URLField(read_only=True)

    class Meta:
        model = models.Interaction
        exclude = ('interaction_type',)
        extra_kwargs = {'url': {'view_name': 'interaction-detail'}}


# noinspection PyMethodMayBeStatic
class ClickerClassSerializer(serializers.HyperlinkedModelSerializer):
    connected_devices = serializers.IntegerField(source='get_connected_devices',
                                                 read_only=True)
    creator = CreatorNameSerializer(read_only=True)

    def validate_class_name(self, class_name):
        if not re.match(r"^[a-z\-_0-9]+$", class_name):
            raise serializers.ValidationError(
                'Must be all lower-case with hyphens or underscores.')
        return class_name

    class Meta:
        model = models.ClickerClass
        extra_kwargs = {'url': {'view_name': 'class-detail'}}


class ConnectionSerializer(serializers.HyperlinkedModelSerializer):
    classes = ClickerClassSerializer(many=True, read_only=True)
    classes_url = serializers.HyperlinkedRelatedField(source='pk',
                                                      view_name='connect-classes',
                                                      read_only=True)
    device_id = serializers.CharField(source='pk', read_only=True)

    class Meta:
        depth = 1
        read_only = ('device_id',)
        model = models.RegisteredDevice
        extra_kwargs = {'url': {'view_name': 'connect-detail', }}
