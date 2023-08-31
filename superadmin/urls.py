from django.urls import path 
from .views import (DistrictLisitng, LAU_Agents, TotalLeadsUnassignedbyLAUAdmin, 
                    BlockListing, TotalLeadAssignd, 
                    TotalLeadUnassigned, DataSourceListing, UploadingNewLeads, 
                    LauAssiginLeadsToAgents, AssignedLeadsforLAUAgents, ShowBasicInfotoLAUAgent, 
                    SaveChangesBasicInfo, updateWAinfoByLAUAgent_1, updateWAinfoByLAUAgent_2,
                    LauCallStatusListing, LauLeadStatusListing, LAUAdminConsenttoWA,
                    ShowBasicInfo_AssignWALeadtoCAUAdmin, AssignWALeadtoCAUAdmin,AssignLeadsConsenttoWA,
                    AssignWAtoSuperAdmin,Showbasicinfo_LAUAdminWAtoSuperAdmin, ShowBasicInfo_AssignRTOLeadstoCOU,
                    AssignRTOLeadstoCOU)

urlpatterns = [
    # SuperAdmin- New Leads
    path('get_district/', DistrictLisitng.as_view(), name = 'District'),
    path('get_block/', BlockListing.as_view(), name = 'Block'),
    path('get_datasource/', DataSourceListing.as_view(), name = 'Data Source'),
    path('uploadnewleads/', UploadingNewLeads.as_view(), name = 'Upload New Leads'),
    path('get_totalleads/', TotalLeadUnassigned.as_view(), name = 'Total Lead Unassigned'),
    path('get_totalleadassignd/',TotalLeadAssignd.as_view(), name='Total Lead Assignd'),
    
    # LAU Admin - Assign new Leads 
    path('get_lauagents/', LAU_Agents.as_view(), name = 'LAU Agents'),
    path('get_TotalLeadsUnassignedbyLAUAdmin/', TotalLeadsUnassignedbyLAUAdmin.as_view(), name = 'Total Leads Unassigned by LAU Admin'),
    path('get_lauAssiginLeadsToConsent/', LauAssiginLeadsToAgents.as_view(), name = 'Lau Assigin Leads To Consent'),
    
    # LAU Agents - Dashboard
    path('get_AssignedLeadsforLAUAgents/', AssignedLeadsforLAUAgents.as_view(), name = 'Assigned Leads for LAU Agents'),
    path('get_ShowBasicInfotoLAUAgent/', ShowBasicInfotoLAUAgent.as_view(), name = 'Show Basic Info Lead to LAU Agent'),
    path('get_SaveChangesBasicInfo/', SaveChangesBasicInfo.as_view(), name = 'Save Changes Basic Info'),
    path('get_updateWAinfoByLAUAgent_1/', updateWAinfoByLAUAgent_1.as_view(), name = 'update WA info By LAU Agent 1'),
    path('get_updateWAinfoByLAUAgent_2/', updateWAinfoByLAUAgent_2.as_view(), name = 'Update WA info By LAU Agent_2'),
    path('get_LauCallStatusListing/', LauCallStatusListing.as_view(), name = 'Lau Call Status Listing'),
    path('get_LauLeadStatusListing/', LauLeadStatusListing.as_view(), name = 'Lau Lead Status Listing'),
    
    # LAU Admin - WhatsApp Leads
    path('get_LAUAdminConsenttoWA/', LAUAdminConsenttoWA.as_view(), name = 'LAU Admin Consent to WA'),
    path('get_AssignLeadsConsenttoWA/', AssignLeadsConsenttoWA.as_view(), name = 'Assign Leads Consent to WA'),
    path('Showbasicinfo_LAUAdminWAtoSuperAdmin/', Showbasicinfo_LAUAdminWAtoSuperAdmin.as_view(), name = 'Show basic info LAU Admin WA to SuperAdmin'),
    path('get_AssignWAtoSuperAdmin/', AssignWAtoSuperAdmin.as_view(), name = 'Assign WA to SuperAdmin'),
     
    # SuperAdmin-CAU Assign
    path('get_ShowBasicInfo_AssignWALeadtoCAUAdmin/', ShowBasicInfo_AssignWALeadtoCAUAdmin.as_view(), name = 'Show Basic Info_Assign WA Lead to CAU'),
    path('get_AssignWALeadtoCAUAdmin/', AssignWALeadtoCAUAdmin.as_view(), name = 'Assign WA Lead to CAU'),
    
    path('get_ShowBasicInfo_AssignRTOLeadstoCOU/', ShowBasicInfo_AssignRTOLeadstoCOU.as_view(), name = 'Show Basic Info Assign RTO Leads to COU'),
    path('get_AssignRTOLeadstoCOU/', AssignRTOLeadstoCOU.as_view(), name = 'Assign RTO Leads to COU'),
    
]    