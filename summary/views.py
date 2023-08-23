from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from datetime import datetime,timedelta
from django.db.models import Q
import csv
import codecs
import tempfile
from .models import *
import pandas as pd
# import chardet
import requests
from functools import reduce

def validatedate(date_text):
    try:
        datetime.strptime(date_text,'%Y-%m-%d')
        return True
    except :
        return False

# Total unassignd consent leads
class TotalUnassignedLAUleads(APIView):
    def post(self,request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access"}
        if request.user.is_authenticated:
            inp_dist = request.data["district"]
            inp_block = request.data["block"]
            inp_source = request.data["source"]
            all_data = Registration.objects.filter(lau_consent_agent_id__isnull=True).values('id', 'master__uid', 'master__name', 'master__district','master__block_ulb',  'master__master_source')
            if (inp_dist == "" and inp_block == "" and inp_source == ""):
                result['count'] = all_data.count()
                result['data'] = all_data
            if inp_dist != "":
                all_data = all_data.filter(master__district=inp_dist).values('id', 'master__uid', 'master__name', 'master__district', 'master__block_ulb', 'master__master_source')
                result['count'] = all_data.count()
                result['data'] = all_data
            if inp_block != "":
                all_data = all_data.filter(master__nblock_ulb=inp_block).values('id', 'master__uid', 'master__name', 'master__district', 'master__block_ulb', 'master__master_source')
                result['count'] = all_data.count()
                result['data'] = all_data
            if inp_source != "":
                all_data = all_data.filter(master__master_source=inp_source).values('id', 'master__uid', 'master__name', 'master__district', 'master__block_ulb', 'master__master_source')
                result['count'] = all_data.count()
                result['data'] = all_data

            result['status'] = "okay"
            result['valid'] = True
            result['result'] = {"message": "Data fetched successfully"}
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class LauConsentAgents(APIView, PageNumberPagination):
    def post(self,request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access", "data":[]}
        if request.user.is_authenticated:
            page_size = request.data["page_size"]
            data1 = User.objects.filter(user_role=3,current_status=1).values()
            if len(data1) == 0:
                result['result']['message'] = "No consent agents available now"
                return Response(result, status=status.HTTp)
            if page_size=='':
                page_size=10
            PageNumberPagination.page_size=page_size
            paginated_data = self.paginate_queryset(data1, request, view=self)
            paginated_data = self.get_paginated_response(paginated_data).data
            result['status'] = "okay"
            result['valid'] = True
            result['result'] = {"message": "Data fetched successfully"}
            result['result']['next'] = paginated_data['next']
            result['result']['previous'] = paginated_data['previous']
            result['result']['count'] = paginated_data['count']
            result['result']['data'] = paginated_data['results']
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_OK)

#Lau leads Auto assign to Consent Agents
class LauAssiginLeadsToConsent(APIView):
    def post(self,request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access", "data":[]}
        if request.user.is_authenticated:
            consent_agent_ids = request.data['agent_ids']
            inp_dist = request.data["district"]
            inp_block = request.data["block"]
            inp_source = request.data["source"]
            inp_leads_count = request.data["leads_count"]
            if consent_agent_ids == "":
                result['result']['message'] = "Please select consent agent"
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            all_data = Registration.objects.filter(lau_consent_agent_id__isnull=True).values('id','master__district','master__block_ulb','master__master_source')
            if len(all_data) < int(inp_leads_count):
                result['result']['message'] = "Select leads count not greater than Available leads"
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            lead_ids_for_assign = []
            if (inp_dist == "" and inp_block == "" and inp_source == ""):
                lead_ids_for_assign = [all_data[l]["id"] for l in range(0,int(inp_leads_count))]

            elif inp_source != "" and (inp_dist == "" and inp_block == ""):
                source_data = all_data.filter(master__master_source=inp_source).values()
                lead_ids_for_assign = [source_data[l]["id"] for l in range(0,int(inp_leads_count))]

            elif inp_dist != "" and (inp_block == "" and inp_source == ""):
                dist_data = all_data.filter(master__district=inp_dist).values()
                lead_ids_for_assign = [dist_data[l]["id"] for l in range(0,int(inp_leads_count))]

            elif (inp_dist != "" and inp_block != "") and inp_source == "":
                dist_block_data = all_data.filter(master__district=inp_dist, master__block_ulb=inp_block).values()
                lead_ids_for_assign = [dist_block_data[l]["id"] for l in range(0,int(inp_leads_count))]

            elif inp_dist != "" and inp_block != "" and inp_source != "":
                dist_block_source_data = all_data.filter(master__district=inp_dist, master__block_ulb=inp_block, master__master_source=inp_source).values()
                lead_ids_for_assign = [dist_block_source_data[l]["id"] for l in range(0,int(inp_leads_count))]

            split_consent_ids = list(map(int,consent_agent_ids.split(",")))
            k, m = divmod(len(lead_ids_for_assign), len(split_consent_ids))
            final_list = list((list(lead_ids_for_assign[i*k+min(i, m):(i+1)*k+min(i+1, m)]) for i in range(len(split_consent_ids))))
            for index, leads in enumerate(final_list):
                if len(leads) > 0:
                    Registration.objects.filter(id__in=leads).update(lau_consent_agent_id=split_consent_ids[index])
            assigned_leads = Registration.objects.filter(id__in=lead_ids_for_assign,lau_consent_agent_id__isnull=False).values('id','master__uid','master__master_source','master__sub_source_name','master__source_contact_no',
                                                                                                                               'master__political_category','master__name','master__contact_number','master__age','master__gender',
                                                                                                                               'master__religion','master__category','master__caste','master__district','master__assembly','master__rural_urban',
                                                                                                                               'master__block_ulb','master__panchayat_ward','master__village_habitation','master__occupation','master__profile',
                                                                                                                               'master__whatsapp_user','master__whatsapp_number','master__new_record_status','lau_consent_agent_id')
            result['status'] = "okay"
            result['valid'] = True
            result['result']['message'] = "Leads assigned successfully"
            result['result']['data'] = assigned_leads
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_OK)

class DistrictListing(APIView):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            district_type = request.data['district_type']
            if district_type != "":
                district = DistrictMapping.objects.filter(district_type=district_type).values('district_name').distinct()
            else:
                district = DistrictMapping.objects.all().values('district_name').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = district
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class ACListing(APIView):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            district_type = request.data['district_type']
            district_name = request.data['district_name']
            if district_type == "Rural":
                aclisting = DistrictMapping.objects.filter(district_type="Rural",district_name=district_name).values('ac_name').distinct()
                message = "Data fetched successfully"
            else:
                aclisting = []
                message = "Please select correct distinct and district type"
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = message
            result['result']['data'] = aclisting
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class BlockListing(APIView):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            ac_name = request.data['ac_name']
            district_name = request.data['district_name']
            if ac_name != "":
                blocklisting = DistrictMapping.objects.filter(ac_name=ac_name).values('block_name').distinct()
            else:
                blocklisting = DistrictMapping.objects.filter(district_name=district_name).values('block_name').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = blocklisting
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class GPListing(APIView):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            block_name = request.data['block_name']
            gplisting = DistrictMapping.objects.filter(block_name=block_name).values('gp_name').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = gplisting
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class MunicipalityListing(APIView):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            block_name = request.data['block_name']
            municipalitylisting = DistrictMapping.objects.filter(block_name=block_name).values('municipality_name').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = municipalitylisting
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class WardListing(APIView):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            municipality_name = request.data['municipality_name']
            wardlisting = DistrictMapping.objects.filter(municipality_name=municipality_name).values('ward_name').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = wardlisting
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class VillageListing(APIView):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            gp_name = request.data['gp_name']
            villagelisting = DistrictMapping.objects.filter(gp_name=gp_name).values('village_name').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = villagelisting

            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class CasteListing(APIView):
    def get(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            castelisting = Caste.objects.all().values('caste_name').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = castelisting
            
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class CategoryListing(APIView):
    def get(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            categorylisting = Category.objects.all().values('category_name').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = categorylisting
            
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class OccupationListing(APIView):
    def get(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            occupationlisting = Occupation.objects.all().values('occupation_name').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = occupationlisting
            
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class ReligionListing(APIView):
    def get(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            religionlisting = Religion.objects.all().values('religion_name').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = religionlisting
            
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class GenderListing(APIView):
    def get(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            genderlisting = Gender.objects.all().values('gender_type').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = genderlisting
            
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class DataSourceListing(APIView):
    def get(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if  request.user.is_authenticated:
            sourcenamelisting = DataSource.objects.all().values('source_name').distinct()
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = sourcenamelisting
            
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class WALeadListing(APIView, PageNumberPagination):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if request.user.is_authenticated:
            district_name = request.data['district_name']
            block_name = request.data['block_name']
            data_source_name = request.data['source_name']
            page_size=request.data['page_size']
            if page_size=='':
                page_size=10
            PageNumberPagination.page_size=page_size
            data = Registration.objects.filter(lau_lead_status="All Criteria Fulfilled WA").values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','master__age').order_by('id')

            if district_name!='':
                data=data.filter(master__district=district_name)
                
            if block_name!='':
                data=data.filter(master__block_ulb=block_name)

            if data_source_name!='':
                data=data.filter(master__master_source=data_source_name)
            total_count = data.count() 
            paginated_data = self.paginate_queryset(data , request, view=self)
            paginated_data= self.get_paginated_response(paginated_data).data
            result['status'] = "OK"
            result['valid']  = True
            result['total_count'] = total_count
            result['result']['message']  = "Data fetched successfully"
            result['result']['next']     = paginated_data['next']
            result['result']['previous'] = paginated_data['previous']
            result['result']['count']    = paginated_data['count']
            result['result']['data']     = paginated_data['results']
            return Response(result, status=status.HTTP_200_OK)
                        
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class WALeadDistributionBySuperAdmin(APIView, PageNumberPagination):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if request.user.is_authenticated:
            if request.user.user_role_id == 1:
                cauAdminid = list(User.objects.filter(user_role_id = 5).values_list('id',flat=True))
                ids = request.data['ids']
                lead_ids = list(map(int,ids.split(',')))
                timenow = (datetime.today()).strftime('%Y-%m-%d %H:%M:%S')
                data = Registration.objects.filter(id__in=lead_ids).values()
                total_count = data.count() 
                for i in cauAdminid:
                    data1 = data.update(cau_created_date=timenow,cau_admin_id=i)
                
                paginated_data = self.paginate_queryset(data , request, view=self)
                paginated_data= self.get_paginated_response(paginated_data).data
                result['status'] = "OK"
                result['valid']  = True
                result['total_count'] = total_count
                result['result']['message']  = "Data fetched successfully"
                result['result']['next']     = paginated_data['next']
                result['result']['previous'] = paginated_data['previous']
                result['result']['count']    = paginated_data['count']
                result['result']['data']     = paginated_data['results']
                return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class RTOLeadListing(APIView, PageNumberPagination):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if request.user.is_authenticated:
            district_name = request.data['district_name']
            block_name = request.data['block_name']
            data_source_name = request.data['source_name']
            page_size=request.data['page_size']
            if page_size=='':
                page_size=10
            PageNumberPagination.page_size=page_size
            data = Registration.objects.filter(cau_lead_status="RTO").values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','master__age').order_by('id')

            if district_name!='':
                data=data.filter(master__district=district_name)
                
            if block_name!='':
                data=data.filter(master__block_ulb=block_name)

            if data_source_name!='':
                data=data.filter(master__master_source=data_source_name)
            total_count = data.count() 
            paginated_data = self.paginate_queryset(data , request, view=self)
            paginated_data= self.get_paginated_response(paginated_data).data
            result['status'] = "OK"
            result['valid']  = True
            result['total_count'] = total_count
            result['result']['message']  = "Data fetched successfully"
            result['result']['next']     = paginated_data['next']
            result['result']['previous'] = paginated_data['previous']
            result['result']['count']    = paginated_data['count']
            result['result']['data']     = paginated_data['results']
            return Response(result, status=status.HTTP_200_OK)
                        
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class RTOLeadDistributionBySuperAdmin(APIView, PageNumberPagination):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if request.user.is_authenticated:
            if request.user.user_role_id == 1:
                couAdminid = list(User.objects.filter(user_role_id = 7).values_list('id',flat=True))
                ids = request.data['ids']
                lead_ids = list(map(int,ids.split(',')))
                timenow = (datetime.today()).strftime('%Y-%m-%d %H:%M:%S')
                data = Registration.objects.filter(id__in=lead_ids).values()
                total_count = data.count() 
                for i in couAdminid:
                    data1 = data.update(cau_created_date=timenow,cau_admin_id=i)
                
                paginated_data = self.paginate_queryset(data , request, view=self)
                paginated_data= self.get_paginated_response(paginated_data).data
                result['status'] = "OK"
                result['valid']  = True
                result['total_count'] = total_count
                result['result']['message']  = "Data fetched successfully"
                result['result']['next']     = paginated_data['next']
                result['result']['previous'] = paginated_data['previous']
                result['result']['count']    = paginated_data['count']
                result['result']['data']     = paginated_data['results']
                return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class InauguratedLeadListing(APIView, PageNumberPagination):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if request.user.is_authenticated:
            start_date = request.data['start_date']
            end_date = request.data['end_date']
            district_name = request.data['district_name']
            block_name = request.data['block_name']
            data_source_name = request.data['source_name']
            page_size=request.data['page_size']
            
            if page_size=='':
                page_size=10
            PageNumberPagination.page_size=page_size
            
            if start_date=="" and end_date =="":
                start_date= "2022-06-17"
                end_date=(datetime.today()).strftime('%Y-%m-%d')

            elif (start_date=="" and end_date!="") or (start_date!="" and end_date==""):
                if start_date=="":
                    result['valid']=True
                    result['result']['message']="start date cannot be empty"
                else:
                    result['valid']=True
                    result['result']['message']="end date cannot be empty"
                return Response (result,status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not validatedate(start_date):
                result['valid']=True
                result['result']['message']="Invalid start date format, valid format yyyy-mm-dd"
                return Response(result,status= status.HTTP_422_UNPROCESSABLE_ENTITY)
    
            if not validatedate(end_date):
                result['valid']=True
                result['result']['message']="Invalid end date format, valid format yyyy-mm-dd"
                return Response(result,status= status.HTTP_422_UNPROCESSABLE_ENTITY)

            if(end_date<start_date):
                result['valid']=True
                result['result']['message']="end date should not be less than start date"
                return Response (result,status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            else:
                end_date=( datetime.strptime(end_date,'%Y-%m-%d') +timedelta(days=1)).strftime('%Y-%m-%d')
            
            data = Registration.objects.filter(cou_lead_status="Inaugurated",cou_followup_date_time__range=(start_date,end_date)).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','cou_followup_date_time','master__age').order_by('id')

            if district_name!='':
                data=data.filter(master__district=district_name)
                
            if block_name!='':
                data=data.filter(master__block_ulb=block_name)

            if data_source_name!='':
                data=data.filter(master__master_source=data_source_name)
            total_count = data.count() 
            paginated_data = self.paginate_queryset(data , request, view=self)
            paginated_data= self.get_paginated_response(paginated_data).data
            result['status'] = "OK"
            result['valid']  = True
            result['total_count'] = total_count
            result['result']['message']  = "Data fetched successfully"
            result['result']['next']     = paginated_data['next']
            result['result']['previous'] = paginated_data['previous']
            result['result']['count']    = paginated_data['count']
            result['result']['data']     = paginated_data['results']
            return Response(result, status=status.HTTP_200_OK)
                        
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class LauTotalWaAgents(APIView):
    def get(self,request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access", "data":[]}
        if request.user.is_authenticated:
            #data1 = User.objects.filter(user_role__in=[3,4],current_status=1).values()
            data1 = User.objects.filter(user_role_id=3,current_status=1).values()
            if len(data1) == 0:
                result['result']['message'] = "No WA agents available now"
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            result['status'] = "okay"
            result['valid'] = True
            result['result'] = {"message": "Data fetched successfully"}
            result['result']['data'] = data1
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_OK)

class TotalAluConsentleads(APIView, PageNumberPagination):
    def post(self,request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}
        if request.user.is_authenticated:
            inp_dist = request.data["district"]
            inp_block = request.data["block"]
            inp_source = request.data["source"]
            inp_page = request.data["page_size"]

            all_data = Registration.objects.filter(lau_consent_lead_status="All Criteria Fulfilled Consent", lau_wa_agent_id__isnull=True).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','lau_consent_call_status','lau_consent_lead_status')
            if (inp_dist == "" and inp_block == "" and inp_source == ""):
                consentleads = all_data

            elif inp_source != "" and (inp_dist == "" and inp_block == ""):
                consentleads = all_data.filter(master__master_source=inp_source).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','lau_consent_call_status','lau_consent_lead_status')

            elif inp_dist != "" and (inp_block == "" and inp_source == ""):
                consentleads = all_data.filter(master__district=inp_dist).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','lau_consent_call_status','lau_consent_lead_status')

            elif (inp_dist != "" and inp_block != "") and inp_source == "":
                consentleads = all_data.filter(master__district=inp_dist, master__block_ulb=inp_block).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','lau_consent_call_status','lau_consent_lead_status')

            elif (inp_dist != "" and inp_source != "") and inp_block == "":
                consentleads = all_data.filter(master__district=inp_dist, master__master_source=inp_source).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','lau_consent_call_status','lau_consent_lead_status')

            elif inp_dist != "" and inp_block != "" and inp_source != "":
                consentleads = all_data.filter(master__district=inp_dist, master__block_ulb=inp_block, master__master_source=inp_source).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','lau_consent_call_status','lau_consent_lead_status')

            if len(consentleads) == 0:
                result['result']['message'] = "No consent leads available now"
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if inp_page == '':
                inp_page = 10
            PageNumberPagination.page_size = inp_page
            paginated_data = self.paginate_queryset(consentleads, request, view=self)
            paginated_data = self.get_paginated_response(paginated_data).data
            result['status'] = "okay"
            result['valid'] = True
            result['result'] = {"message": "Data fetched successfully"}
            result['total_count'] = consentleads.count()
            result['result']['next'] = paginated_data['next']
            result['result']['previous'] = paginated_data['previous']
            result['result']['count'] = paginated_data['count']
            result['result']['data'] = paginated_data['results']
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_OK)

class LauAdminAssiginConsentToWaAgent(APIView):
    def post(self,request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access"}
        if request.user.is_authenticated:
            wa_agent_ids = request.data['agent_ids']
            consent_leads_ids = request.data["leads"]
            if wa_agent_ids == "":
                result['result']['message'] = "Please select WA agent"
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if consent_leads_ids == "":
                result['result']['message'] = "Please select Consent leads"
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            split_wa_ids = list(map(int, wa_agent_ids.split(",")))
            split_consent_leads = list(map(int, consent_leads_ids.split(",")))

            k, m = divmod(len(split_consent_leads), len(split_wa_ids))
            final_list = list((list(split_consent_leads[i*k+min(i, m):(i+1)*k+min(i+1, m)]) for i in range(len(split_wa_ids))))

            assign_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            for ind, n in enumerate(final_list):
                if len(n) > 0:
                    Registration.objects.filter(id__in=n, lau_consent_lead_status="All Criteria Fulfilled Consent").update(lau_wa_agent_id=split_wa_ids[ind],lau_wa_assign_date=assign_date)
            result['status'] = "okay"
            result['valid'] = True
            result['result']['message'] = "Leads assigned successfully"
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_OK)

# Total wa completed leads
class LauWaCompletedLeads(APIView, PageNumberPagination):
    def post(self,request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access", "data":[]}
        if request.user.is_authenticated:
            inp_dist = request.data["district"]
            inp_block = request.data["block"]
            inp_source = request.data["source"]
            page_size=request.data['page_size']

            all_data = Registration.objects.filter(lau_lead_status="All Criteria Fulfilled WA",lau_sa_status__isnull=True).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','wa_group_strength','lau_lead_status')
            if (inp_dist == "" and inp_block == "" and inp_source == ""):
                waleads = all_data

            elif inp_source != "" and (inp_dist == "" and inp_block == ""):
                waleads = all_data.filter(master__master_source=inp_source).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','wa_group_strength','lau_lead_status')

            elif inp_dist != "" and (inp_block == "" and inp_source == ""):
                waleads = all_data.filter(master__district=inp_dist).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','wa_group_strength','lau_lead_status')

            elif (inp_dist != "" and inp_block != "") and inp_source == "":
                waleads = all_data.filter(master__district=inp_dist, master__block_ulb=inp_block).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','wa_group_strength','lau_lead_status')

            elif (inp_dist != "" and inp_source != "") and inp_block == "":
                waleads = all_data.filter(master__district=inp_dist, master__master_source=inp_source).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','wa_group_strength','lau_lead_status')

            elif inp_dist != "" and inp_block != "" and inp_source != "":
                waleads = all_data.filter(master__district=inp_dist, master__block_ulb=inp_block, master__master_source=inp_source).values('id','master__uid','master__master_source','master__name','master__contact_number','master__district','master__block_ulb','wa_group_strength','lau_lead_status')

            if len(waleads) == 0:
                result['result']['message'] = "No WA leads available now"
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if page_size == '':
                page_size = 10
            PageNumberPagination.page_size = page_size
            paginated_data = self.paginate_queryset(waleads, request, view=self)
            paginated_data = self.get_paginated_response(paginated_data).data
            result['status'] = "okay"
            result['valid'] = True
            result['result'] = {"message": "Data fetched successfully"}
            result['total_count'] = waleads.count()
            result['result']['next'] = paginated_data['next']
            result['result']['previous'] = paginated_data['previous']
            result['result']['count'] = paginated_data['count']
            result['result']['data'] = paginated_data['results']
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_OK)

class LauWALeadAssignToSuperAdmin(APIView):
    def post(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": []}

        if request.user.is_authenticated:
            superadmin = User.objects.filter(user_role_id=1).values('id')
            superadmin_id = superadmin[0]["id"]
            inp_ids = request.data['ids']
            lead_ids = list(map(int, inp_ids.split(',')))
            timenow = (datetime.today()).strftime('%Y-%m-%d %H:%M:%S')
            Registration.objects.filter(id__in=lead_ids).update(lau_admin_assign_sa_date = timenow, lau_sa_status = superadmin_id)
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Leads assigin to Super Admin successfully"
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

class UploadingNewLeads(APIView):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access"}
        if request.user.is_authenticated:
            if request.user.user_role_id == 1:
                file_link = request.data["filelink"]
                if not file_link:
                    # Handle the case when the file link is not provided.
                    return Response("File link is missing.", status=status.HTTP_400_BAD_REQUEST)
                try:
                    data_list = []
                    df = pd.read_csv(file_link)
                    df['age'].fillna(0, inplace=True)
                    for index , row in df.iterrows():
                        d = {'uid':row['uid'],'master_source':row['master_source'],'sub_source_name':row['sub_source_name'],
'source_contact_no':row['source_contact_no'],'political_category':row['political_category'],'name':row['name'],
'contact_number':row['contact_number'],'age':row['age'],'gender':row['gender'],'religion':row['religion'],
'category':row['category'],'caste':row['caste'],'district':row['district'],'assembly':row['assembly'],
'block_ulb':row['block_ulb'],'panchayat_ward':row['panchayat_ward'],'village_habitation':row['village_habitation'],
'occupation':row['occupation'],'profile':row['profile'],'whatsapp_user':['whatsapp_user'],
'whatsapp_number':row['whatsapp_number'],'rural_urban':row['rural_urban']}
                        data_list.append(Master(**d))
                    Master.objects.bulk_create(data_list)

                    result['status']="OK"
                    result['valid']=True
                    result['result']['message'] = "Data Uploaded successfully"
                    return Response(result, status=status.HTTP_200_OK)
                except UnicodeDecodeError as e:
                    # Handle the case when there's a UnicodeDecodeError.
                    result['status']="OK"
                    result['valid']=True
                    result['result']['message'] = "File In Special Character There, Please Remove and upload Again"
                    return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except:
                    result['status']="OK"
                    result['valid']=True
                    result['result']['message'] = "Duplicate Records There"
                    return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            result['status']="OK"
            result['valid']=True
            result['result']['message'] = "Please Use Correct Format And Try To Upload Again"
            return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class NewLeadsListing(APIView):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if request.user.is_authenticated:
            district_name = request.data['district_name']
            block_name = request.data['block_name']
            data_source_name = request.data['source_name']
            #page_size=request.data['page_size']
            download = request.data['download']
            #if page_size=='':
            #    page_size=10
            #PageNumberPagination.page_size=page_size
            #data = Master.objects.filter(new_record_status=0).values('id','uid','master_source','name','contact_number','district','block_ulb','age').order_by('id')
            data = Master.objects.filter(new_record_status=0).values().order_by('id')
            if district_name!='':
                data=data.filter(district=district_name)
                
            if block_name!='':
                data=data.filter(block_ulb=block_name)

            if data_source_name!='':
                data=data.filter(master_source=data_source_name)
            total_count = data.count()
            if download=="true":
                if total_count>0:    
                    result['status'] = "OK"
                    result['valid']  = True
                    result['result']['message']  = "Data fetched successfully"
                    result['result']['data'] = data 
                    return Response(result,status=status.HTTP_200_OK)
            #paginated_data = self.paginate_queryset(data , request, view=self)
            #paginated_data= self.get_paginated_response(paginated_data).data
            #result['status'] = "OK"
            #result['valid']  = True
            #result['total_count'] = total_count
            #result['result']['message']  = "Data fetched successfully"
            #result['result']['next']     = paginated_data['next']
            #result['result']['previous'] = paginated_data['previous']
            #result['result']['count']    = paginated_data['count']
            #result['result']['data']     = paginated_data['results']
            result['status'] = "OK"
            result['valid']  = True
            result['total_count'] = total_count
            result['result']['message']  = "Data fetched successfully"
            result['result']['data'] = data
            return Response(result, status=status.HTTP_200_OK)
                        
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)

class NewLeadDistributionBySuperAdmin(APIView, PageNumberPagination):
    def post(self, request):
        result={}
        result['status']="NOK"
        result['valid']=False
        result['result']={"message":"Unauthorized access","data":[]}

        if request.user.is_authenticated:
            if request.user.user_role_id == 1:
                lauAdminid = User.objects.filter(user_role_id = 2).values_list('id',flat=True)[0]
                district_name = request.data['district_name']
                block_name = request.data['block_name']
                data_source_name = request.data['source_name']
                download = request.data['download']
                leads_count = int(request.data['leads_count'])
                ids = request.data['ids']
                if ids != '':
                    ids =list(map(int,ids.split(',')))
                timenow = (datetime.today()).strftime('%Y-%m-%d %H:%M:%S')
                data_query = Master.objects.filter(new_record_status=0).values('id','uid','master_source','name','contact_number','district','block_ulb','age').order_by('id')
                data = data_query.values()
                if district_name!='':
                    data=data.filter(district=district_name)
                    
                if block_name!='':
                    data=data.filter(block_ulb=block_name)

                if data_source_name!='':
                    data=data.filter(master_source=data_source_name)
                data = data[:leads_count]
                ids_list = list(data.values_list('id',flat=True))
                final_list = []
                if download == "false":
                    for i in ids_list:
                        d = {
                        'lau_admin_id':lauAdminid,
                        'lau_created_date':timenow,
                        'master_id':i
                        }
                        final_list.append(Registration(**d))
                    
                    Registration.objects.bulk_create(final_list)
                    Master.objects.filter(id__in=ids_list).update(new_record_status=1)
                elif download=="true":
                    if len(ids)>0:
                        data = Registration.objects.filter(master__id__in=ids,lau_admin_id=lauAdminid).values('master__uid', 'master__master_source', 'master__sub_source_name', 'master__source_contact_no', 'master__political_category', 'master__name', 'master__contact_number', 'master__age', 'master__gender', 'master__religion', 'master__category', 'master__caste', 'master__district', 'master__assembly', 'master__rural_urban', 'master__block_ulb', 'master__panchayat_ward', 'master__village_habitation', 'master__occupation', 'master__profile', 'master__whatsapp_user', 'master__whatsapp_number','lau_created_date').order_by('id') 
                        result['status'] = "OK"
                        result['valid']  = True
                        result['result']['message']  = "Data fetched successfully"
                        result['result']['data'] = data
                        return Response(result,status=status.HTTP_200_OK)
                data1 = Master.objects.filter(id__in=ids_list,new_record_status=1).values()
                total_count = data1.count()
                paginated_data = self.paginate_queryset(data1 , request, view=self)
                paginated_data= self.get_paginated_response(paginated_data).data
                result['status'] = "OK"
                result['valid']  = True
                result['total_count'] = total_count
                result['result']['message']  = "Data fetched successfully"
                result['result']['next']     = paginated_data['next']
                result['result']['previous'] = paginated_data['previous']
                result['result']['count']    = paginated_data['count']
                result['result']['data']     = paginated_data['results']
                return Response(result, status=status.HTTP_200_OK)
        return Response(result,status=status.HTTP_401_UNAUTHORIZED)
        
#In lau agent screen shown all assignd leads
class AssignedLeadsForLauAgent(APIView, PageNumberPagination):
    def post(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": []}

        if request.user.is_authenticated:
            role_id = request.user.user_role_id
            if role_id in [1,2,3]:
                #agent_id = int(request.data['agent'])
                #agent_role = int(request.data['role_id'])
                calling_mode = request.data['calling_mode']
                inp_search = request.data['search_name_uid']
                inp_dist = request.data['district']
                inp_block = request.data['block']
                inp_call_status = request.data['call_status']
                inp_lead_status = request.data['lau_lead_status']
                # inp_date = request.data['date']
                page_size = request.data['page_size']
                if page_size == '':
                    page_size = 10
                if calling_mode == 'consent':
                    # leads_data = Registration.objects.filter(lau_consent_agent_id=agent_id).exclude(lau_lead_status__exact="All Criteria Fulfilled Consent").exclude(lau_lead_status__exact="All Criteria Fulfilled WA").values('id','master__uid','master__name','master__contact_number','master__district','master__block_ulb','lau_consent_call_status','lau_lead_status','lau_consent_call_status','lau_wa_assign_date','lau_followup_date_time')
                    leads_data = Registration.objects.filter(lau_consent_agent_id=request.user.id).exclude(Q(lau_consent_lead_status="All Criteria Fulfilled Consent") | Q(lau_consent_lead_status="All Criteria Fulfilled WA") | Q(lau_consent_lead_status="Not Interested")).values(
                                                                                    'id', 'master__uid', 'master__name',
                                                                                    'master__contact_number',
                                                                                    'master__district', 'master__block_ulb',
                                                                                    'lau_consent_lead_status',
                                                                                    'lau_consent_call_status',
                                                                                    'lau_wa_assign_date',
                                                                                    'lau_consent_followup_date_time','lau_consent_remarks','lau_consent_call_status_2','lau_consent_lead_status_2','lau_consent_followup_date_time_2','lau_consent_remarks_2','lau_consent_call_status_3','lau_consent_lead_status_3','lau_consent_followup_date_time_3','lau_consent_remarks_3','lau_consent_call_count').order_by('id')

                    for d in range(len(leads_data)):
                        date1 = leads_data[d]['lau_consent_followup_date_time']
                        date2 = leads_data[d]['lau_consent_followup_date_time_2']
                        date3 = leads_data[d]['lau_consent_followup_date_time_3']
                        if date1 is None:
                            date1 = datetime.strptime('2022-06-17', '%Y-%m-%d')
                        if date2 is None:
                            date2 = datetime.strptime('2022-06-17', '%Y-%m-%d')
                        if date3 is None:
                            date3 = datetime.strptime('2022-06-17', '%Y-%m-%d')
                        latest_date = max(date1,date2,date3)

                        if latest_date == date1:
                            del leads_data[d]['lau_consent_followup_date_time_2']
                            del leads_data[d]['lau_consent_followup_date_time_3']
                            del leads_data[d]['lau_consent_call_status_2']
                            del leads_data[d]['lau_consent_lead_status_2']
                            del leads_data[d]['lau_consent_call_status_3']
                            del leads_data[d]['lau_consent_lead_status_3']
                            del leads_data[d]['lau_consent_remarks_2']
                            del leads_data[d]['lau_consent_remarks_3']
                        elif latest_date == date2:
                            del leads_data[d]['lau_consent_followup_date_time']
                            del leads_data[d]['lau_consent_followup_date_time_3']
                            del leads_data[d]['lau_consent_call_status']
                            del leads_data[d]['lau_consent_lead_status']
                            del leads_data[d]['lau_consent_call_status_3']
                            del leads_data[d]['lau_consent_lead_status_3']
                            del leads_data[d]['lau_consent_remarks']
                            del leads_data[d]['lau_consent_remarks_3']
                        elif latest_date == date3:
                            del leads_data[d]['lau_consent_followup_date_time_2']
                            del leads_data[d]['lau_consent_followup_date_time']
                            del leads_data[d]['lau_consent_call_status_2']
                            del leads_data[d]['lau_consent_lead_status_2']
                            del leads_data[d]['lau_consent_call_status']
                            del leads_data[d]['lau_consent_lead_status']
                            del leads_data[d]['lau_consent_remarks_2']
                            del leads_data[d]['lau_consent_remarks']

                elif calling_mode == 'whatsapp':
                    # leads_data = Registration.objects.filter(lau_wa_agent_id=agent_id).exclude(lau_lead_status__exact="All Criteria Fulfilled WA").exclude(lau_lead_status__exact="All Criteria Fulfilled Consent").values('id','master__uid','master__name','master__contact_number','master__district','master__block_ulb','lau_call_status','lau_lead_status','lau_consent_call_status','lau_wa_assign_date','lau_followup_date_time')
                    leads_data = Registration.objects.filter(lau_wa_agent_id=request.user.id).exclude(Q(lau_lead_status="All Criteria Fulfilled WA") | Q(lau_lead_status="Not Interested")).values(
                                                                                        'id', 'master__uid', 'master__name',
                                                                                        'master__contact_number',
                                                                                        'master__district',
                                                                                        'master__block_ulb',
                                                                                        'lau_call_status',
                                                                                        'lau_lead_status',
                                                                                        #'lau_consent_call_status',
                                                                                        'lau_wa_assign_date',
                                                                                        'lau_followup_date_time','lau_remarks_1','lau_call_status_2','lau_lead_status_2','lau_followup_date_time_2','lau_remarks_2','lau_call_status_3','lau_lead_status_3','lau_followup_date_time_3','lau_remarks_3','lau_call_count').order_by('id')
                    for d in range(len(leads_data)):
                        date1 = leads_data[d]['lau_followup_date_time']
                        date2 = leads_data[d]['lau_followup_date_time_2']
                        date3 = leads_data[d]['lau_followup_date_time_3']
                        if date1 is None:
                            date1 = datetime.strptime('2022-06-17', '%Y-%m-%d')
                        if date2 is None:
                            date2 = datetime.strptime('2022-06-17', '%Y-%m-%d')
                        if date3 is None:
                            date3 = datetime.strptime('2022-06-17', '%Y-%m-%d')
                        latest_date = max(date1,date2,date3)

                        if latest_date == date1:
                            del leads_data[d]['lau_followup_date_time_2']
                            del leads_data[d]['lau_followup_date_time_3']
                            del leads_data[d]['lau_call_status_2']
                            del leads_data[d]['lau_lead_status_2']
                            del leads_data[d]['lau_call_status_3']
                            del leads_data[d]['lau_lead_status_3']
                            del leads_data[d]['lau_remarks_2']
                            del leads_data[d]['lau_remarks_3']
                        elif latest_date == date2:
                            del leads_data[d]['lau_followup_date_time']
                            del leads_data[d]['lau_followup_date_time_3']
                            del leads_data[d]['lau_call_status']
                            del leads_data[d]['lau_lead_status']
                            del leads_data[d]['lau_call_status_3']
                            del leads_data[d]['lau_lead_status_3']
                            del leads_data[d]['lau_remarks_1']
                            del leads_data[d]['lau_remarks_3']
                        elif latest_date == date3:
                            del leads_data[d]['lau_followup_date_time_2']
                            del leads_data[d]['lau_followup_date_time']
                            del leads_data[d]['lau_call_status_2']
                            del leads_data[d]['lau_lead_status_2']
                            del leads_data[d]['lau_call_status']
                            del leads_data[d]['lau_lead_status']
                            del leads_data[d]['lau_remarks_2']
                            del leads_data[d]['lau_remarks_3']
                if len(leads_data) == 0:
                    result['result']['message'] = 'No leads available for this agent'
                    return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                if inp_search != "":
                    master_data = leads_data.filter(
                        Q(master__name=inp_search) | Q(master__uid=inp_search)).values(
                        'id', 'master__uid', 'master__name', 'master__contact_number', 'master__district',
                        'master__block_ulb', 'lau_call_status', 'lau_lead_status','lau_consent_call_status','lau_consent_lead_status', 'lau_wa_assign_date',
                        'lau_followup_date_time')
                    if len(master_data) == 0:
                        result['result']['message'] = 'No leads available for this agent'
                        return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                    total_count = master_data.count()
                    PageNumberPagination.page_size = page_size
                    paginated_data = self.paginate_queryset(master_data, request, view=self)
                    paginated_data = self.get_paginated_response(paginated_data).data
                    result['status'] = "OK"
                    result['valid'] = True
                    result['total_count'] = total_count
                    result['result']['message'] = "Data fetched successfully"
                    result['result']['next'] = paginated_data['next']
                    result['result']['previous'] = paginated_data['previous']
                    result['result']['count'] = paginated_data['count']
                    result['result']['data'] = paginated_data['results']
                    return Response(result, status=status.HTTP_200_OK)
                if inp_dist != "" or inp_block != "" or inp_call_status != "" or inp_lead_status != "":
                    master_data = leads_data.filter(Q(master__district=inp_dist) | Q(master__block_ulb=inp_block) |
                                                           Q(lau_call_status=inp_call_status) | Q(lau_lead_status=inp_lead_status) | Q(lau_consent_call_status=inp_call_status) | Q(lau_consent_lead_status=inp_lead_status)).values('id', 'master__uid', 'master__name', 'master__contact_number', 'master__district','master__block_ulb', 'lau_call_status', 'lau_lead_status','lau_consent_call_status','lau_consent_lead_status', 'lau_wa_assign_date', 'lau_followup_date_time')
                    if len(master_data) == 0:
                        result['result']['message'] = 'No leads available for this agent'
                        return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                    total_count = master_data.count()
                    PageNumberPagination.page_size = page_size
                    paginated_data = self.paginate_queryset(master_data, request, view=self)
                    paginated_data = self.get_paginated_response(paginated_data).data
                    result['status'] = "OK"
                    result['valid'] = True
                    result['total_count'] = total_count
                    result['result']['message'] = "Data fetched successfully"
                    result['result']['next'] = paginated_data['next']
                    result['result']['previous'] = paginated_data['previous']
                    result['result']['count'] = paginated_data['count']
                    result['result']['data'] = paginated_data['results']
                    return Response(result, status=status.HTTP_200_OK)
                total_count = leads_data.count()
                PageNumberPagination.page_size = page_size
                paginated_data = self.paginate_queryset(leads_data, request, view=self)
                paginated_data = self.get_paginated_response(paginated_data).data
                result['status'] = "OK"
                result['valid'] = True
                result['total_count'] = total_count
                result['result']['message'] = "Data fetched successfully"
                result['result']['next'] = paginated_data['next']
                result['result']['previous'] = paginated_data['previous']
                result['result']['count'] = paginated_data['count']
                result['result']['data'] = paginated_data['results']
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)
# Action button in agent screen specific lead for show basic information
class ShowLeadBasicInfoToLauAgent(APIView):
    def post(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": []}

        if request.user.is_authenticated:
            lead_id = int(request.data['id'])
            calling_mode = request.data['calling_mode']
            if calling_mode == 'consent':
                leads_id = Registration.objects.filter(id=lead_id).values('id','master_id','interested_in_opening_youth_club','founding_25_members','whatsapp_group_of_100','physical_meeting_space','ready_to_create_club_fb_page','ready_to_pk_connect_app_download','whatsapp_group_created','wa_group_link','wa_group_name','wa_group_strength','central_number_added','pk_connect_app_download','app_download_verified','referral_name','referral_contact_no','lau_remarks',
                                                                      'lau_consent_call_status','lau_consent_lead_status','lau_consent_followup_date_time','lau_consent_remarks','lau_consent_call_status_2','lau_consent_lead_status_2','lau_consent_followup_date_time_2','lau_consent_remarks_2','lau_consent_call_status_3','lau_consent_lead_status_3','lau_consent_followup_date_time_3','lau_consent_remarks_3','lau_consent_call_count')
            elif calling_mode == 'whatsapp':
                leads_id = Registration.objects.filter(id=lead_id).values('id', 'master_id','interested_in_opening_youth_club','founding_25_members','whatsapp_group_of_100','physical_meeting_space','ready_to_create_club_fb_page','ready_to_pk_connect_app_download','whatsapp_group_created', 'wa_group_link','wa_group_name', 'wa_group_strength','central_number_added','pk_connect_app_download','app_download_verified', 'referral_name','referral_contact_no', 'lau_remarks',
                                                                          'lau_call_status','lau_lead_status','lau_followup_date_time','lau_remarks_1', 'lau_call_status_2','lau_lead_status_2','lau_followup_date_time_2','lau_remarks_2','lau_call_status_3', 'lau_lead_status_3','lau_followup_date_time_3','lau_remarks_3', 'lau_call_count')
            # basic_info = Registration.objects.filter(id=lead_id).values('id','master__uid', 'master__master_source', 'master__sub_source_name', 'master__source_contact_no', 'master__political_category', 'master__name', 'master__contact_number', 'master__age', 'master__gender', 'master__religion', 'master__category', 'master__caste', 'master__district', 'master__assembly', 'master__rural_urban', 'master__block_ulb', 'master__panchayat_ward', 'master__village_habitation', 'master__occupation', 'master__profile', 'master__whatsapp_user', 'master__whatsapp_number','interested_in_opening_youth_club','founding_25_members','whatsapp_group_of_100','physical_meeting_space','ready_to_create_club_fb_page','ready_to_pk_connect_app_download','whatsapp_group_created','wa_group_link','wa_group_name','wa_group_strength','central_number_added','pk_connect_app_download','app_download_verified','referral_name','referral_contact_no','lau_remarks')
            lead_id_master = leads_id[0]["master_id"]
            basic_info = Master.objects.filter(id=lead_id_master).values()
            basic_info = [(leads_id[0] | basic_info[0])]
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = basic_info
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

#save changes in agent screen
class SaveChangesBasicInfoByLauAgent(APIView):
    def post(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access"}

        if request.user.is_authenticated:
            inp_id = int(request.data['id'])
            inp_sub_source_name = request.data['sub_source_name']
            inp_source_contact_no = request.data['source_contact_no']
            inp_political_category = request.data['political_category']
            inp_name = request.data['name']
            inp_age = request.data['age']
            inp_gender = request.data['gender']
            inp_religion = request.data['religion']
            inp_category = request.data['category']
            inp_caste = request.data['caste']
            inp_district = request.data['district']
            inp_assembly = request.data['assembly']
            inp_rural_urban = request.data['rural_urban']
            inp_block_ulb = request.data['block_ulb']
            inp_panchayat_ward = request.data['panchayat_ward']
            inp_village_habitation = request.data['village_habitation']
            inp_occupation = request.data['occupation']
            inp_profile = request.data['profile']
            inp_whatsapp_user = request.data['whatsapp_user']
            inp_whatsapp_number = request.data['whatsapp_number']
            inp_other_caste = request.data['other_caste']

            if inp_age == "":
                inp_age = None
            reg_lead = Registration.objects.filter(id=inp_id).values('master_id')
            lead_master_id = reg_lead[0]["master_id"]
            Master.objects.filter(id=lead_master_id).update(sub_source_name=inp_sub_source_name, source_contact_no=inp_source_contact_no,
                                                    political_category=inp_political_category, name=inp_name,
                                                    age=inp_age, gender=inp_gender, religion=inp_religion, category=inp_category,
                                                    caste=inp_caste, district=inp_district, assembly=inp_assembly, rural_urban=inp_rural_urban,
                                                    block_ulb=inp_block_ulb, panchayat_ward=inp_panchayat_ward, village_habitation=inp_village_habitation,
                                                    occupation=inp_occupation, profile=inp_profile, whatsapp_user=inp_whatsapp_user, whatsapp_number=inp_whatsapp_number,other_caste=inp_other_caste)

            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data updated successfully"
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

#update wa info by agent in agent screen, id need in Registration
class UpdateWaInfoByLauAgent(APIView):
    def post(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access"}

        if request.user.is_authenticated:
            inp_id = request.data['id']
            inp_interested_in_opening_youth_club = request.data['interested_in_opening_youth_club']
            inp_founding_25_members = request.data['founding_25_members']
            inp_whatsapp_group_of_100 = request.data['whatsapp_group_of_100']
            inp_physical_meeting_space = request.data['physical_meeting_space']
            inp_ready_to_create_club_fb_page = request.data['ready_to_create_club_fb_page']
            inp_ready_pk_connect_app_download = request.data['ready_pk_connect_app_download']
            inp_whatsapp_group_created = request.data['whatsapp_group_created']
            inp_wa_group_link = request.data['wa_group_link']
            inp_wa_group_name = request.data['wa_group_name']
            inp_wa_group_strength = request.data['wa_group_strength']
            inp_central_number_added = request.data['central_number_added']
            inp_pk_connect_app_download = request.data['pk_connect_app_download']
            inp_app_download_verified = request.data['app_download_verified']
            inp_referral_name = request.data['referral_name']
            inp_referral_contact_no = request.data['referral_contact_no']
            inp_lau_remarks = request.data['lau_remarks']
            inp_call_status = request.data['call_status']
            inp_lead_statusrs = request.data['lead_status']
            inp_follow_date_time = request.data['follow_date_time']
            inp_remarks = request.data['remarks']
            calling_mode = request.data['calling_mode']
            if inp_follow_date_time == "":
                inp_follow_date_time = None
            if inp_wa_group_strength == "":
                inp_wa_group_strength = None
            if calling_mode == 'consent' :
                pre_call_count = Registration.objects.filter(id=inp_id).values('lau_consent_call_count')
                count = pre_call_count[0]['lau_consent_call_count']
                current_date = (datetime.today()).strftime('%Y-%m-%d %H:%M:%S')
                if count == None:
                    incr_count = 1
                    # update 1st status
                    Registration.objects.filter(id=inp_id).update(interested_in_opening_youth_club=inp_interested_in_opening_youth_club, founding_25_members=inp_founding_25_members, whatsapp_group_of_100=inp_whatsapp_group_of_100,
                        physical_meeting_space=inp_physical_meeting_space, ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page, ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                        wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength, central_number_added=inp_central_number_added, pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                        referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_consent_call_status=inp_call_status, lau_consent_lead_status=inp_lead_statusrs,lau_consent_followup_date_time=inp_follow_date_time, lau_consent_remarks=inp_remarks,lau_consent_call_count=incr_count,lau_last_updated_date_time=current_date)


                elif count == 1:
                    # update 2nd status
                    Registration.objects.filter(id=inp_id).update(
                        interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members, whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                        ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                        wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                        referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_consent_call_status_2=inp_call_status, lau_consent_lead_status_2=inp_lead_statusrs,lau_consent_followup_date_time_2=inp_follow_date_time, lau_consent_remarks_2=inp_remarks,lau_consent_call_count=count+1,lau_last_updated_date_time=current_date)
                elif count == 2:
                    # update 3rd status
                    Registration.objects.filter(id=inp_id).update(
                        interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members, whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                        ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                        wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                        referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_consent_call_status_3=inp_call_status, lau_consent_lead_status_3=inp_lead_statusrs,lau_consent_followup_date_time_3=inp_follow_date_time, lau_consent_remarks_3=inp_remarks,lau_consent_call_count=count+1,lau_last_updated_date_time=current_date)
                elif count == 3:
                    # update 1st status
                    Registration.objects.filter(id=inp_id).update(
                        interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members, whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                        ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                        wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                        referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_consent_call_status=inp_call_status, lau_consent_lead_status=inp_lead_statusrs,lau_consent_followup_date_time=inp_follow_date_time, lau_consent_remarks=inp_remarks,lau_consent_call_count=count+1,lau_last_updated_date_time=current_date)

                elif count > 3:
                    k,rem = divmod(count, 3)
                    if rem == 0:
                        # update 1st status
                        Registration.objects.filter(id=inp_id).update(
                            interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members,whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                            ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                            wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                            referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_consent_call_status=inp_call_status, lau_consent_lead_status=inp_lead_statusrs,lau_consent_followup_date_time=inp_follow_date_time, lau_consent_remarks=inp_remarks,lau_consent_call_count=count+1,lau_last_updated_date_time=current_date)

                    elif rem == 1:
                        # update 2nd status
                        Registration.objects.filter(id=inp_id).update(
                            interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members,whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                            ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                            wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                            referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_consent_call_status_2=inp_call_status, lau_consent_lead_status_2=inp_lead_statusrs,lau_consent_followup_date_time_2=inp_follow_date_time, lau_consent_remarks_2=inp_remarks,lau_consent_call_count=count+1,lau_last_updated_date_time=current_date)

                    elif rem == 2:
                        # update 3rd status
                        Registration.objects.filter(id=inp_id).update(
                            interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members,whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                            ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                            wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                            referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_consent_call_status_3=inp_call_status, lau_consent_lead_status_3=inp_lead_statusrs,lau_consent_followup_date_time_3=inp_follow_date_time, lau_consent_remarks_3=inp_remarks,lau_consent_call_count=count+1,lau_last_updated_date_time=current_date)

            elif calling_mode == 'whatsapp':
                pre_call_count = Registration.objects.filter(id=inp_id).values('lau_call_count')
                count = pre_call_count[0]['lau_call_count']
                current_date = (datetime.today()).strftime('%Y-%m-%d %H:%M:%S')
                if count == None:
                    # update 1st status
                    Registration.objects.filter(id=inp_id).update(
                        interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members,whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                        ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                        wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                        referral_contact_no=inp_referral_contact_no,lau_remarks=inp_lau_remarks, lau_call_status=inp_call_status, lau_lead_status=inp_lead_statusrs,lau_followup_date_time=inp_follow_date_time, lau_remarks_1=inp_remarks,lau_call_count=1,lau_last_updated_date_time=current_date)

                elif count == 1:
                    # update 2nd status
                    Registration.objects.filter(id=inp_id).update(
                        interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members, whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                        ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                        wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                        referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_call_status_2=inp_call_status, lau_lead_status_2=inp_lead_statusrs,lau_followup_date_time_2=inp_follow_date_time, lau_remarks_2=inp_remarks,lau_call_count=count+1,lau_last_updated_date_time=current_date)

                elif count == 2:
                    # update 3rd status
                    Registration.objects.filter(id=inp_id).update(
                        interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members, whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                        ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download, whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                        wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                        referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_call_status_3=inp_call_status, lau_lead_status_3=inp_lead_statusrs,lau_followup_date_time_3=inp_follow_date_time, lau_remarks_3=inp_remarks,lau_call_count=count+1,lau_last_updated_date_time=current_date)

                elif count == 3:
                    # update 1st status
                    Registration.objects.filter(id=inp_id).update(
                        interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members, whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                        ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                        wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                        referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_call_status=inp_call_status, lau_lead_status=inp_lead_statusrs,lau_followup_date_time=inp_follow_date_time, lau_remarks_1=inp_remarks,lau_call_count=count+1,lau_last_updated_date_time=current_date)

                elif count > 3:
                    k, rem = divmod(count, 3)
                    if rem == 0:
                        # update 1st status
                        Registration.objects.filter(id=inp_id).update(
                            interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members,whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                            ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                            wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                            referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_call_status=inp_call_status, lau_lead_status=inp_lead_statusrs,lau_followup_date_time=inp_follow_date_time, lau_remarks_1=inp_remarks,lau_call_count=count+1,lau_last_updated_date_time=current_date)

                    elif rem == 1:
                        # update 2nd status
                        Registration.objects.filter(id=inp_id).update(
                            interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members,whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                            ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                            wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                            referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks, lau_call_status_2=inp_call_status, lau_lead_status_2=inp_lead_statusrs,lau_followup_date_time_2=inp_follow_date_time, lau_remarks_2=inp_remarks,lau_call_count=count+1,lau_last_updated_date_time=current_date)

                    elif rem == 2:
                        # update 3rd status
                        Registration.objects.filter(id=inp_id).update(
                            interested_in_opening_youth_club=inp_interested_in_opening_youth_club,founding_25_members=inp_founding_25_members,whatsapp_group_of_100=inp_whatsapp_group_of_100,physical_meeting_space=inp_physical_meeting_space,
                            ready_to_create_club_fb_page=inp_ready_to_create_club_fb_page,ready_to_pk_connect_app_download=inp_ready_pk_connect_app_download,whatsapp_group_created=inp_whatsapp_group_created, wa_group_link=inp_wa_group_link,
                            wa_group_name=inp_wa_group_name, wa_group_strength=inp_wa_group_strength,central_number_added=inp_central_number_added,pk_connect_app_download=inp_pk_connect_app_download,app_download_verified=inp_app_download_verified, referral_name=inp_referral_name,
                            referral_contact_no=inp_referral_contact_no, lau_remarks=inp_lau_remarks,lau_call_status_3=inp_call_status, lau_lead_status_3=inp_lead_statusrs,lau_followup_date_time_3=inp_follow_date_time, lau_remarks_3=inp_remarks,lau_call_count=count+1,lau_last_updated_date_time=current_date)

            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data updated successfully"
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

#update CRM info by agent in agent screen, id need in Registration
# class UpdateCRMInfoByLauAgent(APIView):
#     def post(self, request):
#         result = {}
#         result['status'] = "NOK"
#         result['valid'] = False
#         result['result'] = {"message": "Unauthorized access"}
#
#         if request.user.is_authenticated:
#             inp_id = request.data['id']
#             inp_call_status = request.data['call_status']
#             inp_lead_statusrs = request.data['lead_status']
#             inp_follow_date_time = request.data['follow_date_time']
#             inp_remarks = request.data['remarks']
#             if inp_follow_date_time == "":
#                 inp_follow_date_time = None
#             Registration.objects.filter(id=inp_id).update(lau_call_status=inp_call_status, lau_lead_status=inp_lead_statusrs, lau_followup_date_time=inp_follow_date_time, lau_crm_remarks=inp_remarks)
#             result['status'] = "OK"
#             result['valid'] = True
#             result['result']['message'] = "Data updated successfully"
#             return Response(result, status=status.HTTP_200_OK)
#         return Response(result, status=status.HTTP_401_UNAUTHORIZED)

# Lau call status details
class LauCallStatus(APIView):
    def get(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": []}

        if request.user.is_authenticated:
            call_status = ["Connected", "Call Back Later", "Busy", "Call Not answered", "Switched off",
                           "Number not reachable", "Wrong Number"]
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data updated successfully"
            result['result']['data'] = call_status
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)



# Lau lead status details
class LauLeadStatus(APIView):
    def get(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": []}

        if request.user.is_authenticated:
            call_status = ["All Criteria Fulfilled Consent", "All Criteria Fulfilled WA", "Not Interested",
                           "Followup"]
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data updated successfully"
            result['result']['data'] = call_status
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

# LauAdmin Dist wise info table for all data
class LauDistrictWiseTableInfo(APIView):
    def post(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access"}

        if request.user.is_authenticated:
            inp_admin_id = request.data['admin_id']
            dist_data = DistrictMapping.objects.all().values('district_name').distinct().order_by('district_name')
            dist_names = [n["district_name"] for n in dist_data]

            data = []
            for d in dist_names:
                master_dist_ids = list(Master.objects.filter(district=d).values_list('id', flat=True))
                reg_data = Registration.objects.filter(master_id__in=master_dist_ids).values('id', 'master__district','lau_admin_id','lau_lead_status','wa_group_strength')
                touch_based = reg_data.filter(lau_admin_id=inp_admin_id).values().count()
                converted = reg_data.filter(lau_lead_status="All Criteria Fulfilled WA").values().count()
                consented = reg_data.filter(lau_lead_status="All Criteria Fulfilled Consent").values().count()
                wa_group_strength = reduce(lambda x, y: x + y['wa_group_strength'], reg_data, 0)

                data.append({
                    "District": d,
                    "Total Leads": reg_data.count(),
                    "Touch Based": touch_based,
                    "Converted": converted,
                    "Consented": consented,
                    "WA-Strength": wa_group_strength
                })
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = data
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

# LauAdmin source wise graph
class LauAdminSourceWiseGraph(APIView):
    def post(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access"}

        if request.user.is_authenticated:
            inp_admin_id = request.data['admin_id']
            inp_source = request.data['source']
            reg_data = Registration.objects.filter(master__master_source=inp_source).values('id', 'master__district', 'master__master_source','lau_admin_id','lau_lead_status','wa_group_strength')
            converted = reg_data.filter(lau_lead_status="All Criteria Fulfilled WA").values().count()
            touch_based = reg_data.filter(lau_admin_id=inp_admin_id).values().count()
            graph_data = [{
                "Touch Based":touch_based,
                "Converted":converted,
            }]
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = graph_data
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

# LauAdmin district wise consent graph
class LauAdminDistrictWiseConsentGraph(APIView):
    def post(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access"}

        if request.user.is_authenticated:
            inp_admin_id = request.data['admin_id']
            inp_district = request.data['district']
            all_data = Registration.objects.filter(master__district=inp_district).values('id', 'master__district', 'master__master_source','lau_admin_id','lau_lead_status','wa_group_strength')
            converted = all_data.filter(lau_lead_status="All Criteria Fulfilled Consent").values().count()
            touch_based = all_data.filter(lau_admin_id=inp_admin_id).values().count()
            graph_data = [{
                "Total Leads":all_data.count(),
                "Touch Based":touch_based,
                "Converted":converted,
            }]
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = graph_data
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

# LauAdmin district wise WA graph
class LauAdminDistrictWiseWAGraph(APIView):
    def post(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access"}

        if request.user.is_authenticated:
            inp_admin_id = request.data['admin_id']
            inp_district = request.data['district']
            all_data = Registration.objects.filter(master__district=inp_district).values('id', 'master__district', 'master__master_source','lau_admin_id','lau_lead_status','wa_group_strength')
            wa_converted = all_data.filter(lau_lead_status="All Criteria Fulfilled WA").values().count()
            touch_based = all_data.filter(lau_admin_id=inp_admin_id).values().count()
            graph_data = [{
                "Total Leads":all_data.count(),
                "Touch Based":touch_based,
                "WA Converted":wa_converted,
            }]
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = graph_data
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

# lauadmin screen bucket tils data
class LauAdminTilsWiseData(APIView):
    def post(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": []}

        if request.user.is_authenticated:
            inp_admin_id = request.data['admin_id']
            inp_district = request.data['district']
            inp_block = request.data['block']
            inp_source = request.data['source']
            inp_gender = request.data['gender']
            inp_age = request.data['age']
            inp_religion = request.data['religion']
            inp_category = request.data['category']
            inp_caste = request.data['caste']

            if inp_district != "":
                master_data = Registration.objects.filter(master__district=inp_district).values('id', 'master__district','master__block_ulb', 'master__master_source','lau_admin_id','lau_call_status','lau_lead_status','wa_group_strength','master__age')
            if inp_block != "":
                master_data = Registration.objects.filter(master__block_ulb=inp_block).values('id','master__district','master__block_ulb','master__master_source','lau_admin_id','lau_lead_status','wa_group_strength','master__age')
            if inp_source != "":
                master_data = Registration.objects.filter(master__master_source=inp_source).values('id','master__district','master__block_ulb','master__master_source','lau_admin_id','lau_call_status','lau_lead_status','wa_group_strength','master__age')
            if inp_gender != "":
                master_data = Registration.objects.filter(master__gender=inp_gender).values('id','master__district','master__block_ulb','master__master_source','lau_admin_id','lau_lead_status','wa_group_strength','master__age')
            if inp_age != "":
                master_data = Registration.objects.filter(master__age=inp_age).values('id','master__district','master__block_ulb','master__master_source','lau_admin_id','lau_lead_status','wa_group_strength','master__age')
            if inp_religion != "":
                master_data = Registration.objects.filter(master__religion=inp_religion).values('id','master__district','master__block_ulb','master__master_source','lau_admin_id','lau_lead_status','wa_group_strength','master__age')
            if inp_category != "":
                master_data = Registration.objects.filter(master__category=inp_religion).values('id','master__district','master__block_ulb','master__master_source','lau_admin_id','lau_lead_status','wa_group_strength','master__age')
            if inp_caste != "":
                master_data = Registration.objects.filter(master__caste=inp_religion).values('id','master__district','master__block_ulb','master__master_source','lau_admin_id','lau_lead_status','wa_group_strength','master__age')
            if inp_caste != "":
                master_data = Registration.objects.filter(master__caste=inp_religion).values('id','master__district','master__block_ulb','master__master_source','lau_admin_id','lau_lead_status','wa_group_strength','master__age')

            touch_based = master_data.filter(lau_admin_id=inp_admin_id).values().count()
            not_connected = master_data.filter(lau_call_status='Number not reachable').values().count()
            droup_out = master_data.filter(lau_lead_status='Not Interested').values().count()
            connected = master_data.filter(lau_call_status='Connected').values().count()
            wa_strength = reduce(lambda x, y: x + y['wa_group_strength'], master_data, 0)
            # in_hand =
            consented = master_data.filter(lau_lead_status="All Criteria Fulfilled Consent").values().count()

            tils_data = [
                {"count": master_data.count(),'name':"Total Leads"},
                {"count": not_connected,'name':"Not Connected"},
                {"count": droup_out,'name':"Total Dropout"},
                {"count": touch_based,'name':"Touch Based"},
                {"count": connected,'name':"Connected"},
                {"count":wa_strength,'name':"WA-Strength"},
                {"count": consented,'name':"Consent"},
            ]

            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = tils_data
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

# complete leads data for download
class CallingMasterSheetDownload(APIView):
    def post(self, request):
        result = {}
        result['status'] = "NOK"
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": []}

        if request.user.is_authenticated:
            inp_district = request.data['district']
            inp_block = request.data['block']
            inp_source = request.data['source']
            start_date = request.data['start_date']
            end_date = request.data['end_date']

            if start_date == "" and end_date == "":
                start_date = "2022-06-17"
                end_date = (datetime.today()).strftime('%Y-%m-%d')

            elif (start_date == "" and end_date != "") or (start_date != "" and end_date == ""):
                if start_date == "":
                    result['valid'] = True
                    result['result']['message'] = "start date cannot be empty"
                else:
                    result['valid'] = True
                    result['result']['message'] = "end date cannot be empty"
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not validatedate(start_date):
                result['valid'] = True
                result['result']['message'] = "Invalid start date format, valid format yyyy-mm-dd"
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not validatedate(end_date):
                result['valid'] = True
                result['result']['message'] = "Invalid end date format, valid format yyyy-mm-dd"
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if (end_date < start_date):
                result['valid'] = True
                result['result']['message'] = "end date should not be less than start date"
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            else:
                end_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

            all_data = Registration.objects.filter(lau_last_updated_date_time__range=(start_date, end_date)).values()
            all_data = all_data.filter(Q(Q(lau_lead_status="All Criteria Fulfilled Consent") | Q(
                lau_lead_status="All Criteria Fulfilled WA") | Q(lau_lead_status="Not Interested") | Q(
                lau_lead_status="Followup")) | Q(Q(lau_consent_lead_status="All Criteria Fulfilled Consent") | Q(
                lau_consent_lead_status="All Criteria Fulfilled WA") | Q(lau_consent_lead_status="Not Interested") | Q(
                lau_consent_lead_status="Followup"))).values(
                'id', 'master__uid', 'master__master_source', 'master__sub_source_name','master__source_contact_no', 'master__political_category','master__name',
                'master__contact_number', 'master__age', 'master__gender', 'master__religion', 'master__category', 'master__caste','master__other_caste','master__district', 'master__assembly',
                'master__block_ulb', 'master__panchayat_ward', 'master__village_habitation', 'master__occupation','master__profile', 'master__whatsapp_user','master__whatsapp_number',
                'master__rural_urban', 'master__new_record_status',
                'interested_in_opening_youth_club', 'founding_25_members',
                'whatsapp_group_of_100', 'physical_meeting_space', 'ready_to_create_club_fb_page','ready_to_pk_connect_app_download','whatsapp_group_created',
                'wa_group_link','wa_group_name','wa_group_strength', 'central_number_added','pk_connect_app_download','app_download_verified','referral_name','referral_contact_no','lau_remarks',
                'lau_consent_call_status','lau_consent_lead_status','lau_consent_followup_date_time','lau_consent_remarks',
                'lau_consent_call_status_2','lau_consent_lead_status_2','lau_consent_followup_date_time_2','lau_consent_remarks_2',
                'lau_consent_call_status_3','lau_consent_lead_status_3','lau_consent_followup_date_time_3','lau_consent_remarks_3','lau_consent_call_count',
                'lau_call_status','lau_lead_status','lau_followup_date_time','lau_remarks_1','lau_call_status_2','lau_lead_status_2','lau_followup_date_time_2','lau_remarks_2',
                'lau_call_status_3','lau_lead_status_3','lau_followup_date_time_3','lau_remarks_3','lau_call_count',
                'lau_admin_id', 'lau_wa_agent_id', 'lau_wa_assign_date', 'lau_admin_assign_sa_date')

            if inp_district != "":
                all_data = all_data.filter(master__district=inp_district)
            if inp_block != "":
                all_data = all_data.filter(master__block_ulb=inp_block)
            if inp_source != "":
                all_data = all_data.filter(master__master_source=inp_source)

            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Data fetched successfully"
            result['result']['data'] = all_data
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)
