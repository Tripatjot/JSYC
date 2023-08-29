from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status  
from summary.models import Registration
from users.models import User
import pandas as pd
from datetime import datetime
import math
from django.db.models import F,Q
from django.core.exceptions import ObjectDoesNotExist

class ShowBasicInfo_AssignRTOLeadstoCOUAgent(APIView):
    def post(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }
        
        try:
            get_district = request.data.get('district')
            get_block = request.data.get('block')
            get_source = request.data.get('source')
            
            cou_id = User.objects.filter(user_role_id=7).values('id').first()  # Get the first id value
            if cou_id is not None:
                data = Registration.objects.all().filter(cou_admin_id=cou_id['id'])
                if get_district:
                    data = data.filter(master__district=get_district)
                if get_block:
                    data = data.filter(master__block_ulb=get_block)
                if get_source:
                    data = data.filter(master__master_source=get_source)

                print(data)
                
                result['status'] = "OK"
                result['valid'] = True
                result['result']['message'] = "Data retrieved successfully"
                result['result']['data'] = data.values()
                return Response(result, status=status.HTTP_200_OK)
            else:
                result['result']['message'] = "User with specified role not found"
                return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        except ObjectDoesNotExist:
            result['result']['message'] = "No data found"
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            result['result']['message'] = str(e)
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class COUAgentListing (APIView):
    def get(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }  
        
        data = User.objects.filter(user_role_id = 8, current_status= 1)
        result['status'] = "OK"
        result['valid'] = True
        result['result']['message'] = "Data retrieved successfully"
        result['result']['data'] = data.values('id','name')
            
        return Response(result, status=status.HTTP_200_OK)              

class AssignRTOLeadstoCOUAgent(APIView): 
    def post (self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        } 
        try:
            get_lead_ids_str = request.data.get('lead_ids')
            get_lead_ids = [int(lead_id) for lead_id in get_lead_ids_str.split(',')]
            
            get_agent_ids_str = request.data.get('agent_ids')
            get_agent_ids = [int(agent_id) for agent_id in get_agent_ids_str.split(',')]
            
            if len(get_agent_ids) > len(get_lead_ids) :
                result['result']['message'] = 'Agents are more than Leads provided.'
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            
            lead_count= len(get_lead_ids) 
            agent_count = len(get_agent_ids) 
            
            leads_per_member = math.floor(lead_count / agent_count)
            remaining_tasks = lead_count % agent_count
            
            distribution_result = {}
            for id in get_agent_ids:
                member_tasks = leads_per_member
                if remaining_tasks > 0:
                    member_tasks += 1
                    remaining_tasks -= 1
                distribution_result[id] = member_tasks
            
            updated_ids = []
            for agent_id in get_agent_ids:
                agent_id_to_assign = distribution_result[agent_id]
                temp = Registration.objects.filter(
                        id__in=get_lead_ids, 
                        cou_agent_id__isnull=True
                    ).order_by('id')[:agent_id_to_assign]

                temp_ids = list(temp.values_list('id', flat=True))
                Registration.objects.filter(id__in=temp_ids).update(cou_agent_id=agent_id)
                updated_ids.extend(temp_ids)
                
            # print(get_lead_ids)
            # print(get_agent_ids)
            data = Registration.objects.filter(id__in=get_lead_ids).values('id')

            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['distribution'] = distribution_result
            result['result']['ids'] = updated_ids
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            result['result']['message'] = "Invalid data format provided."
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            result['result']['message'] = "An error occurred while processing the request."
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
              
class ShowBasicInfo_COUAgent(APIView):
    def post(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }
        
        try:
            get_id = request.data.get('id')
            get_district = request.data.get('district')
            get_block = request.data.get('block')
            get_call_status = request.data.get('call_status')
            get_lead_status = request.data.get('lead_status')
            get_date = request.data.get('date')
            
            if not get_id:
                result['result']['message'] = "Missing 'id' parameter."
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            data = Registration.objects.all().filter(cou_agent_id=get_id).exclude(
                Q (cou_lead_status = "All Criteria Fulfilled"))
            
            if get_district:
                data = data.filter(master__district=get_district)
            if get_block:
                data = data.filter(master__block_ulb=get_block)
            if get_call_status:
                data = data.filter(cau_call_status=get_call_status)
            if get_lead_status:
                data = data.filter(cau_lead_status=get_lead_status)
            if get_date:
                data = data.filter(cau_followup_date_time=get_date)
            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['data'] = data.values(
                    'id', 'master__name', 'master__contact_number', 
                    'master__district', 'master__block_ulb', 'cou_call_status', 'cou_lead_status', 'cou_followup_date_time' )
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            result['result']['message'] = "An error occurred while processing the request."
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)     

