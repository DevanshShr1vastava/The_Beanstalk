import csv
from django.core.management.base import BaseCommand
from eva01.models import questionBank

class Command(BaseCommand):
    help = 'Import questions from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be imported')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row

            for row in reader:
                questionBank.objects.create(
                    qID = row[0], 
                    questions = row[1], 
                    op1 = row[2], 
                    op2 = row[3], 
                    op3 = row[4], 
                    op4 = row[5], 
                    CorrectAnswer = row[6], 
                    option_number = row[7], 
                    difficulty = row[8], 
                    domain = row[9], 
                    subdomain = row[10], 
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported questions from "%s"' % csv_file))
