from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Añadir claims personalizados
        token['username'] = user.username
        # Puedes añadir más campos aquí

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Añadir información adicional a la respuesta
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        # Puedes añadir más campos aquí

        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer