from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status  
from summary.models import DistrictMapping, DataSource, Master, Registration
from users.models import User
import pandas as pd
from datetime import datetime
import math
from django.db import transaction
from django.db.models import F

# SuperAdmin- New Leads
class GetDistrict(APIView):
    def get(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }
        
        district_names = DistrictMapping.objects.values_list('district_name', flat=True).distinct()
        if district_names:
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = list(district_names)
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
    
class GetBlock(APIView):
    def post(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }
        
        district = request.data.get('district')  # Get the 'district' from request data
        if not district:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        block_names = DistrictMapping.objects.filter(district_name=district).values_list('block_name', flat=True).distinct()
        if block_names:
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = list(block_names)
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
class GetDataSource(APIView):
    def get(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }
        
        data_source_names = DataSource.objects.values_list('source_name', flat=True).distinct()
        if data_source_names:
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = list(data_source_names)
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
class UploadNewLeads(APIView):
    def post (self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }
        
        file = request.data['file']
        if not file:
            return Response("File link is missing.", status=status.HTTP_400_BAD_REQUEST)

        content_type = file.content_type.lower()  
        
        if content_type in ['csv', 'text/csv']:  # Handle both 'csv' and 'text/csv'
            print("Reading CSV file...")
            df = pd.read_csv(file)
            print("CSV file successfully read.")
        elif content_type in ['xls', 'xlsx']:
            print("Reading Excel file...")
            df = pd.read_excel(file)
            print("Excel file successfully read.")
        else:
            return Response(f"Unsupported file format = '{content_type}'", status=status.HTTP_400_BAD_REQUEST)

        try: 
            data_list = []
            for _, row in df.iterrows():
                d = {field: row[field] for field in [
                    'uid', 'master_source', 'sub_source_name', 'source_contact_no', 'political_category', 'name', 'contact_number', 'age', 'gender',
                    'religion', 'category', 'caste', 'district', 'assembly', 'block_ulb', 'panchayat_ward', 'village_habitation', 'occupation', 'profile',
                    'whatsapp_user', 'whatsapp_number', 'rural_urban'
                ]}
                data_list.append(Master(**d))
            Master.objects.bulk_create(data_list)
            
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data Uploaded successfully"
            return Response(result, status=status.HTTP_200_OK)

        except UnicodeDecodeError as e:
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = str(e)
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as error:
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = str(error)
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
            
class TotalLeadUnassigned (APIView):
    def get(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }

        ids_with_new_record_status_zero = Master.objects.filter(new_record_status=0).count()
        if ids_with_new_record_status_zero:
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = ids_with_new_record_status_zero
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
class TotalLeadAssignd(APIView):
    def post(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found"
            }
        }
        data = request.data.get('leads')
        get_district = request.data["district"]
        get_block = request.data["block"]
        get_source = request.data["source"]
        
        if not data:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        ids_with_new_record_status_zero = Master.objects.filter(new_record_status=0).values_list('id', flat=True)[:int(data)]
        # if ()
        registrations_created = []
        for lead_uid in ids_with_new_record_status_zero:
            try:
                master = Master.objects.get(id=lead_uid)
                registration = Registration.objects.create(master=master)
                registrations_created.append(registration)
                
                master.new_record_status = 1
                registration.lau_admin_id = '3'
                registration.lau_created_date = datetime.now() 
                registration.save()
                master.save()
            except Master.DoesNotExist:
                pass
        
        
        result['status'] = "OK"
        result['valid'] = True
        result['result']['message'] = "Registrations created and new_record_status updated successfully"
        result['result']['data'] = registration.lau_created_date, registration.lau_admin_id, [reg.id for reg in registrations_created]
        
        # result['result']['message'] = ids_with_new_record_status_zero
        # result['result']['data'] = [reg.id for reg in registrations_created]
        return Response(result, status=status.HTTP_200_OK)
    
# LAU Admin - Assign new Leads 
class LAU_Agents(APIView):
    def get(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }
        
        agents = User.objects.filter(user_role=3, current_status=1).values()
        if len(agents) == 0:
            result['result']['message'] = "Agents aren't available"
        
        result['status'] = "OK"
        result['valid'] = True
        result['result']['message'] = "Data Fetched Successfully"
        result['result']['data'] = agents
        return Response(result, status=status.HTTP_200_OK)
    

class TotalLeadsUnassignedbyLAUAdmin(APIView):
    def post ():
        pass    
    
class TaskDistributionAPIView(APIView):
    def post(self, request, format=None):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }
        try:
            tasks_count = int(request.data.get('tasks_count', 0))
            member_ids = request.data.get('member_ids', {})
            if tasks_count <= 0 or not member_ids:
                return Response({'error': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)

            total_number_of_members = len(member_ids)
            tasks_per_member = math.floor(tasks_count / total_number_of_members)
            remaining_tasks = tasks_count % total_number_of_members

            distribution_result = {}
            for id in member_ids:
                member_tasks = tasks_per_member
                if remaining_tasks > 0:
                    member_tasks += 1
                    remaining_tasks -= 1

                distribution_result[id] = member_tasks
                        
            ids_to_update = list(Registration.objects.filter(lau_consent_agent_id = 0 , master__new_record_status=1)[:tasks_count])
            print((ids_to_update))

            i=0
            for temp in range(0, tasks_count):
                    for ids in member_ids:
                        for task in range(0,distribution_result[ids]):
                            # print(ids)
                            Registration.objects.filter(id = ids_to_update[i].id).update(lau_consent_agent_id=ids)
                            print(ids)
            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data Fetched Successfully"
            result['result']['data'] = distribution_result
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        

