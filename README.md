# UML Diagram Generator (Sequence & Activity)

Консольное приложение на Python 3.11+ для автоматизированного проектирования
диаграмм последовательности и деятельности. Работает без внешних зависимостей.

## Запуск

```bash
# REPL
python run.py --repl

# Рендер одного файла
python run.py --file samples/activity_sample.json --render activity
python run.py --file samples/sequence_sample.json --render sequence

# Анализ + отчёт
python run.py --file samples/activity_sample.json --render activity --analyze --export markdown

# Экспорт через плагин Mermaid
python run.py --file samples/activity_sample.json --export mermaid