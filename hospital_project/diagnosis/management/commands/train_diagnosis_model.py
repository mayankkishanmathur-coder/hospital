from django.core.management.base import BaseCommand
from django.conf import settings
import os
from diagnosis.ml_model import get_diagnosis_model


class Command(BaseCommand):
    help = 'Train the diagnosis model using a CSV dataset'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data',
            type=str,
            required=True,
            help='Path to the CSV dataset file'
        )
        parser.add_argument(
            '--tune',
            action='store_true',
            default=False,
            help='Enable hyperparameter tuning (only for larger datasets)'
        )
        parser.add_argument(
            '--cv',
            action='store_true',
            default=True,
            help='Enable cross-validation (disable with --no-cv)'
        )

    def handle(self, *args, **options):
        data_path = options['data']
        use_tuning = options.get('tune', False)
        use_cv = options.get('cv', True)
        
        if not os.path.exists(data_path):
            self.stdout.write(
                self.style.ERROR(f'Dataset file not found: {data_path}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting model training with dataset: {data_path}')
        )
        
        try:
            model = get_diagnosis_model()
            success = model.train(
                data_path, 
                use_hyperparameter_tuning=use_tuning,
                use_cross_validation=use_cv
            )
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✓ Model trained and saved successfully!')
                )
                self.stdout.write(
                    f'  Symptoms found: {len(model.symptom_list)}'
                )
                self.stdout.write(
                    f'  Conditions: {len(model.condition_encoder.classes_)}'
                )
                self.stdout.write(
                    f'  Specializations: {len(model.specialization_encoder.classes_)}'
                )
                
                # Display CV scores if available
                if model.cv_scores:
                    self.stdout.write('\n📊 Cross-Validation Scores:')
                    for task, scores in model.cv_scores.items():
                        self.stdout.write(
                            f'  {task}: {scores["mean"]:.4f} (+/- {scores["std"]:.4f})'
                        )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Failed to train model')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error during training: {str(e)}')
            )

