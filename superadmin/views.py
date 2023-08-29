from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status  
from summary.models import DistrictMapping, DataSource, Master, Registration
from users.models import User
import pandas as pd
from datetime import datetime
import math
from django.db.models import F,Q
from django.core.exceptions import ObjectDoesNotExist

# SuperAdmin- New Leads
class DistrictLisitng(APIView):
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
    
class BlockListing(APIView):
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
        
class DataSourceListing(APIView):
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
        
class UploadingNewLeads(APIView):
    def post(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }

        file = request.data.get('file')
        if not file:
            return Response("File is missing.", status=status.HTTP_400_BAD_REQUEST)

        content_type = file.content_type.lower()
        allowed_formats = ['csv', 'text/csv', 'xls', 'xlsx']

        if content_type not in allowed_formats:
            return Response(f"Unsupported file format: {content_type}", status=status.HTTP_400_BAD_REQUEST)

        try:
            if content_type in ['csv', 'text/csv']:
                print("Reading CSV file...")
                df = pd.read_csv(file)
            else:  # Assuming 'xls' or 'xlsx'
                print("Reading Excel file...")
                df = pd.read_excel(file)
            
            data_list = []
            for _, row in df.iterrows():
                fields_to_extract = [
                    'uid', 'master_source', 'sub_source_name', 'source_contact_no', 'political_category', 'name', 'contact_number', 'age', 'gender',
                    'religion', 'category', 'caste', 'district', 'assembly', 'block_ulb', 'panchayat_ward', 'village_habitation', 'occupation', 'profile',
                    'whatsapp_user', 'whatsapp_number', 'rural_urban'
                ]
                d = {field: row[field] for field in fields_to_extract}
                data_list.append(Master(**d))
            
            Master.objects.bulk_create(data_list)
            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data Uploaded successfully"
            return Response(result, status=status.HTTP_200_OK)

        except pd.errors.ParserError as e:
            error_message = "Error parsing the file. Please check the file format."
        except Exception as e:
            error_message = str(e)
        
        result['status'] = "NOK"
        result['valid'] = False
        result['result']['message'] = error_message
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

class TotalLeadUnassigned(APIView):
    def get(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found"
            }
        }

        get_dist = request.data.get('district')
        get_block = request.data.get('block')
        get_source = request.data.get('source')
        
        total_data = Registration.objects.filter(lau_consent_agent_id__isnull=True)
        
        if get_dist:
            total_data = total_data.filter(master__district=get_dist)
        if get_block:
            total_data = total_data.filter(master__block_ulb=get_block)
        if get_source:
            total_data = total_data.filter(master__master_source=get_source)
        
        result['count'] = total_data.count()
        result['data'] = total_data.values(
            'id', 'master__uid', 'master__name', 'master__district',
            'master__block_ulb', 'master__master_source'
        )
        
        result['status'] = "okay"
        result['valid'] = True
        result['result'] = {"message": "Data fetched successfully"}
        return Response(result, status=status.HTTP_200_OK)
        
class TotalLeadAssignd(APIView):
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
        
        lau_id = User.objects.filter(user_role_id=2).values('id')
        data = request.data.get('leads')
        
        if not data:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        ids_with_new_record_status_zero = Master.objects.filter(new_record_status=0).values('id')[:int(data)]
        master_ids = [item['id'] for item in ids_with_new_record_status_zero]
        
        if master_ids:
            master_objects = Master.objects.filter(id__in=master_ids)
            registrations_to_create = []
            
            for master_obj in master_objects:
                try:
                    registration = Registration( master=master_obj, lau_admin_id=lau_id, lau_created_date=datetime.now())
                    master_obj.new_record_status = 1
                    registrations_to_create.append(registration)
                except Master.DoesNotExist:
                    pass
            
            if registrations_to_create:
                Registration.objects.bulk_create(registrations_to_create)
                Master.objects.filter(id__in=master_ids).update(new_record_status=1)
        result['status'] = "okay"
        result['valid'] = True
        result['result'] = {"message": "Registrations created successfully"}
        result['result']['Updated Ids'] = master_ids
        
        return Response(result, status=status.HTTP_201_CREATED)

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
        print(agents.count())
        result['status'] = "OK"
        result['valid'] = True
        result['result']['message'] = "Data Fetched Successfully"
        result['result']['count'] = agents.count()
        result['result']['data'] = agents
        return Response(result, status=status.HTTP_200_OK)
    
class TotalLeadsUnassignedbyLAUAdmin(APIView):
    def post (self, request):
            result = {
                'status': "NOK",
                'valid': False,
                'result': {
                    'message': "Data not Found",
                    'data': []
                }
            }
            get_dist = request.data["district"]
            get_block = request.data["block"]
            get_source = request.data["source"]
            all_data = Registration.objects.filter(lau_consent_agent_id__isnull=True)
            
            if get_dist:
                all_data = all_data.filter(master__district = get_dist)
            if get_block:
                all_data = all_data.filter(master__block_ulb = get_block)
            if get_source:
                all_data = all_data.filter(master__master_source = get_source)
                
            result['status'] = "okay"
            result['valid'] = True
            result['count'] = all_data.count()
            # result['data'] = all_data.values(
            #     'id', 'master__uid', 'master__name','master__district', 'master__block_ulb', 'master__master_source'
            #     )
            result['result'] = {"message": "Data fetched successfully"}
            return Response(result, status=status.HTTP_200_OK)        
        
