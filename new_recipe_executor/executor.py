from steps import get_step_instance


class Executor:
    def __init__(self, recipe, context, logger):
        self.recipe = recipe
        self.context = context
        self.logger = logger

    def execute_all(self):
        self.logger.info('Starting recipe execution')
        for idx, step_data in enumerate(self.recipe.steps):
            step_type = step_data.get('type')
            self.logger.info(f'Executing step {idx+1}: {step_type}')
            try:
                step = get_step_instance(step_type, step_data.get('config', {}), self.logger)
                step.execute(self.context)
                self.logger.info(f'Step {idx+1} completed successfully.')
            except Exception as e:
                self.logger.error(f'Error in step {idx+1} ({step_type}): {e}', exc_info=True)
                raise e
        self.logger.info('Recipe execution completed successfully.')
