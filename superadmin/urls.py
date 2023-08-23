from django.urls import path 
from .views import GetDistrict, GetBlock, GetDataSource, UploadNewLeads, TotalLeadUnassigned, TotalLeadAssignd, LAU_Agents, TaskDistributionAPIView

urlpatterns = [
    path('get_district/', GetDistrict.as_view(), name = 'District'),
    path('get_block/', GetBlock.as_view(), name = 'Block'),
    path('get_datasource/', GetDataSource.as_view(), name = 'Data Source'),
    path('uploadnewleads/', UploadNewLeads.as_view(), name = 'Upload New Leads'),
    path('get_totalleads/', TotalLeadUnassigned.as_view(), name = 'Total Lead Unassigned'),
    path('get_totalleadassignd/',TotalLeadAssignd.as_view(), name='Total Lead Assignd'),
    # path('get_assignnewleads/', AssignNewLeads.as_view(), name = 'Assign New Leads'),
    path('get_lauagents/', LAU_Agents.as_view(), name = 'LAU Agents'),
    path('get_TaskDistributionAPIView/', TaskDistributionAPIView.as_view(), name = 'Task Distribution API'),
]