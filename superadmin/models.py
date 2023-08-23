
# from django.db import models

# # Create your models here.
# class Master(models.Model):
#     #id = models.BigAutoField(primary_key=True)
#     uid = models.CharField(max_length=100, blank=True, null=True)
#     master_source = models.CharField(max_length=50, blank=True, null=True)
#     sub_source_name = models.CharField(max_length=50, blank=True, null=True)
#     source_contact_no = models.CharField(max_length=15, blank=True, null=True)
#     political_category = models.CharField(max_length=50, blank=True, null=True)
#     name = models.CharField(max_length=50, blank=True, null=True)
#     contact_number = models.CharField(max_length=15, unique=True,default=0)
#     age = models.IntegerField(blank=True, null=True)
#     gender = models.CharField(max_length=15, blank=True, null=True)
#     religion = models.CharField(max_length=50, blank=True, null=True)
#     category = models.CharField(max_length=50, blank=True, null=True)
#     caste = models.CharField(max_length=50, blank=True, null=True)
#     district = models.CharField(max_length=50, blank=True, null=True)
#     assembly = models.CharField(max_length=50, blank=True, null=True)
#     block_ulb = models.CharField(max_length=50, blank=True, null=True)
#     panchayat_ward = models.CharField(max_length=50, blank=True, null=True)
#     village_habitation = models.CharField(max_length=100, blank=True, null=True)
#     occupation = models.CharField(max_length=50, blank=True, null=True)
#     profile = models.TextField(blank=True, null=True)
#     whatsapp_user = models.CharField(max_length=10, blank=True, null=True)
#     whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
#     rural_urban = models.CharField(max_length=50, blank=True, null=True)
#     other_caste = models.CharField(max_length=50, blank=True, null=True)

#     new_record_status = models.IntegerField(blank=True, null=True,default=0)


#     class Meta:
#         managed = True
#         db_table = 'summary_master'
        

# class Registration(models.Model):
#     master = models.ForeignKey(Master,on_delete=models.CASCADE)
#     # LAU Consent fields
#     lau_created_date = models.DateTimeField(blank=True, null=True)
#     interested_in_opening_youth_club = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     founding_25_members = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     whatsapp_group_of_100 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     physical_meeting_space = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     pk_connect_app_download = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     ready_to_create_club_fb_page = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     wa_group_name = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_consent_agent_id = models.IntegerField(blank=True, null=True)
#     lau_consent_call_status = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_consent_lead_status = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     # previous status
#     lau_consent_followup_date_time = models.DateTimeField(blank=True, null=True)
#     lau_consent_remarks = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_consent_call_status_2 = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_consent_lead_status_2 = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_consent_followup_date_time_2 = models.DateTimeField(blank=True, null=True)
#     lau_consent_remarks_2 = models.TextField(db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_consent_call_status_3 = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_consent_lead_status_3 = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_consent_followup_date_time_3 = models.DateTimeField(blank=True, null=True)
#     lau_consent_remarks_3 = models.TextField(db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_consent_call_count = models.IntegerField(blank=True, null=True)

#     #LAU whatsapp fields
#     wa_group_link = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     wa_group_strength = models.IntegerField(blank=True, null=True)
#     central_number_added = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     referral_contact_no = models.CharField(max_length=20, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     referral_name = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_remarks = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_followup_date_time = models.DateTimeField(blank=True, null=True)
#     lau_call_status = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_lead_status = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_admin_id = models.IntegerField(blank=True, null=True)
#     lau_wa_agent_id = models.IntegerField(blank=True, null=True)
#     lau_wa_assign_date = models.DateTimeField(blank=True, null=True)
#     lau_admin_assign_sa_date = models.DateTimeField(blank=True, null=True)
#     lau_sa_status = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_crm_remarks = models.TextField(db_collation='utf8mb4_general_ci', blank=True, null=True)
#     whatsapp_group_created =models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     ready_to_pk_connect_app_download = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     app_download_verified = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     # previous status
#     lau_remarks_1 = models.TextField(db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_call_status_2 = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_lead_status_2 = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_followup_date_time_2 = models.DateTimeField(blank=True, null=True)
#     lau_remarks_2 = models.TextField(db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_call_status_3 = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_lead_status_3 = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_followup_date_time_3 = models.DateTimeField(blank=True, null=True)
#     lau_remarks_3 = models.TextField(db_collation='utf8mb4_general_ci', blank=True, null=True)
#     lau_call_count = models.IntegerField(blank=True, null=True)
#     lau_last_updated_date_time = models.DateTimeField(blank=True, null=True)
#     # CAU fields
#     cau_created_date = models.DateTimeField(blank=True, null=True)
#     club_type = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     total_no_of_members_on_WA = models.IntegerField(blank=True, null=True)
#     members_100_added_on_WA = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     president_name = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     president_contact_no = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     smpoc_name = models.CharField(max_length= 50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     smpoc_contact_no = models.CharField(max_length= 15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     vice_president_name = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     vice_president_contact_no = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     secretary_name = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     secretary_contact_no = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     treasurer_name = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     treasurer_contact_no = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     office_bearers_5_provided = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     space_address = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     space_pic_or_video_provided = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     upload_space_pic_or_video = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fb_page_name = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fb_page_link = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fb_page_id = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fb_page_password = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     admin_right_shared_with_master_id = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     admin_right_received_by_master_id = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fb_page_created = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     confirmation_status_clubs_rto = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     want_to_contest_election = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     electoral_preference = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     cau_remarks = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     cau_followup_date_time = models.DateTimeField(blank=True, null=True)
#     cau_call_status = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     cau_lead_status = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     cau_admin_id = models.IntegerField(blank=True, null=True)
#     cau_agent_id = models.IntegerField(blank=True, null=True)
#     cau_admin_assign_sa_date = models.DateTimeField(blank=True, null=True)
#     cau_sa_status = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)

