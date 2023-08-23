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
import requests