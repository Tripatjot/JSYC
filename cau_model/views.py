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
        
class ShowBasicInfo_AssignWALeadtoCAUAgent(APIView):
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
            
            cau_instance = User.objects.filter(user_role=5, current_status=1).values()
            cau_id= cau_instance[0]['id']
            all_data = Registration.objects.filter(cau_admin_id = cau_id)
            
            if get_district:
                data = data.filter(master__district = get_district)
            if get_block:
                data = data.filter(master__block_ulb = get_block)
            if get_source:
                data = data.filter(master__master_source = get_source)
            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['data'] = all_data.values(
                    'id', 'master__name', 'master__contact_number', 
                    'master__district', 'master__block_ulb', 'wa_group_strength' )
            
            return Response(result, status=status.HTTP_200_OK)
        except KeyError as e:
            result['result']['message'] = f"KeyError: {str(e)} not found in request data"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            result['result']['message'] = "Object not found"
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result['result']['message'] = f"An error occurred: {str(e)}"
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CAUAgentsListing(APIView):
    def get(self, request):
        result = {
                'status': "NOK",
                'valid': False,
                'result': {
                    'message': "Data not Found",
                    'data': []
                }
            }
        
        agents = User.objects.filter(user_role=6, current_status=1).values()
        result['status'] = "OK"
        result['valid'] = True
        result['result']['message'] = "Data retrieved successfully"
        result['result']['data'] = agents   
        return Response(result, status=status.HTTP_200_OK) 
    
class AssignWALeadtoCAUAgent(APIView):
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
                        cau_agent_id__isnull=True
                    ).order_by('id')[:agent_id_to_assign]

                temp_ids = list(temp.values_list('id', flat=True))
                Registration.objects.filter(id__in=temp_ids).update(cau_agent_id=agent_id)
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
              
