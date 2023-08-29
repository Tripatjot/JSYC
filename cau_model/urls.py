from django.urls import path 
from cau_model.views import (ShowBasicInfo_AssignWALeadtoCAUAgent,CAUAgentsListing,AssignWALeadtoCAUAgent,
                             ShowBasicInfo_CAUAgent,UpdateCAUfieldsbyCAUAgent,PreviousStatusonCAUAgentLeadform,
                             ShowBasicInfo_RTOLeadtoSuperAdmin,AssignRTOLeadstoSuperAdmin,CAUCallStatusListing,
                             CAULeadStatusListing)
urlpatterns = [
    path('get_ShowBasicInfo_AssignWALeadtoCAUAgent/', ShowBasicInfo_AssignWALeadtoCAUAgent.as_view(), name = 'Show Basic Info Assign WA Lead to CAU Agent'),
    path('get_CAUAgentsListing/', CAUAgentsListing.as_view(), name = 'CAU Agents Listing'),
    path('get_AssignWALeadtoCAUAgent/', AssignWALeadtoCAUAgent.as_view(), name = 'Assign WA Lead to CAU Agent'),
    path('get_ShowBasicInfo_CAUAgent/', ShowBasicInfo_CAUAgent.as_view(), name = 'Show Basic Info CAU Agent'),
    path('get_CAUCallStatusListing/', CAUCallStatusListing.as_view(), name = 'CAU Call Status Listing'),
    path('get_CAULeadStatusListing/', CAULeadStatusListing.as_view(), name = 'CAU Lead Status Listing'),
    path('get_UpdateCAUfieldsbyCAUAgent/', UpdateCAUfieldsbyCAUAgent.as_view(), name = 'Update CAU fields by CAU Agent'),
    path('get_PreviousStatusonCAUAgentLeadform/', PreviousStatusonCAUAgentLeadform.as_view(), name = 'Previous Status on CAU Agent Lead form'),
    path('get_ShowBasicInfo_RTOLeadtoSuperAdmin/', ShowBasicInfo_RTOLeadtoSuperAdmin.as_view(), name = 'Show Basic Info RTO Lead to SuperAdmin'),
    path('get_AssignRTOLeadstoSuperAdmin/', AssignRTOLeadstoSuperAdmin.as_view(), name = 'Assign RTO Leads to SuperAdmin'),
]