#     #COU fields
#     cou_created_date = models.DateTimeField(blank=True, null=True)
#     designation_1 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     bank_account_number_1 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     ifsc_code_1 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     designation_2 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     bank_account_number_2 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     ifsc_code_2 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     designation_3 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     bank_account_number_3 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     ifsc_code_3 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     founding_20_member_list_upload = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_1 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_1 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_2 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_2 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_3 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_3 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_4 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_4 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_5 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_5 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_6 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_6 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_7 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_7 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_8 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_8 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_9 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_9 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_10 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_10 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_11 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_11 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_12 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_12 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_13 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_13 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_14 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_14 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_15 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_15 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_16 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_16 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_17 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_17 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_18 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_18 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_19 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_19 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_contact_no_20 = models.CharField(max_length=15, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     fm_name_20 = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     upload_pledge_video = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     upload_testimonial_video = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     upload_group_picture_with_flex = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     club_location_google_link = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     number_of_attendees_for_the_inauguration = models.IntegerField(blank=True, null=True)
#     number_of_PK_connect_downloads = models.IntegerField(blank=True, null=True)
#     carrom_board_provided = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     photo_frame_provided = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     ob_5_id_card_provided = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     opening_kit_provided = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     club_inauguration_verified = models.TextField(db_collation='utf8mb4_general_ci', blank=True, null=True)
#     cou_remarks = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     cou_followup_date_time = models.DateTimeField(blank=True, null=True)
#     cou_call_status = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     cou_lead_status = models.TextField( db_collation='utf8mb4_general_ci', blank=True, null=True)
#     cou_admin_id = models.IntegerField(blank=True, null=True)
#     cou_agent_id = models.IntegerField(blank=True, null=True)
#     cou_admin_assign_sa_date = models.DateTimeField(blank=True, null=True)
#     cou_sa_status = models.CharField(max_length=50, db_collation='utf8mb4_general_ci', blank=True, null=True)

#     class Meta:
#         unique_together = ("id", "master")
#         managed = True
#         db_table = 'summary_registration'


# class Religion(models.Model):
#     religion_name = models.CharField(max_length = 50,blank=True, null=True)
    
#     class Meta:
#         managed = True
#         db_table = 'summary_religion'

# class Occupation(models.Model):
#     occupation_id = models.CharField(max_length=100,blank=True, null=True)
#     occupation_name = models.CharField(max_length=100,blank=True, null=True)
#     class Meta:
#         managed = True
#         db_table = 'summary_occupation'

# class Gender(models.Model):
#     gender_type = models.CharField(max_length=15,blank=True, null=True)
#     class Meta:
#         managed = True
#         db_table = 'summary_gender'

# class Caste(models.Model):
#     caste_id = models.CharField(max_length=30,blank=True, null=True)
#     caste_name = models.CharField(max_length=30,blank=True, null=True)
#     class Meta:
#         managed = False
#         db_table = 'summary_caste'

# class DistrictMapping(models.Model):
#     district_type = models.CharField(max_length= 50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     district_name = models.CharField(max_length= 50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     block_name = models.CharField(max_length= 50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     ac_name = models.CharField(max_length= 50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     gp_name = models.CharField(max_length= 50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     municipality_name = models.CharField(max_length= 50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     ward_name = models.CharField(max_length= 50, db_collation='utf8mb4_general_ci', blank=True, null=True)
#     village_name = models.CharField(max_length= 50, db_collation='utf8mb4_general_ci', blank=True, null=True)
    
#     class Meta:
#         managed = True
#         db_table = 'summary_districtmapping'

# class Category(models.Model):
#     #id = models.BigAutoField(primary_key=True)
#     category_name = models.CharField(max_length=20,blank=True, null=True)

#     class Meta:
#         managed = True
#         db_table = 'summary_category'


# class DataSource(models.Model):
#     #id = models.BigAutoField(primary_key=True)
#     source_name = models.CharField(max_length=30,blank=True, null=True)

#     class Meta:
#         managed = True
#         db_table = 'summary_datasource'