from django.urls import path 
from .views import DistrictLisitng, LAU_Agents, TotalLeadsUnassignedbyLAUAdmin, TaskDistributionAPIView, BlockListing, TotalLeadAssignd, TotalLeadUnassigned, DataSourceListing, UploadingNewLeads, LauAssiginLeadsToAgents, AssignedLeadsforLAUAgents, ShowBasicInfotoLAUAgent, SaveChangesBasicInfo

urlpatterns = [
    path('get_district/', DistrictLisitng.as_view(), name = 'District'),
    path('get_block/', BlockListing.as_view(), name = 'Block'),
    path('get_datasource/', DataSourceListing.as_view(), name = 'Data Source'),
    path('uploadnewleads/', UploadingNewLeads.as_view(), name = 'Upload New Leads'),
    path('get_totalleads/', TotalLeadUnassigned.as_view(), name = 'Total Lead Unassigned'),
    path('get_totalleadassignd/',TotalLeadAssignd.as_view(), name='Total Lead Assignd'),
    path('get_lauagents/', LAU_Agents.as_view(), name = 'LAU Agents'),
    path('get_TotalLeadsUnassignedbyLAUAdmin/', TotalLeadsUnassignedbyLAUAdmin.as_view(), name = 'Total Leads Unassigned by LAU Admin'),
    path('get_lauAssiginLeadsToConsent/', LauAssiginLeadsToAgents.as_view(), name = 'Lau Assigin Leads To Consent'),
    path('get_TaskDistributionAPIView/', TaskDistributionAPIView.as_view(), name = 'Task Distribution API'),
    path('get_AssignedLeadsforLAUAgents/', AssignedLeadsforLAUAgents.as_view(), name = 'Assigned Leads for LAU Agents'),
    path('get_ShowBasicInfotoLAUAgent/', ShowBasicInfotoLAUAgent.as_view(), name = 'Show Basic Info Lead to LAU Agent'),
    path('get_SaveChangesBasicInfo/', SaveChangesBasicInfo.as_view(), name = 'Save Changes Basic Info'),
]