class ShowBasicInfo_CAUAgent(APIView):
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

            data = Registration.objects.all().filter(cau_agent_id=get_id).exclude(
                Q (cau_lead_status = "All Criteria Fulfilled"))
            
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
                    'master__district', 'master__block_ulb', 'wa_group_strength' )
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            result['result']['message'] = "An error occurred while processing the request."
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateCAUfieldsbyCAUAgent(APIView):
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
            get_id = request.data.get(id)
            get_club_type = request.data.get('club_type')
            get_total_no_of_members_on_WA = request.data.get('total_no_of_members_on_WA')
            get_members_100_added_on_WA = request.data.get('members_100_added_on_WA')
            get_president_name = request.data.get('president_name')
            get_president_contact_no = request.data.get('president_contact_no')
            get_smpoc_name = request.data.get('smpoc_name')
            get_smpoc_contact_no = request.data.get('smpoc_contact_no')
            get_vice_president_name = request.data.get('vice_president_name')
            get_vice_president_contact_no = request.data.get('vice_president_contact_no')
            get_secretary_name = request.data.get('secretary_name')
            get_secretary_contact_no = request.data.get('secretary_contact_no')
            get_treasurer_name = request.data.get('treasurer_name')
            get_treasurer_contact_no = request.data.get('treasurer_contact_no')
            get_office_bearers_5_provided = request.data.get('office_bearers_5_provided')
            get_space_address = request.data.get('space_address')
            get_space_pic_or_video_provided = request.data.get('space_pic_or_video_provided')
            get_upload_space_pic_or_video = request.data.get('upload_space_pic_or_video')
            get_fb_page_name = request.data.get('fb_page_name')
            get_fb_page_link = request.data.get('fb_page_link')
            get_fb_page_id = request.data.get('fb_page_id')
            get_fb_page_password = request.data.get('fb_page_password')
            get_admin_right_shared_with_master_id = request.data.get('admin_right_shared_with_master_id')
            get_admin_right_received_by_master_id = request.data.get('admin_right_received_by_master_id')
            get_fb_page_created = request.data.get('fb_page_created')
            get_confirmation_status_clubs_rto = request.data.get('confirmation_status_clubs_rto')
            get_want_to_contest_election = request.data.get('want_to_contest_election')
            get_electoral_preference = request.data.get('electoral_preference')
            get_cau_remarks = request.data.get('cau_remarks')
            get_cau_followup_date_time = request.data.get('cau_followup_date_time')
            get_cau_call_status = request.data.get('cau_call_status')
            get_cau_lead_status = request.data.get('cau_lead_status')
            
            field_mapping = {
                'club_type': get_club_type,
                'total_no_of_members_on_WA': get_total_no_of_members_on_WA,
                'members_100_added_on_WA': get_members_100_added_on_WA,
                'president_name': get_president_name,
                'president_contact_no': get_president_contact_no,
                'smpoc_name': get_smpoc_name,
                'smpoc_contact_no': get_smpoc_contact_no,
                'vice_president_name': get_vice_president_name,
                'vice_president_contact_no': get_vice_president_contact_no,
                'secretary_name': get_secretary_name,
                'secretary_contact_no': get_secretary_contact_no,
                'treasurer_name': get_treasurer_name,
                'treasurer_contact_no': get_treasurer_contact_no,
                'office_bearers_5_provided': get_office_bearers_5_provided,
                'space_address': get_space_address,
                'space_pic_or_video_provided': get_space_pic_or_video_provided,
                'upload_space_pic_or_video': get_upload_space_pic_or_video,
                'fb_page_name': get_fb_page_name,
                'fb_page_link': get_fb_page_link,
                'fb_page_id': get_fb_page_id,
                'fb_page_password': get_fb_page_password,
                'admin_right_shared_with_master_id': get_admin_right_shared_with_master_id,
                'admin_right_received_by_master_id': get_admin_right_received_by_master_id,
                'fb_page_created': get_fb_page_created,
                'confirmation_status_clubs_rto': get_confirmation_status_clubs_rto,
                'want_to_contest_election': get_want_to_contest_election,
                'electoral_preference': get_electoral_preference,
                'cau_remarks': get_cau_remarks,
                'cau_followup_date_time': get_cau_followup_date_time,
                'cau_call_status': get_cau_call_status,
                'cau_lead_status': get_cau_lead_status
            } 
            
            Registration.objects.filter(id=get_id).update(**field_mapping)
            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data updated successfully"
            return Response(result, status=status.HTTP_200_OK)
        except KeyError as e:
            result['result']['message'] = f"KeyError: {str(e)} not found in request data"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            result['result']['message'] = "Object not found"
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result['result']['message'] = f"An error occurred: {str(e)}"
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        
class PreviousStatusonCAUAgentLeadform(APIView):
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
            data = Registration.objects.filter(id= get_id).values(
                'cau_followup_date_time',
                'cau_admin_id',
                'cau_agent_id',
                'cau_call_status',
                'cau_lead_status',
                'cau_remarks'
            )
            cau_agent_id = data[0]['cau_agent_id']
            agent = User.objects.filter(id=cau_agent_id, user_role=6).values('name')
            
            cau_admin = User.objects.filter(user_role=5).values('name')
            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data updated successfully"
            result['result']['cau_agent_id'] = agent
            result['result']['cau_admin_id'] = cau_admin
            result['result']['data'] = data
            return Response(result, status=status.HTTP_200_OK)
        except KeyError as e:
            result['result']['message'] = f"KeyError: {str(e)} not found in request data"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            result['result']['message'] = "Id not found"
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result['result']['message'] = f"An error occurred: {str(e)}"
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ShowBasicInfo_RTOLeadtoSuperAdmin(APIView):
    def post(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }
        get_district = request.data.get('district')
        get_block = request.data.get('block')
        get_source = request.data.get('source')
        
        data = Registration.objects.all().filter(cau_admin_id=5, cau_lead_status = "All Criteria Fulfilled" )

        
        if get_district:
            data = data.filter(master__district = get_district)
        if get_block:
            data = data.filter(master__block_ulb = get_block)
        if get_source:
            data = data.filter(master__master_source = get_source)
            
        result['status'] = "OK"
        result['valid'] = True
        result['result']['message'] = "Data retrieved successfully"
        result['result']['data'] = data.values(
                'id', 'master__name', 'master__contact_number', 
                'master__district', 'master__block_ulb', 'wa_group_strength' )
        
class AssignRTOLeadstoSuperAdmin (APIView):
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
            get_ids = request.data.get('ids')
            sa_id = User.objects.filter(user_role_id = 1).values('id') 
            data = Registration.objects.filter(id__in=get_ids).update(cau_sa_status=sa_id, cau_admin_assign_sa_date = datetime.today())
            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['data'] = data.values('id')
            return Response(result, status=status.HTTP_200_OK)
        except KeyError as e:
            result['result']['message'] = f"KeyError: {str(e)} not found in request data"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            result['result']['message'] = "Object not found"
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result['result']['message'] = f"An error occurred: {str(e)}"
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   


     
        
        
        
        
        
        
        
        
        
        
        
        
         


            
            
            
            
        
        
        