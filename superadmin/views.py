from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status  
from django.db import IntegrityError
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
        try:
            district = request.data['district']  # Get the 'district' from request data
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
        except KeyError:
            result['result']['message'] = "Missing required parameters."
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        try:
            get_dist = request.data['district']
            get_block = request.data['block']
            get_source = request.data['source']

            total_data = Registration.objects.filter(lau_consent_agent_id__isnull=True)
            
            if get_dist:
                total_data = total_data.filter(master__district=get_dist)
            if get_block:
                total_data = total_data.filter(master__block_ulb=get_block)
            if get_source:
                total_data = total_data.filter(master__master_source=get_source)
            
            result['count'] = total_data.count()
            
            if result['count'] == 0:
                result['result']['message'] = "No data found."
                return Response(result, status=status.HTTP_404_NOT_FOUND)
            
            result['data'] = total_data.values(
                'id', 'master__uid', 'master__name', 'master__district',
                'master__block_ulb', 'master__master_source'
            )
            
            result['status'] = "okay"
            result['valid'] = True
            result['result'] = {"message": "Data fetched successfully"}
            
            return Response(result, status=status.HTTP_200_OK)
        except KeyError:
            result['result']['message'] = "Missing required parameters."
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

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
        try:
            get_district = request.data['district']
            get_block = request.data['block']
            get_source = request.data['source']
            
            lau_id = User.objects.filter(user_role_id=2).values('id')
            data = request.data['leads']
            
            if not data:
                result['result']['message'] = "No leads provided."
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                num_leads = int(data)
            except ValueError:
                result['result']['message'] = "Invalid format for leads."
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            if num_leads <= 0:
                result['result']['message'] = "Number of leads must be greater than zero."
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            ids_with_new_record_status_zero = Master.objects.filter(new_record_status=0).values('id')[:num_leads]
            master_ids = [item['id'] for item in ids_with_new_record_status_zero]
            
            registrations_to_create = []
            master_objects_to_update = []
            
            if master_ids:
                master_objects = Master.objects.filter(id__in=master_ids)
                
                if get_district or get_block or get_source:
                    total_data = Registration.objects.filter(lau_consent_agent_id__isnull=True)
                    if get_district:
                        total_data = total_data.filter(master__district=get_district)
                    if get_block:
                        total_data = total_data.filter(master__block_ulb=get_block)
                    if get_source:
                        total_data = total_data.filter(master__master_source=get_source)
                    
                    for master_obj in master_objects:
                        try:
                            registration = Registration(
                                master=master_obj, lau_admin_id=lau_id,
                                lau_created_date=datetime.now()
                            )
                            registrations_to_create.append(registration)
                            master_objects_to_update.append(master_obj)
                        except Master.DoesNotExist:
                            pass
                else:
                    for master_obj in master_objects:
                        try:
                            registration = Registration(
                                master=master_obj, lau_admin_id=lau_id,
                                lau_created_date=datetime.now()
                            )
                            registrations_to_create.append(registration)
                            master_objects_to_update.append(master_obj)
                        except Master.DoesNotExist:
                            pass
                
                if registrations_to_create:
                    try:
                        Registration.objects.bulk_create(registrations_to_create)
                    except IntegrityError as e:
                        result['result']['message'] = f"An error occurred while creating registrations: {str(e)}"
                        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            Master.objects.filter(id__in = master_ids).update(new_record_status = 1 )
            
            result['status'] = "okay"
            result['valid'] = True
            result['result'] = {"message": "Registrations created successfully"}
            result['result']['Updated Ids'] = master_ids
            
            return Response(result, status=status.HTTP_201_CREATED)
        except KeyError:
            result['result']['message'] = "Missing required parameters."
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

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
        
        try:
            agents = User.objects.filter(user_role=3, current_status=1).values()
            
            if agents.count() == 0:
                result['result']['message'] = "Agents aren't available"
                return Response(result, status=status.HTTP_404_NOT_FOUND)
            
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data Fetched Successfully"
            result['result']['count'] = agents.count()
            result['result']['data'] = agents
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            result['result']['message'] = f"An error occurred: {str(e)}"
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
            try:
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
            except KeyError:
                result['result']['message'] = "Missing required parameters."
                return Response(result, status=status.HTTP_400_BAD_REQUEST)       
        
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
            tasks_count = int(request.data['leads_count'])
            member_ids = request.data['agent_ids']
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
                    Registration.objects.filter(id__in=temp_ids).update(lau_consent_agent_id=agent_id)
                    updated_ids.extend(temp_ids)
                    
                result['status'] = "OK"
                result['valid'] = True
                result['result']['message'] = "Data Fetched Successfully"
                result['result']['data'] = distribution_result
                result['result']['Updated Ids'] = updated_ids
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                result['result']['message'] = str(e)
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError:
            result['result']['message'] = "Missing required parameters."
            return Response(result, status=status.HTTP_400_BAD_REQUEST)     
        
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
            lau_id = request.data['lau_agent_id']
            get_district = request.data['district']
            get_block = request.data['block']
            get_call_status = request.data['call_status']
            get_lead_status = request.data['lead_status']
            
            # Retrieve relevant data for the given LAU agent ID
            try:
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
            except Exception as e:
                result['result']['message'] = str(e)
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response(result, status=status.HTTP_200_OK)
        except KeyError:
            result['result']['message'] = "Missing or invalid input"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

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
            try: 
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
            except Exception as e:
                result['result']['message'] = str(e)
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError:
            result['result']['message'] = "Missing or invalid input"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
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
            get_id = request.data['lead_id']
            reg_instance = Registration.objects.get(id=get_id)
            master_lead_id = reg_instance.master_id
            
            fields_to_update = [
                'master_source', 'sub_source_name', 'source_contact_no', 'political_category',
                'name', 'age', 'contact_number', 'gender', 'religion', 'category', 'caste', 'district', 'assembly',
                'rural_urban', 'block_ulb', 'panchayat_ward', 'village_habitation',
                'occupation', 'profile', 'whatsapp_user', 'whatsapp_number', 'other_caste'
            ]
            update_data = {}
            missing_fields = []
            
            for field in fields_to_update:
                try:
                    update_data[field] = request.data[field]
                except KeyError:
                    missing_fields.append(field)
            
            if missing_fields:
                result['result']['message'] = "Missing or invalid input"
                result['result']['missing_fields'] = missing_fields
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            try:
                Master.objects.filter(id=master_lead_id).update(**update_data)

                result['status'] = "OK"
                result['valid'] = True
                result['result']['message'] = "Data updated successfully"
                result['result']['Updated data'] = update_data
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                result['result']['message'] = "An error occurred"
                result['result']['error'] = str(e)
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError:
            result['result']['message'] = "Missing or invalid input"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
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
        try:
            get_district = request.data['district']
            get_block = request.data['block']
            get_source = request.data['source']
            try:
                data = Registration.objects.all().filter(
                    lau_consent_agent_id__isnull = False, 
                    lau_consent_lead_status = 'All Criteria Fulfilled Consent')
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
            except Exception as e:
                result['result']['message'] = f"An error occurred: {str(e)}"
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError:
            result['result']['message'] = "Missing or invalid input"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
     
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
            get_lead_ids_str = request.data['lead_ids']
            get_lead_ids = [int(lead_id) for lead_id in get_lead_ids_str.split(',')]
            
            get_agent_ids_str = request.data['agent_ids']
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
                        lau_consent_agent_id__isnull=True
                    ).order_by('id')[:agent_id_to_assign]

                temp_ids = list(temp.values_list('id', flat=True))
                Registration.objects.filter(id__in=temp_ids).update(lau_consent_agent_id=agent_id)
                updated_ids.extend(temp_ids)
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data retrieved successfully"
            result['result']['distribution'] = distribution_result
            result['result']['ids'] = updated_ids
            return Response(result, status=status.HTTP_200_OK)
        except KeyError as e:
            result['result']['message'] = "Invalid data format provided."
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            result['result']['message'] = f"An error occurred while processing the request.{str(e)}"
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
        try:
            get_district = request.data['district']
            get_block = request.data['block']
            get_source = request.data['source']
            try:
                data = Registration.objects.all().filter(
                    lau_consent_agent_id__isnull = False, 
                    lau_lead_status = "All Criteria Fulfilled WA")
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
            except Exception as e:
                result['result']['message'] = f"An error occurred while processing the request.{str(e)}"
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e:
            result['result']['message'] = "Invalid data format provided."
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
  
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
            get_ids_str = request.data['ids']
            get_ids = [int(agent_id) for agent_id in get_ids_str.split(',')]
            sa_id = User.objects.filter(user_role_id = 1).values('id') 
            try:
                data = Registration.objects.filter(id__in=get_ids).update(
                    lau_sa_status=sa_id, 
                    lau_admin_assign_sa_date = datetime.today())
                
                result['status'] = "OK"
                result['valid'] = True
                result['result']['message'] = "Data retrieved successfully"
                result['result']['data'] = data
                result['result']['ids'] = get_ids
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                result['result']['message'] = f"An error occurred: {str(e)}"
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e:
            result['result']['message'] = f"KeyError: {str(e)} not found in request data"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            result['result']['message'] = "Object not found"
            return Response(result, status=status.HTTP_404_NOT_FOUND)
  
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
            get_district = request.data['district']
            get_block = request.data['block']
            get_source = request.data['source']
            try:
                sa_id = User.objects.filter(user_role_id = 1).values('id')
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
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e:
            result['result']['message'] = f"KeyError: {str(e)} not found in request data"
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
            get_ids_str = request.data['ids']
            get_ids = [int(agent_id) for agent_id in get_ids_str.split(',')]
            try:
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
            except ObjectDoesNotExist:
                result['result']['message'] = "Object not found"
                return Response(result, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                result['result']['message'] = f"An error occurred: {str(e)}"
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e:
            result['result']['message'] = f"KeyError: {str(e)} not found in request data"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
   
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
            try:
                sa_id = User.objects.filter(user_role_id = 1).values('id')
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
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e:
            result['result']['message'] = f"KeyError: {str(e)} not found in request data"
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
            get_ids_str = request.data['ids']
            get_ids = [int(agent_id) for agent_id in get_ids_str.split(',')]
            try:
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
            except Exception as e:
                result['result']['message'] = f"An error occurred: {str(e)}"
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ObjectDoesNotExist:
            result['result']['message'] = "Object not found"
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        except KeyError as e:
                result['result']['message'] = f"KeyError: {str(e)} not found in request data"
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
   