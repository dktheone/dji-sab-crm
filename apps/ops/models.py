from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from country_state_city import State, City
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.emp.utils import generate_random_key
import os

from apps import cdata 