class LauAssiginLeadsToAgents(APIView):
    def post(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Unauthorized access",
                'data': []
            }
        }
        try:
            tasks_count = int(request.data.get('leads_count', 0))
            member_ids = request.data.get('agent_ids', {})
            if tasks_count <= 0 or not member_ids:
                return Response({'error': 'Invalid getut'}, status=status.HTTP_400_BAD_REQUEST)

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
            
            try:
                updated_ids = []
                for agent_id in member_ids:
                    agent_id_to_assign = distribution_result[agent_id]
                    temp = Registration.objects.filter(
                            lau_consent_agent_id__isnull = True , 
                            master__new_record_status=1
                        ).order_by('id')[:agent_id_to_assign]

                    temp_ids = list(temp.values_list('id', flat=True))
                    # print(temp_ids)
                    Registration.objects.filter(id__in=temp_ids).update(cau_agent_id=agent_id)
                    updated_ids.extend(temp_ids)
                
                
                # ids_to_update = Registration.objects.filter(lau_consent_agent_id__isnull = True , master__new_record_status=1)[:tasks_count]
                # Registration.objects.filter(id__in = ids_to_update).update(lau_consent_agent_id=ids)
                # # print(ids_to_update.values('id'))
                # # print(len(ids_to_update))
                
                # if len(ids_to_update) < tasks_count:
                #     result['result']['message'] = "Invalid task/ Provide more Leads"
                #     return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
                # try :
                #     i = 0
                #     res = []
                #     for ids in member_ids:
                #         for task in range(0,distribution_result[ids]):
                #             register = Registration.objects.filter(id = ids_to_update[i].id).update(lau_consent_agent_id=ids)
                #             res.append(register)
                #             i= i+1

                #     print('register : ', res)
                # except Exception as err:
                #     result['status'] = "NOK"
                #     result['valid'] = False
                #     result['result']['message'] = str(err)
                #     return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                result['status'] = "OK"
                result['valid'] = True
                result['result']['message'] = "Data Fetched Successfully"
                result['result']['data'] = distribution_result
                result['result']['Updated Ids'] = updated_ids
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                result['status'] = "NOK"
                result['valid'] = False
                result['result']['message'] = str(e)
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class TaskDistributionAPIView(APIView):
#     def post(self, request, format=None):
#         result = {
#             'status': "NOK",
#             'valid': False,
#             'result': {
#                 'message': "Data not Found",
#                 'data': []
#             }
#         }
#         try:
#             tasks_count = int(request.data.get('tasks_count', 0))
#             member_ids = request.data.get('member_ids', {})
#             if tasks_count <= 0 or not member_ids:
#                 return Response({'error': 'Invalid getut'}, status=status.HTTP_400_BAD_REQUEST)

#             total_number_of_members = len(member_ids)
#             tasks_per_member = math.floor(tasks_count / total_number_of_members)
#             remaining_tasks = tasks_count % total_number_of_members

#             distribution_result = {}
#             for id in member_ids:
#                 member_tasks = tasks_per_member
#                 if remaining_tasks > 0:
#                     member_tasks += 1
#                     remaining_tasks -= 1

#                 distribution_result[id] = member_tasks
            
#             try:
#                 ids_to_update = Registration.objects.filter(lau_consent_agent_id__isnull = True , master__new_record_status=1)[:tasks_count]
#                 print(ids_to_update.values('id'))
#                 print(len(ids_to_update))
                
#                 if len(ids_to_update) < tasks_count:
#                     result['result']['message'] = "Invalid task/ Provide more Leads"
#                     return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
#                 try :
#                     i = 0
#                     res = []
#                     for ids in member_ids:
#                         for task in range(0,distribution_result[ids]):
#                             register = Registration.objects.filter(id = ids_to_update[i].id).update(lau_consent_agent_id=ids)
#                             res.append(register)
#                             i= i+1

