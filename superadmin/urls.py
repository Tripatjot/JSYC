from django.urls import path 
from .views import (DistrictLisitng, LAU_Agents, TotalLeadsUnassignedbyLAUAdmin, 
                    TaskDistributionAPIView, BlockListing, TotalLeadAssignd, 
                    TotalLeadUnassigned, DataSourceListing, UploadingNewLeads, 
                    LauAssiginLeadsToAgents, AssignedLeadsforLAUAgents, ShowBasicInfotoLAUAgent, 
                    SaveChangesBasicInfo, updateWAinfoByLAUAgent_1, updateWAinfoByLAUAgent_2,
                    LauCallStatusListing, LauLeadStatusListing, LAUAdminConsenttoWA,
                    LAUAdminWAtoSuperAdmin, ShowBasicInfo_AssignWALeadtoCAUAdmin, AssignWALeadtoCAUAdmin,
                    ShowBasicInfo_AssignWALeadtoCAUAdmin, AssignWALeadtoCAUAgent, CAUAgentsListing,
                    ShowBasicInfo_CAUAgent,PreviousStatusonCAUAgentLeadform)

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
    path('get_TaskDistributionAPIView/', TaskDistributionAPIView.as_view(), name = 'Task Distribution API'),
    
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
    path('get_LAUAdminWAtoSuperAdmin/', LAUAdminWAtoSuperAdmin.as_view(), name = 'LAU Admin WA to Super Admin'),
    
    # SuperAdmin-CAU Assign
    path('get_ShowBasicInfo_AssignWALeadtoCAUAdmin/', ShowBasicInfo_AssignWALeadtoCAUAdmin.as_view(), name = 'Show Basic Info_Assign WA Lead to CAU'),
    path('get_AssignWALeadtoCAUAdmin/', AssignWALeadtoCAUAdmin.as_view(), name = 'Assign WA Lead to CAU'),
]    