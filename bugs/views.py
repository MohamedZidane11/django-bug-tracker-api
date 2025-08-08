from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import BugReport
from .serializers import BugReportSerializer, BugStatsSerializer
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({"status": "ok", "message": "Bug tracker API is running"})

@api_view(['GET', 'POST'])
def bug_list(request):
    """
    GET: List all bugs
    POST: Create a new bug
    """
    if request.method == 'GET':
        bugs = BugReport.get_all()
        serializer = BugReportSerializer(bugs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BugReportSerializer(data=request.data)
        if serializer.is_valid():
            bug = serializer.save()
            return Response(BugReportSerializer(bug).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'DELETE'])
def bug_detail(request, bug_id):
    """
    PATCH: Update a bug
    DELETE: Delete a bug
    """
    try:
        bug = BugReport.get_by_id(bug_id)
        if not bug:
            return Response({'error': 'Bug not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == 'PATCH':
        serializer = BugReportSerializer(bug, data=request.data, partial=True)
        if serializer.is_valid():
            updated_bug = serializer.save()
            return Response(BugReportSerializer(updated_bug).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            bug.delete()
            return Response({'message': 'Bug deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def bug_stats(request):
    """
    GET: Get bug statistics
    """
    try:
        stats = BugReport.get_statistics()
        serializer = BugStatsSerializer(stats)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