#                     print('register : ', res)
#                 except Exception as err:
#                     result['status'] = "NOK"
#                     result['valid'] = False
#                     result['result']['message'] = str(err)
#                     return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
#                 result['status'] = "OK"
#                 result['valid'] = True
#                 result['result']['message'] = "Data Fetched Successfully"
#                 result['result']['data'] = distribution_result
#                 return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#             except Exception as e:
#                 result['status'] = "NOK"
#                 result['valid'] = False
#                 result['result']['message'] = str(e)
#                 return Response(result, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        
# LAU Agents 
class AssignedLeadsforLAUAgents(APIView):
    # LAU Agent screen will show all the leads assigned to them.
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
            lau_id = request.data.get('lau_agent_id')
            get_district = request.data.get('district')
            get_block = request.data.get('block')
            get_call_status = request.data.get('call_status')
            get_lead_status = request.data.get('lead_status')
            
            # Retrieve relevant data for the given LAU agent ID
            data = Registration.objects.filter(
                lau_consent_agent_id=lau_id
            ).values(
                'id', 'master__uid', 'master__name', 'master__contact_number', 'master__district',
                'lau_consent_call_status', 'lau_consent_call_status_2', 'lau_consent_call_status_3',
                'lau_consent_lead_status', 'lau_consent_lead_status_2', 'lau_consent_lead_status_3',
                'lau_consent_followup_date_time', 'lau_consent_followup_date_time_2', 'lau_consent_followup_date_time_3'
            ).order_by('id')
            
            # data = Registration.objects.filter( lau_consent_agent_id=lau_id).values()
            if get_district:
                data = data.filter(master__district = get_district)
            if get_block:
                data = data.filter(master__block_ulb = get_block)
            if get_lead_status:
                data = data.filter(lau_consent_lead_status = get_lead_status).exclude(
                    Q(lau_consent_lead_status="All Criteria Fulfilled Consent") | 
                    Q(lau_consent_lead_status="All Criteria Fulfilled WA") | 
                    Q(lau_consent_lead_status="Not Interested") |
                    Q(lau_consent_lead_status_2="All Criteria Fulfilled Consent") | 
                    Q(lau_consent_lead_status_2="All Criteria Fulfilled WA") | 
                    Q(lau_consent_lead_status_2="Not Interested") |
                    Q(lau_consent_lead_status_3="All Criteria Fulfilled Consent") | 
                    Q(lau_consent_lead_status_3="All Criteria Fulfilled WA") | 
                    Q(lau_consent_lead_status_3="Not Interested"))
            if get_call_status:
                data = data.filter(lau_consent_lead_status = get_lead_status).exclude( 
                    Q(lau_consent_call_status="Connected") | 
                    Q(lau_consent_call_status="Wrong Number") |
                    Q(lau_consent_call_status_2="Connected") |
                    Q(lau_consent_call_status_2="Wrong Number") |
                    Q(lau_consent_call_status_3="Connected") | 
                    Q(lau_consent_call_status_3="Wrong Number"))
                
            # Update the result dictionary
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data Fetched Successfully"
            result['result']['count'] = data.count()
            result['result']['data'] = data
            
            return Response(result, status=status.HTTP_200_OK)
        except KeyError:
            result['result']['message'] = "Missing or invalid input"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result['result']['message'] = str(e)
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShowBasicInfotoLAUAgent(APIView):
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
            lead_id = request.data['lead_id']
            
            reg_id = Registration.objects.filter(id=lead_id).values()
            if not reg_id:
                result['result']['message'] = "Registration data not found"
                return Response(result, status=status.HTTP_404_NOT_FOUND)
            
            master_lead_id = reg_id[0]["master_id"]
            
            data = Master.objects.filter(id=master_lead_id).values()
            if not data:
                result['result']['message'] = "Master data not found"
                return Response(result, status=status.HTTP_404_NOT_FOUND)
            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data Fetched Successfully"
            result['result']['data'] = data.values(
                'uid','master_source','sub_source_name','source_contact_no',
                'political_category','name','contact_number','age','gender',
                'religion','category','caste','district','assembly','block_ulb',
                'panchayat_ward','village_habitation','occupation','profile',
                'whatsapp_user','whatsapp_number','rural_urban','other_caste')
            
            return Response(result, status=status.HTTP_200_OK)
        except KeyError:
            result['result']['message'] = "Missing or invalid input"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result['result']['message'] = str(e)
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class SaveChangesBasicInfo(APIView):
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
            get_id = request.data.get('lead_id')
            reg_instance = Registration.objects.get(id=get_id)
            master_lead_id = reg_instance.master_id
            print(master_lead_id)
            
            fields_to_update = [
                'master_source', 'sub_source_name', 'source_contact_no', 'political_category',
                'name', 'age','contact_number' 'gender', 'religion', 'category', 'caste', 'district', 'assembly',
                'rural_urban', 'block_ulb', 'panchayat_ward', 'village_habitation',
                'occupation', 'profile', 'whatsapp_user', 'whatsapp_number', 'other_caste'
            ]
            update_data = {}
            for field in fields_to_update:
                value = request.data.get(field)
                if value is not None:
                    update_data[field] = value

            Master.objects.filter(id=master_lead_id).update(**update_data)

            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data updated successfully"
            return Response(result, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            result['result']['message'] = "Registration ID not found"
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result['result']['message'] = "An error occurred"
            result['result']['error'] = str(e)
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
      
class updateWAinfoByLAUAgent_1(APIView):
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
            get_id = request.data['id']
            
            get_interested_in_opening_youth_club = request.data['interested_in_opening_youth_club']
            get_founding_25_members = request.data['founding_25_members']
            get_whatsapp_group_of_100 = request.data['whatsapp_group_of_100']
            get_physical_meeting_space = request.data['physical_meeting_space']
            get_ready_to_create_club_fb_page = request.data['ready_to_create_club_fb_page']
            get_ready_pk_connect_app_download = request.data['ready_pk_connect_app_download']
            
            get_whatsapp_group_created = request.data['whatsapp_group_created']
            get_wa_group_link = request.data['wa_group_link']
            get_wa_group_name = request.data['wa_group_name']
            get_wa_group_strength = request.data['wa_group_strength']
            get_central_number_added = request.data['central_number_added']
            get_pk_connect_app_download = request.data['pk_connect_app_download']
            get_app_download_verified = request.data['app_download_verified']
            
            get_referral_name = request.data['referral_name']
            get_referral_contact_no = request.data['referral_contact_no']
            get_lau_remarks = request.data['lau_remarks']
            
            calling_mode = request.data['calling_mode']    
            
            if calling_mode == 'consent':
                registration_data = {
                    'interested_in_opening_youth_club': get_interested_in_opening_youth_club,
                    'founding_25_members': get_founding_25_members,
                    'whatsapp_group_of_100': get_whatsapp_group_of_100,
                    'physical_meeting_space': get_physical_meeting_space,
                    'ready_to_create_club_fb_page': get_ready_to_create_club_fb_page,
                    'ready_to_pk_connect_app_download': get_ready_pk_connect_app_download,
                    'whatsapp_group_created': get_whatsapp_group_created,
                    'wa_group_link': get_wa_group_link,
                    'wa_group_name': get_wa_group_name,
                    'wa_group_strength': get_wa_group_strength,
                    'central_number_added': get_central_number_added,
                    'pk_connect_app_download': get_pk_connect_app_download,
                    'app_download_verified': get_app_download_verified,
                    'referral_name': get_referral_name,
                    'referral_contact_no': get_referral_contact_no,
                    'lau_remarks': get_lau_remarks,
                    'lau_last_updated_date_time': datetime.today(),
                }
                print(registration_data)
                Registration.objects.filter(id=get_id).update(**registration_data)
            elif calling_mode == 'whatsapp' :
                registration_data = {
                    'interested_in_opening_youth_club': get_interested_in_opening_youth_club,
                    'founding_25_members': get_founding_25_members,
                    'whatsapp_group_of_100': get_whatsapp_group_of_100,
                    'physical_meeting_space': get_physical_meeting_space,
                    'ready_to_create_club_fb_page': get_ready_to_create_club_fb_page,
                    'ready_to_pk_connect_app_download': get_ready_pk_connect_app_download,
                    'whatsapp_group_created': get_whatsapp_group_created,
                    'wa_group_link': get_wa_group_link,
                    'wa_group_name': get_wa_group_name,
                    'wa_group_strength': get_wa_group_strength,
                    'central_number_added': get_central_number_added,
                    'pk_connect_app_download': get_pk_connect_app_download,
                    'app_download_verified': get_app_download_verified,
                    'referral_name': get_referral_name,
                    'referral_contact_no': get_referral_contact_no,
                    'lau_remarks': get_lau_remarks,
                    'lau_last_updated_date_time': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                }
                
                print(registration_data)
                Registration.objects.filter(id=get_id).update(**registration_data)
            else:
                result['result']['message'] = "Invalid calling_mode"
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            reg_instance = Registration.objects.get (id= get_id)
            master_lead_id = reg_instance.master_id
            
            data = Master.objects.filter(id= master_lead_id).values()
            data_1 = Registration.objects.filter(id= get_id).values()
            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data updated successfully"
            result['result']['data'] = list(data), list(data_1)
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
        
class updateWAinfoByLAUAgent_2(APIView):
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
            get_id= request.data['id']
            calling_mode = request.data['calling_mode']    
            get_call_status = request.data['call_status']
            get_lead_status = request.data['lead_status']
            get_follow_date_time = request.data['follow_date_time']
            get_remarks = request.data['remarks']
            
            # registration_data = {
            #     'lau_consent_call_status' : get_call_status,
            #     'lau_consent_lead_status' : get_lead_status,
            #     'lau_last_updated_date_time': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            #     'lau_consent_remarks' : get_remarks
            # }
            
            if calling_mode == 'consent':
                registration_data = {
                    'lau_consent_call_status' : get_call_status,
                    'lau_consent_lead_status' : get_lead_status,
                    # 'lau_consent_followup_date_time': get_follow_date_time,
                    'lau_consent_followup_date_time': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    'lau_consent_remarks' : get_remarks
                }
            elif calling_mode == 'whatsapp' :
                registration_data = {
                'lau_call_status' : get_call_status,
                'lau_lead_status' : get_lead_status,
                # 'lau_followup_date_time': get_follow_date_time,
                'lau_followup_date_time': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                'lau_crm_remarks' : get_remarks
            }
            else:
                result['result']['message'] = "Invalid calling_mode"
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
            Registration.objects.filter(id=get_id).update(**registration_data)
            data = Registration.objects.filter(id=get_id).values()
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data updated successfully"
            result['result']['data'] = data
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
        
class LauCallStatusListing(APIView):
    def get(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }
        try:
            call_status = ["Connected", "Call Back Later", "Busy", 
                           "Call Not answered", "Switched off",
                           "Number not reachable", "Wrong Number"]
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['data'] = call_status 
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            result['result']['message'] = f"An error occurred: {str(e)}"
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      
        
class LauLeadStatusListing(APIView):
    def get(self, request):
        result = {
            'status': "NOK",
            'valid': False,
            'result': {
                'message': "Data not Found",
                'data': []
            }
        }
        try:
            call_status = ["All Criteria Fulfilled Consent", "All Criteria Fulfilled WA", 
                           "Not Interested", "Followup"]
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['data'] = call_status 
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            result['result']['message'] = f"An error occurred: {str(e)}"
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
# LAU Admin - Assign Leads-Consent to WA   
class LAUAdminConsenttoWA(APIView):
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
        
        data = Registration.objects.all().filter(lau_consent_agent_id__isnull = False, lau_consent_lead_status = 'All Criteria Fulfilled Consent')
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
                'id', 'master__uid', 'master__name', 
                'master__district', 'master__block_ulb', 
                'master__master_source','lau_consent_lead_status',
            )
        return Response(result, status=status.HTTP_200_OK) 
     
