from django.urls import path 
from cou_model.views import (ShowBasicInfo_AssignRTOLeadstoCOUAgent,COUAgentListing,AssignRTOLeadstoCOUAgent,
                             ShowBasicInfo_COUAgent)

urlpatterns = [
    path('get_ShowBasicInfo_AssignRTOLeadstoCOUAgent/', ShowBasicInfo_AssignRTOLeadstoCOUAgent.as_view(), name = 'Show Basic Info Assign RTO Leads to COU Agent'),
    path('get_COUAgentListing/', COUAgentListing.as_view(), name = 'COU Agent Listing'),
    path('get_AssignRTOLeadstoCOUAgent/', AssignRTOLeadstoCOUAgent.as_view(), name = 'Assign RTO Leads to COU Agent'),
    path('get_ShowBasicInfo_COUAgent/', ShowBasicInfo_COUAgent.as_view(), name = 'Show Basic Info COU Agent'),
]