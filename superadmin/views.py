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
                'message': "Data not Found"
            }
        }
        data = request.data.get('leads')
        # get_district = request.data.get("district")
        # get_block = request.data.get("block")
        # get_source = request.data.get("source")
        
        if not data:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        ids_with_new_record_status_zero = Master.objects.filter(new_record_status=0).values('id')[:int(data)]
        # print(ids_with_new_record_status_zero.values('id'))
        registrations_created = []
        for lead_uid in ids_with_new_record_status_zero:
            try:
                # master_id = lead_uid['id']
                master = Master.objects.get(id=lead_uid['id'])
                registration = Registration.objects.create(
                    master=master,
                    lau_admin_id='3',
                    lau_created_date=datetime.now()
                )
                master.new_record_status = 1
                master.save()
                registrations_created.append(registration)
            except Master.DoesNotExist:
                pass
        
        result['status'] = "OK"
        result['valid'] = True
        result['result']['message'] = "Registrations created and new_record_status updated successfully"
        result['result']['data'] = {
            'lau_created_date': registration.lau_created_date,
            'lau_admin_id': registration.lau_admin_id,
            'registration_ids': [reg.id for reg in registrations_created]
        }
        
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
            if (get_dist == "" and get_block == "" and get_source == ""):
                result['count'] = all_data.count()
                result['data'] = all_data
            if get_dist != "":
                all_data = all_data.filter(master__district=get_dist)
                result['count'] = all_data.count()
                result['data'] = all_data
            if get_block != "":
                all_data = all_data.filter(master__block_ulb=get_block)
                result['count'] = all_data.count()
                result['data'] = all_data
            if get_source != "":
                all_data = all_data.filter(master__master_source=get_source)
                result['count'] = all_data.count()
                result['data'] = all_data

            result['status'] = "okay"
            result['valid'] = True
            result['data'] = all_data.values(
                'id', 'master__uid', 'master__name','master__district', 'master__block_ulb', 'master__master_source'
                )
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

        consent_agent_ids = request.data.get('agent_ids')
        get_dist = request.data.get("district")
        get_block = request.data.get("block")
        get_source = request.data.get("source")
        get_leads_count = int(request.data.get("leads_count", 0))

        if not consent_agent_ids:
            result['result']['message'] = "Please select consent agent"
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        all_data = Registration.objects.filter(lau_consent_agent_id__isnull=True).values(
            'id', 'master__district', 'master__block_ulb', 'master__master_source'
        )
        
        if len(all_data) < get_leads_count:
            result['result']['message'] = "Select leads count not greater than Available leads"
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        lead_ids_for_assign = []

        if get_source and not (get_dist or get_block):
            lead_ids_for_assign = [all_data[i]["id"] for i in range(get_leads_count)]

        elif get_dist and not (get_block or get_source):
            dist_data = all_data.filter(master__district=get_dist).values()
            lead_ids_for_assign = [dist_data[i]["id"] for i in range(get_leads_count)]

        elif get_dist and get_block and not get_source:
            dist_block_data = all_data.filter(master__district=get_dist, master__block_ulb=get_block).values()
            lead_ids_for_assign = [dist_block_data[i]["id"] for i in range(get_leads_count)]

        elif get_dist and get_block and get_source:
            dist_block_source_data = all_data.filter(master__district=get_dist, master__block_ulb=get_block, master__master_source=get_source).values()
            lead_ids_for_assign = [dist_block_source_data[i]["id"] for i in range(get_leads_count)]
        
        split_consent_ids = list(map(int, consent_agent_ids.split(",")))
        final_list = [lead_ids_for_assign[i:i + len(split_consent_ids)] for i in range(0, len(lead_ids_for_assign), len(split_consent_ids))]

        print("Length of final_list:", len(final_list))
        print("Length of split_consent_ids:", len(split_consent_ids))

        for index, leads in enumerate(final_list):
            print("Processing index:", index)
            if leads:
                consent_agent_id = split_consent_ids[index] if index < len(split_consent_ids) else None
                print("Using consent_agent_id:", consent_agent_id)
                Registration.objects.filter(id__in=leads).update(lau_consent_agent_id=consent_agent_id)

        assigned_leads = Registration.objects.filter(id__in=lead_ids_for_assign, lau_consent_agent_id__isnull=False).values(
            'id', 'master__uid', 'master__master_source', 'master__sub_source_name', 'master__source_contact_no',
            'master__political_category', 'master__name', 'master__contact_number', 'master__age', 'master__gender',
            'master__religion', 'master__category', 'master__caste', 'master__district', 'master__assembly',
            'master__rural_urban', 'master__block_ulb', 'master__panchayat_ward', 'master__village_habitation',
            'master__occupation', 'master__profile', 'master__whatsapp_user', 'master__whatsapp_number',
            'master__new_record_status', 'lau_consent_agent_id'
        )

        result['status'] = "OK"
        result['valid'] = True
        result['result']['message'] = "Leads assigned successfully"
        result['result']['data'] = assigned_leads

        return Response(result, status=status.HTTP_200_OK)

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
                ids_to_update = Registration.objects.filter(lau_consent_agent_id__isnull = True , master__new_record_status=1)[:tasks_count]
                print(ids_to_update.values('id'))
                print(len(ids_to_update))
                
                if len(ids_to_update) < tasks_count:
                    result['result']['message'] = "Invalid task/ Provide more Leads"
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
                try :
                    i = 0
                    res = []
                    for ids in member_ids:
                        for task in range(0,distribution_result[ids]):
                            register = Registration.objects.filter(id = ids_to_update[i].id).update(lau_consent_agent_id=ids)
                            res.append(register)
                            i= i+1

                    print('register : ', res)
                except Exception as err:
                    result['status'] = "NOK"
                    result['valid'] = False
                    result['result']['message'] = str(err)
                    return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                result['status'] = "OK"
                result['valid'] = True
                result['result']['message'] = "Data Fetched Successfully"
                result['result']['data'] = distribution_result
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                result['status'] = "NOK"
                result['valid'] = False
                result['result']['message'] = str(e)
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        
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
            lau_id = request.data['lau_id']
            get_district = request.data['district']
            get_block = request.data['block']
            get_call_status = request.data['call_status']
            get_lead_status = request.data['lead_status']
            
            # Retrieve relevant data for the given LAU agent ID
            data = Registration.objects.filter(
                lau_consent_agent_id=lau_id
            ).values(
                'id', 'master__uid', 'master__name', 'master__contact_number', 'master__district',
                'lau_consent_call_status', 'lau_consent_call_status_2', 'lau_consent_call_status_3',
                'lau_consent_lead_status', 'lau_consent_lead_status_2', 'lau_consent_lead_status_3',
                'lau_consent_followup_date_time', 'lau_consent_followup_date_time_2', 'lau_consent_followup_date_time_3'
            ).order_by('id')
            
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
            result['result']['data'] = data
            
            return Response(result, status=status.HTTP_200_OK)
        except KeyError:
            result['result']['message'] = "Missing or invalid `inp`ut"
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
            result['result']['data'] = list(data)
            
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
            get_id = request.data.get('id')
            reg_instance = Registration.objects.get(id=get_id)
            master_lead_id = reg_instance.master_id
            
            update_data = {
                'sub_source_name': request.data.get('sub_source_name'),
                'source_contact_no': request.data.get('source_contact_no'),
                'political_category': request.data.get('political_category'),
                'name': request.data.get('name'),
                'age': request.data.get('age'),
                'gender': request.data.get('gender'),
                'religion': request.data.get('religion'),
                'category': request.data.get('category'),
                'caste': request.data.get('caste'),
                'district': request.data.get('district'),
                'assembly': request.data.get('assembly'),
                'rural_urban': request.data.get('rural_urban'),
                'block_ulb': request.data.get('block_ulb'),
                'panchayat_ward': request.data.get('panchayat_ward'),
                'village_habitation': request.data.get('village_habitation'),
                'occupation': request.data.get('occupation'),
                'profile': request.data.get('profile'),
                'whatsapp_user': request.data.get('whatsapp_user'),
                'whatsapp_number': request.data.get('whatsapp_number'),
                'other_caste': request.data.get('other_caste')
            }

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
            get_call_status = request.data['call_status']
            get_lead_status = request.data['lead_status']
            get_follow_date_time = request.data['follow_date_time']
            get_remarks = request.data['remarks']
            
            registration_data = {
                'lau_consent_call_status' : get_call_status,
                'lau_consent_lead_status' : get_lead_status,
                'lau_last_updated_date_time': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                'lau_consent_remarks' : get_remarks
            }
            Registration.objects.filter(id=get_id).update(**registration_data)
            data = Registration.objects.filter(id=get_id).values()
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data updated successfully"
            result['result']['data'] = list(data)
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
        
# LAU Admin - Assign Leads-Consent      
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
        
        data = Registration.objects.all().filter(lau_consent_agent_id__isnull = False)
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
        
class LAUAdminWAtoSuperAdmin(APIView):
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
        
        data = Registration.objects.all().filter(lau_consent_agent_id__isnull = False).exclude(Q (lau_lead_status = "All Criteria Fulfilled Consent") | Q (lau_lead_status__isnull = False))
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
        