class AssignLeadsConsenttoWA(APIView):
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
            print(get_agent_ids)
            print(get_lead_ids)
            
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
                        lau_consent_agent_id__isnull=True
                    ).order_by('id')[:agent_id_to_assign]

                temp_ids = list(temp.values_list('id', flat=True))
                Registration.objects.filter(id__in=temp_ids).update(lau_consent_agent_id=agent_id)
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

# LAU Admin - Leads WA-SuperAdmin
class Showbasicinfo_LAUAdminWAtoSuperAdmin(APIView):
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
        
        data = Registration.objects.all().filter(lau_consent_agent_id__isnull = False, lau_lead_status = "All Criteria Fulfilled WA")
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
                'id', 'master__uid', 'master__name', 
                'master__district', 'master__block_ulb', 
                'master__master_source','lau_lead_status','wa_group_strength'
            )
        return Response(result, status=status.HTTP_200_OK) 
  
class AssignWAtoSuperAdmin(APIView):
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
            get_ids_str = request.data.get('ids')
            get_ids = [int(agent_id) for agent_id in get_ids_str.split(',')]
            sa_id = User.objects.filter(user_role_id = 1).values('id') 
            data = Registration.objects.filter(id__in=get_ids).update(lau_sa_status=sa_id, lau_admin_assign_sa_date = datetime.today())
            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['data'] = data
            result['result']['ids'] = get_ids
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
  
