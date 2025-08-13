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
        try:
            bugs = BugReport.get_all()
            # Convert BugReport objects to dictionaries for serialization
            bugs_data = [bug.to_dict() for bug in bugs]

            # Add id field and map reporter to reporter_name for frontend compatibility
            for i, bug_data in enumerate(bugs_data):
                bug_data['id'] = bugs[i].bug_id
                bug_data['reporter_name'] = bug_data.get('reporter', '')

            return Response(bugs_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'POST':
        try:
            # Extract data from request
            title = request.data.get('title', '').strip()
            description = request.data.get('description', '').strip()
            severity = request.data.get('severity', 'medium')
            reporter = request.data.get('reporter', '').strip()

            # Validate required fields
            if not all([title, description, severity, reporter]):
                return Response({
                    'error': 'Missing required fields',
                    'required': ['title', 'description', 'severity', 'reporter']
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate severity
            if severity not in BugReport.SEVERITY_CHOICES:
                return Response({
                    'error': f'Invalid severity. Choose from: {BugReport.SEVERITY_CHOICES}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create bug report
            bug = BugReport(
                title=title,
                description=description,
                severity=severity,
                reporter=reporter,
                status='open'  # Default status
            )

            # Save to Firebase
            bug_id = bug.save()

            # Return the created bug data
            bug_data = bug.to_dict()
            bug_data['id'] = bug_id
            bug_data['reporter_name'] = bug.reporter

            return Response(bug_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PATCH', 'DELETE'])
def bug_detail(request, bug_id):
    """
    GET: Get a specific bug
    PATCH: Update a bug
    DELETE: Delete a bug
    """
    try:
        bug = BugReport.get_by_id(bug_id)
        if not bug:
            return Response({'error': 'Bug not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == 'GET':
        try:
            bug_data = bug.to_dict()
            bug_data['id'] = bug.bug_id
            bug_data['reporter_name'] = bug.reporter
            return Response(bug_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'PATCH':
        try:
            # Update only provided fields
            if 'title' in request.data:
                bug.title = request.data['title'].strip()
            if 'description' in request.data:
                bug.description = request.data['description'].strip()
            if 'severity' in request.data:
                severity = request.data['severity']
                if severity in BugReport.SEVERITY_CHOICES:
                    bug.severity = severity
                else:
                    return Response({
                        'error': f'Invalid severity. Choose from: {BugReport.SEVERITY_CHOICES}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            if 'status' in request.data:
                new_status = request.data['status']
                if new_status in BugReport.STATUS_CHOICES:
                    bug.status = new_status
                else:
                    return Response({
                        'error': f'Invalid status. Choose from: {BugReport.STATUS_CHOICES}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            if 'reporter' in request.data:
                bug.reporter = request.data['reporter'].strip()
            if 'assignee' in request.data:
                bug.assignee = request.data['assignee'].strip()

            # Save updated bug
            bug.save()

            # Return updated data
            bug_data = bug.to_dict()
            bug_data['id'] = bug.bug_id
            bug_data['reporter_name'] = bug.reporter

            return Response(bug_data)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'DELETE':
        try:
            success = bug.delete()
            if success:
                return Response({'message': 'Bug deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'Failed to delete bug'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def bug_stats(request):
    """
    GET: Get bug statistics
    """
    try:
        stats = BugReport.get_statistics()

        # Ensure the stats match what the frontend expects
        formatted_stats = {
            'total_bugs': stats.get('total_bugs', 0),
            'open_bugs': stats.get('open_bugs', 0),
            'closed_bugs': stats.get('closed_bugs', 0),
            'most_common_severity': stats.get('most_common_severity', 'medium'),
            'severity_distribution': stats.get('severity_distribution', {}),
            'status_distribution': stats.get('status_distribution', {})
        }

        return Response(formatted_stats)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)