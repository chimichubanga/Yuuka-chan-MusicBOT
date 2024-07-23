from tqdm import tqdm

class ProgressBar:
    def __init__(self, stages):
        # Общее количество шагов в прогресс-баре
        self.total_steps = 100
        # Количество шагов на каждую стадию
        self.steps_per_stage = self.total_steps // stages
        # Инициализация прогресс-бара с заданными параметрами
        self.loading_bar = tqdm(
            total=self.total_steps, 
            desc="Запуск бота", 
            bar_format="{l_bar}{bar} [Время: {elapsed}]", 
            ncols=100
        )

    def update_stage(self, stage_name):
        # Обновление описания стадии и прогресс-бара
        self.loading_bar.set_description(stage_name)
        # Обновление прогресс-бара на количество шагов, соответствующее одной стадии
        for _ in range(self.steps_per_stage):
            self.loading_bar.update(1)

    def finish(self):
        # Завершение прогресс-бара, заполняя оставшиеся шаги
        remaining_steps = self.total_steps - self.loading_bar.n
        for _ in range(remaining_steps):
            self.loading_bar.update(1)
        # Закрытие прогресс-бара
        self.loading_bar.close()