#Superadmin-Whatsapp-Lead Consent
class ShowBasicInfo_AssignWALeadtoCAUAdmin(APIView):
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
            
            sa_id = User.objects.filter(user_role_id = 1).values('id')
            print(sa_id)
            data = Registration.objects.filter( lau_sa_status__in = sa_id).values(
                    'id', 'master__name', 'master__contact_number', 
                    'master__district', 'master__block_ulb', 'master__age' )
            
            if get_district:
                data = data.filter(master__district = get_district)
            if get_block:
                data = data.filter(master__block_ulb = get_block)
            if get_source:
                data = data.filter(master__master_source = get_source)
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['data'] = data
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            result['result']['message'] = str(e)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

class AssignWALeadtoCAUAdmin(APIView):
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
            # get_ids = request.data.get('ids')
            get_ids_str = request.data.get('ids')
            get_ids = [int(agent_id) for agent_id in get_ids_str.split(',')]
            
            cau_instance = User.objects.filter(user_role=5, current_status=1).values()
            cau_id= cau_instance[0]['id']
            
            Registration.objects.filter(id__in=get_ids).update(cau_admin_id=cau_id)
            
            data = Registration.objects.filter(cau_admin_id = cau_id).values()
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['data'] = data.values('id')
            # result['result']['ids'] = get_ids
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
   
class ShowBasicInfo_AssignRTOLeadstoCOU (APIView):
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
            
            sa_id = User.objects.filter(user_role_id = 1).values('id')
            print(sa_id)
            data = Registration.objects.filter( cau_sa_status__in = sa_id).values(
                    'id', 'master__name', 'master__contact_number', 
                    'master__district', 'master__block_ulb', 'master__age' )
            
            if get_district:
                data = data.filter(master__district = get_district)
            if get_block:
                data = data.filter(master__block_ulb = get_block)
            if get_source:
                data = data.filter(master__master_source = get_source)
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['data'] = data
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            result['result']['message'] = str(e)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
class AssignRTOLeadstoCOU(APIView):
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
            # get_ids = request.data.get('ids')
            get_ids_str = request.data.get('ids')
            get_ids = [int(agent_id) for agent_id in get_ids_str.split(',')]
            
            cou_instance = User.objects.filter(user_role=7, current_status=1).values()
            cou_id= cou_instance[0]['id']
            
            Registration.objects.filter(id__in=get_ids).update(cou_admin_id=cou_id)
            
            data = Registration.objects.filter(cou_admin_id = cou_id).values()
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['data'] = data.values('id')
            result['result']['ids'] = get_ids
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
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
        
# class ShowBasicInfo_AssignWALeadtoCAUAgent(APIView):
#     def post(self, request):
#         result = {
#             'status': "NOK",
#             'valid': False,
#             'result': {
#                 'message': "Data not Found",
#                 'data': []
#             }
#         }
#         try:
#             get_district = request.data.get('district')
#             get_block = request.data.get('block')
#             get_source = request.data.get('source')
            
#             cau_instance = User.objects.filter(user_role=5, current_status=1).values()
#             cau_id= cau_instance[0]['id']
#             all_data = Registration.objects.filter(cau_admin_id = cau_id)
            
#             if get_district:
#                 data = data.filter(master__district = get_district)
#             if get_block:
#                 data = data.filter(master__block_ulb = get_block)
#             if get_source:
#                 data = data.filter(master__master_source = get_source)
            
#             result['status'] = "OK"
#             result['valid'] = True
#             result['result']['message'] = "Data retrieved successfully"
#             result['result']['data'] = all_data.values(
#                     'id', 'master__name', 'master__contact_number', 
#                     'master__district', 'master__block_ulb', 'wa_group_strength' )
            
