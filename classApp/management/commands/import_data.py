import os
import json
from django.core.management.base import BaseCommand
from classApp.models import College, Major

class Command(BaseCommand):
    help = 'Imports Colleges and Majors from JSON'

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Adjusted path to go up one level from commands/ to management/
        json_path = os.path.join(current_dir, 'colleges.json')

        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"File NOT found at: {json_path}"))
            return

        with open(json_path, 'r') as file:
            data = json.load(file)

        for level, colleges in data.items():
            is_graduate = (level == "Graduate")
            
            for college_name, majors in colleges.items():
                college_obj, _ = College.objects.get_or_create(name=college_name)
                
                for item in majors:
                    if isinstance(item, str):
                        major_name = item
                    elif isinstance(item, dict):
                        # Pulls the key name (e.g., 'Business Administration')
                        major_name = list(item.keys())[0]

                    # Now creates a unique entry for every major + college combination
                    # Major name stays clean without level parentheses - is_graduate flag handles the distinction
                    Major.objects.get_or_create(
                        name=major_name,
                        college=college_obj,
                        defaults={'is_graduate': is_graduate}
                    )
        
        self.stdout.write(self.style.SUCCESS('Successfully imported data!'))
