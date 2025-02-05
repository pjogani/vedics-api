from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .conversation_manager import ConversationManager

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle a user's chat message. 
        Request data must include:
          - session_id: string
          - message: user's text
        """
        session_id = request.data.get("session_id")
        user_input = request.data.get("message")
        if not session_id or not user_input:
            return Response({"error": "session_id and message are required"}, status=400)

        manager = ConversationManager(request.user)
        result = manager.chat(session_id, user_input)
        return Response({"reply": result["reply"]}, status=status.HTTP_200_OK)