#             return Response(result, status=status.HTTP_200_OK)
#         except KeyError as e:
#             result['result']['message'] = f"KeyError: {str(e)} not found in request data"
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)
#         except ObjectDoesNotExist:
#             result['result']['message'] = "Object not found"
#             return Response(result, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             result['result']['message'] = f"An error occurred: {str(e)}"
#             return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class CAUAgentsListing(APIView):
#     def get(self, request):
#         result = {
#                 'status': "NOK",
#                 'valid': False,
#                 'result': {
#                     'message': "Data not Found",
#                     'data': []
#                 }
#             }
        
#         agents = User.objects.filter(user_role=6, current_status=1).values()
#         result['status'] = "OK"
#         result['valid'] = True
#         result['result']['message'] = "Data retrieved successfully"
#         result['result']['data'] = agents   
#         return Response(result, status=status.HTTP_200_OK) 
    
# class AssignWALeadtoCAUAgent(APIView):
#     def post (self, request):
#         result = {
#             'status': "NOK",
#             'valid': False,
#             'result': {
#                 'message': "Data not Found",
#                 'data': []
#             }
#         } 
#         try:
#             get_lead_ids_str = request.data.get('lead_ids')
#             get_lead_ids = [int(lead_id) for lead_id in get_lead_ids_str.split(',')]
            
#             get_agent_ids_str = request.data.get('agent_ids')
#             get_agent_ids = [int(agent_id) for agent_id in get_agent_ids_str.split(',')]
            
#             if len(get_agent_ids) > len(get_lead_ids) :
#                 result['result']['message'] = 'Agents are more than Leads provided.'
#                 return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            
#             lead_count= len(get_lead_ids) 
#             agent_count = len(get_agent_ids) 
            
#             leads_per_member = math.floor(lead_count / agent_count)
#             remaining_tasks = lead_count % agent_count
            
#             distribution_result = {}
#             for id in get_agent_ids:
#                 member_tasks = leads_per_member
#                 if remaining_tasks > 0:
#                     member_tasks += 1
#                     remaining_tasks -= 1
#                 distribution_result[id] = member_tasks
            
#             updated_ids = []
#             for agent_id in get_agent_ids:
#                 agent_id_to_assign = distribution_result[agent_id]
#                 temp = Registration.objects.filter(
#                         id__in=get_lead_ids, 
#                         cau_agent_id__isnull=True
#                     ).order_by('id')[:agent_id_to_assign]

#                 temp_ids = list(temp.values_list('id', flat=True))
#                 Registration.objects.filter(id__in=temp_ids).update(cau_agent_id=agent_id)
#                 updated_ids.extend(temp_ids)
                
#             # print(get_lead_ids)
#             # print(get_agent_ids)
#             data = Registration.objects.filter(id__in=get_lead_ids).values('id')

            
#             result['status'] = "OK"
#             result['valid'] = True
#             result['result']['message'] = "Data retrieved successfully"
#             result['result']['distribution'] = distribution_result
#             result['result']['ids'] = updated_ids
#             return Response(result, status=status.HTTP_200_OK)
#         except ValueError as e:
#             result['result']['message'] = "Invalid data format provided."
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             result['result']['message'] = "An error occurred while processing the request."
#             return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
              
# class ShowBasicInfo_CAUAgent(APIView):
#     def post(self, request):
#         result = {
#             'status': "NOK",
#             'valid': False,
#             'result': {
#                 'message': "Data not Found",
#                 'data': []
#             }
#         }
        
#         try:
#             get_id = request.data.get('id')
#             get_district = request.data.get('district')
#             get_block = request.data.get('block')
#             get_call_status = request.data.get('call_status')
#             get_lead_status = request.data.get('lead_status')
#             get_date = request.data.get('date')
            
#             if not get_id:
#                 result['result']['message'] = "Missing 'id' parameter."
#                 return Response(result, status=status.HTTP_400_BAD_REQUEST)

#             data = Registration.objects.all().filter(cau_agent_id=get_id).exclude(
#                 Q (cau_lead_status = "All Criteria Fulfilled"))
            
#             if get_district:
#                 data = data.filter(master__district=get_district)
#             if get_block:
#                 data = data.filter(master__block_ulb=get_block)
#             if get_call_status:
#                 data = data.filter(cau_call_status=get_call_status)
#             if get_lead_status:
#                 data = data.filter(cau_lead_status=get_lead_status)
#             if get_date:
#                 data = data.filter(cau_followup_date_time=get_date)
            
#             result['status'] = "OK"
#             result['valid'] = True
#             result['result']['message'] = "Data retrieved successfully"
#             result['result']['data'] = data.values('id')
#             return Response(result, status=status.HTTP_200_OK)

