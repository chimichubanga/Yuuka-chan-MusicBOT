from tqdm import tqdm

class ProgressBar:
    def __init__(self, stages):
        self.total_steps = 100
        self.steps_per_stage = self.total_steps // stages
        self.loading_bar = tqdm(
            total=self.total_steps, 
            desc="Запуск бота", 
            bar_format="{l_bar}{bar} [Время: {elapsed}]", 
            ncols=100
        )

    def update_stage(self, stage_name):
        # Обновление стадии и прогресс-бара
        self.loading_bar.set_description(stage_name)
        for _ in range(self.steps_per_stage):
            self.loading_bar.update(1)

    def finish(self):
        # Завершение прогресс-бара
        remaining_steps = self.total_steps - self.loading_bar.n
        for _ in range(remaining_steps):
            self.loading_bar.update(1)
        self.loading_bar.close()
