from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from api.models import CustomUser, Friendship, School
from api.serializers import UserSerializer, FriendshipSerializer, SchoolSerializer


class SearchViewSet(ModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields = {
        CustomUser: ["username", "email", "first_name", "last_name"],
        Friendship: ["user__username", "friend__username"],
        School: ["name", "address", "city", "state", "zip_code"],
    }

    def get_queryset(self):
        queryset = []
        for model, fields in self.search_fields.items():
            query = self.request.query_params.get("q", None)
            if query:
                for field in fields:
                    objects = model.objects.filter(**{field + "__icontains": query})
                    if objects is not None:
                        queryset += objects
        return queryset

    def get_serializer_class(self):
        for model in self.search_fields.keys():
            if model in self.search_fields:
                if model == CustomUser:
                    return UserSerializer
                elif model == Friendship:
                    return FriendshipSerializer
                elif model == School:
                    return SchoolSerializer

        return None