#         except Exception as e:
#             result['result']['message'] = "An error occurred while processing the request."
#             return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# class UpdateCAUfieldsbyCAUAgent(APIView):
#     def post(self, request):
#         result = {
#             'status': "NOK",
#             'valid': False,
#             'result': {
#                 'message': "Data not Found",
#                 'data': []
#             }
#         }
#         try: 
#             get_id = request.data.get(id)
#             get_club_type = request.data.get('club_type')
#             get_total_no_of_members_on_WA = request.data.get('total_no_of_members_on_WA')
#             get_members_100_added_on_WA = request.data.get('members_100_added_on_WA')
#             get_president_name = request.data.get('president_name')
#             get_president_contact_no = request.data.get('president_contact_no')
#             get_smpoc_name = request.data.get('smpoc_name')
#             get_smpoc_contact_no = request.data.get('smpoc_contact_no')
#             get_vice_president_name = request.data.get('vice_president_name')
#             get_vice_president_contact_no = request.data.get('vice_president_contact_no')
#             get_secretary_name = request.data.get('secretary_name')
#             get_secretary_contact_no = request.data.get('secretary_contact_no')
#             get_treasurer_name = request.data.get('treasurer_name')
#             get_treasurer_contact_no = request.data.get('treasurer_contact_no')
#             get_office_bearers_5_provided = request.data.get('office_bearers_5_provided')
#             get_space_address = request.data.get('space_address')
#             get_space_pic_or_video_provided = request.data.get('space_pic_or_video_provided')
#             get_upload_space_pic_or_video = request.data.get('upload_space_pic_or_video')
#             get_fb_page_name = request.data.get('fb_page_name')
#             get_fb_page_link = request.data.get('fb_page_link')
#             get_fb_page_id = request.data.get('fb_page_id')
#             get_fb_page_password = request.data.get('fb_page_password')
#             get_admin_right_shared_with_master_id = request.data.get('admin_right_shared_with_master_id')
#             get_admin_right_received_by_master_id = request.data.get('admin_right_received_by_master_id')
#             get_fb_page_created = request.data.get('fb_page_created')
#             get_confirmation_status_clubs_rto = request.data.get('confirmation_status_clubs_rto')
#             get_want_to_contest_election = request.data.get('want_to_contest_election')
#             get_electoral_preference = request.data.get('electoral_preference')
#             get_cau_remarks = request.data.get('cau_remarks')
#             get_cau_followup_date_time = request.data.get('cau_followup_date_time')
#             get_cau_call_status = request.data.get('cau_call_status')
#             get_cau_lead_status = request.data.get('cau_lead_status')
            
#             field_mapping = {
#                 'club_type': get_club_type,
#                 'total_no_of_members_on_WA': get_total_no_of_members_on_WA,
#                 'members_100_added_on_WA': get_members_100_added_on_WA,
#                 'president_name': get_president_name,
#                 'president_contact_no': get_president_contact_no,
#                 'smpoc_name': get_smpoc_name,
#                 'smpoc_contact_no': get_smpoc_contact_no,
#                 'vice_president_name': get_vice_president_name,
#                 'vice_president_contact_no': get_vice_president_contact_no,
#                 'secretary_name': get_secretary_name,
#                 'secretary_contact_no': get_secretary_contact_no,
#                 'treasurer_name': get_treasurer_name,
#                 'treasurer_contact_no': get_treasurer_contact_no,
#                 'office_bearers_5_provided': get_office_bearers_5_provided,
#                 'space_address': get_space_address,
#                 'space_pic_or_video_provided': get_space_pic_or_video_provided,
#                 'upload_space_pic_or_video': get_upload_space_pic_or_video,
#                 'fb_page_name': get_fb_page_name,
#                 'fb_page_link': get_fb_page_link,
#                 'fb_page_id': get_fb_page_id,
#                 'fb_page_password': get_fb_page_password,
#                 'admin_right_shared_with_master_id': get_admin_right_shared_with_master_id,
#                 'admin_right_received_by_master_id': get_admin_right_received_by_master_id,
#                 'fb_page_created': get_fb_page_created,
#                 'confirmation_status_clubs_rto': get_confirmation_status_clubs_rto,
#                 'want_to_contest_election': get_want_to_contest_election,
#                 'electoral_preference': get_electoral_preference,
#                 'cau_remarks': get_cau_remarks,
#                 'cau_followup_date_time': get_cau_followup_date_time,
#                 'cau_call_status': get_cau_call_status,
#                 'cau_lead_status': get_cau_lead_status
#             } 
            
#             Registration.objects.filter(id=get_id).update(**field_mapping)
            
#             result['status'] = "OK"
#             result['valid'] = True
#             result['result']['message'] = "Data updated successfully"
#             return Response(result, status=status.HTTP_200_OK)
#         except KeyError as e:
#             result['result']['message'] = f"KeyError: {str(e)} not found in request data"
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)
#         except ObjectDoesNotExist:
#             result['result']['message'] = "Object not found"
#             return Response(result, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             result['result']['message'] = f"An error occurred: {str(e)}"
#             return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        
# class PreviousStatusonCAUAgentLeadform(APIView):
#     def post(self, request):
#         result = {
#             'status': "NOK",
#             'valid': False,
#             'result': {
#                 'message': "Data not Found",
#                 'data': []
#             }
#         }
#         try:
#             get_id = request.data.get('id')
#             data = Registration.objects.filter(id= get_id).values(
#                 'cau_followup_date_time',
#                 'cau_admin_id',
#                 'cau_agent_id',
#                 'cau_call_status',
#                 'cau_lead_status',
#                 'cau_remarks'
#             )
#             cau_agent_id = data[0]['cau_agent_id']
#             agent = User.objects.filter(id=cau_agent_id, user_role=6).values('name')
            
#             cau_admin = User.objects.filter(user_role=5).values('name')
            
#             result['status'] = "OK"
#             result['valid'] = True
#             result['result']['message'] = "Data updated successfully"
#             result['result']['cau_agent_id'] = agent
#             result['result']['cau_admin_id'] = cau_admin
#             result['result']['data'] = data
#             return Response(result, status=status.HTTP_200_OK)
#         except KeyError as e:
#             result['result']['message'] = f"KeyError: {str(e)} not found in request data"
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)
#         except ObjectDoesNotExist:
#             result['result']['message'] = "Id not found"
#             return Response(result, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             result['result']['message'] = f"An error occurred: {str(e)}"
#             return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# class ShowBasicInfo_RTOLeadtoSuperAdmin(APIView):
#     def post(self, request):
#         result = {
#             'status': "NOK",
#             'valid': False,
#             'result': {
#                 'message': "Data not Found",
#                 'data': []
#             }
#         }
#         get_district = request.data.get('district')
#         get_block = request.data.get('block')
#         get_source = request.data.get('source')
        
#         data = Registration.objects.all().filter(cau_admin_id=5, cau_lead_status = "All Criteria Fulfilled" )

        
#         if get_district:
#             data = data.filter(master__district = get_district)
#         if get_block:
#             data = data.filter(master__block_ulb = get_block)
#         if get_source:
#             data = data.filter(master__master_source = get_source)
            
#         result['status'] = "OK"
#         result['valid'] = True
#         result['result']['message'] = "Data retrieved successfully"
#         result['result']['data'] = data.values(
#                 'id', 'master__name', 'master__contact_number', 
#                 'master__district', 'master__block_ulb', 'wa_group_strength' )
        
# class AssignRTOLeadstoSuperAdmin (APIView):
#     def post(self, request):
#         result = {
#             'status': "NOK",
#             'valid': False,
#             'result': {
#                 'message': "Data not Found",
#                 'data': []
#             }
#         }        
#         try:
#             get_ids = request.data.get('ids')
#             sa_id = User.objects.filter(user_role_id = 1).values('id') 
#             data = Registration.objects.filter(id__in=get_ids).update(cau_sa_status=sa_id, cau_admin_assign_sa_date = datetime.today())
            
#             result['status'] = "OK"
#             result['valid'] = True
#             result['result']['message'] = "Data retrieved successfully"
#             result['result']['data'] = data.values('id')
#             return Response(result, status=status.HTTP_200_OK)
#         except KeyError as e:
#             result['result']['message'] = f"KeyError: {str(e)} not found in request data"
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)
#         except ObjectDoesNotExist:
#             result['result']['message'] = "Object not found"
#             return Response(result, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             result['result']['message'] = f"An error occurred: {str(e)}"
#             return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
# class ShowBasicInfo_AssignRTOLeadstoCOU(APIView):
#     def post(self, request):
#         result = {
#             'status': "NOK",
#             'valid': False,
#             'result': {
#                 'message': "Data not Found",
#                 'data': []
#             }
#         } 
#         try:
#             get_district = request.data.get('district')
#             get_block = request.data.get('block')
#             get_source = request.data.get('source')
            
#             sa_id = User.objects.filter(user_role_id = 1).values('id') 
#             data = Registration.objects.filter(cau_sa_status=sa_id)
            
#             if get_district:
#                 data = data.filter(master__district = get_district)
#             if get_block:
#                 data = data.filter(master__block_ulb = get_block)
#             if get_source:
#                 data = data.filter(master__master_source = get_source)
                
            
#             result['status'] = "OK"
#             result['valid'] = True
#             result['result']['message'] = "Data retrieved successfully"
#             result['result']['data'] = data.values(
#                     'id', 'master__name', 'master__contact_number', 
#                     'master__district', 'master__block_ulb', 'master__age' )
            
#             return Response(result, status=status.HTTP_200_OK)
#         except KeyError as e:
#             result['result']['message'] = f"KeyError: {str(e)} not found in request data"
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)
#         except ObjectDoesNotExist:
#             result['result']['message'] = "Object not found"
#             return Response(result, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             result['result']['message'] = f"An error occurred: {str(e)}"
#             return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class AssignRTOLeadstoCOU(APIView):
#     def post(self, request):
#         result = {
#             'status': "NOK",
#             'valid': False,
#             'result': {
#                 'message': "Data not Found",
#                 'data': []
#             }
#         }
#         try:
#             get_ids = request.data.get('ids') 
#             cou_id = User.objects.filter(user_role_id = 7).values('id')
            
#             data = Registration.objects.filter(id__in=get_ids).update(cou_admin_id = cou_id)
        
#             result['status'] = "OK"
#             result['valid'] = True
#             result['result']['message'] = "Data Updated successfully"
#             return Response(result, status=status.HTTP_200_OK)
#         except KeyError as e:
#             result['result']['message'] = f"KeyError: {str(e)} not found in request data"
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)
#         except ObjectDoesNotExist:
#             result['result']['message'] = "Object not found"
#             return Response(result, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             result['result']['message'] = f"An error occurred: {str(e)}"
#             return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
        
         


            
            
            
            
        
        
        