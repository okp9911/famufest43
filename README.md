# FAMUFEST: мозаика фильмов

Бесконечное пространство фильмов на разной глубине: его можно тянуть мышкой (с инерцией), колесом или щипком лететь вперёд и назад, края нет ни в одну сторону. Курсор работает как лупа. Кадры вне фокуса (слишком близко или далеко) идут через шейдер Lens distortion из Figma. Клик открывает фильм на весь экран с названием, автором и длительностью внизу. Фон #E5E4DF.

## Как добавить фильмы (всё через сайт GitHub, ничего устанавливать не нужно)

1. **Загрузить видео.** Откройте папку `films` → **Add file → Upload files** → перетащите отрывки → **Commit changes**.
   - Требования к видео смотрите ниже, в разделе «Какие должны быть видео».
   - Имя файла любое, например `Sůl.mp4`.
2. **Подождать 1–3 минуты.** GitHub сам (вкладка **Actions**) делает к каждому видео превью в папке `posters`, а в таблицу `films.csv` добавляет строку для каждого нового файла.
3. **Вписать название, автора и время.** Откройте `films.csv` → значок карандаша (**Edit**) → заполните строки → **Commit changes**:

```
video;title;author;duration
Sůl.mp4;Sůl;Jana Nováková;14:26
Noc v lese.mp4;Noc v lese;Petr Svoboda;08:03
```

- `video` — имя файла в папке `films`. Его не трогать.
- `title`, `author`, `duration` — то, что увидит посетитель. Длительность пишется как удобно: `14:26` или `14 min`.
- Порядок строк — это порядок фильмов в мозаике.
- Чтобы убрать фильм, удалите его файл в `films` и его строку в `films.csv`.

Изменения появляются на сайте через 1–2 минуты после **Commit changes**.

## Какие должны быть видео

| | |
|---|---|
| Формат | **MP4 (H.264)** |
| Разрешение | **1280×720**, горизонтально 16:9 |
| Длина | **6–8 секунд**, максимум 15 |
| Вес | **до 3 МБ**, максимум 5 МБ (битрейт около 2 Мбит/с) |
| Звук | не нужен, на сайте его нет |
| Кадр/с | 24 или 25 |
| Содержание | без титров, логотипов и чёрных кадров в начале и в конце: отрывок крутится по кругу |

Страховка: если видео тяжелее 5 МБ, больше 1920×1080, длиннее 15 секунд или не MP4 (H.264), например MOV с iPhone, GitHub после загрузки сам ужмёт его до 1280×720, обрежет до 15 секунд и уберёт звук. Через браузер GitHub принимает файлы до 25 МБ, больше загрузить нельзя.

## Первая настройка репозитория (один раз)

1. Создать репозиторий на GitHub и загрузить в него всё из этого архива. Проверить, что в репозитории появилась папка `.github/workflows` с файлом `films.yml`. Скрытые папки при перетаскивании иногда не загружаются; тогда нажать **Add file → Create new file**, вписать имя `.github/workflows/films.yml` и вставить туда содержимое файла из архива.
2. **Settings → Pages** → Source: **Deploy from a branch**, ветка `main`, папка `/ (root)` → Save. Через минуту там появится адрес сайта, вида `https://имя.github.io/репозиторий/`.
3. Если на вкладке **Actions** запуск падает с ошибкой прав: **Settings → Actions → General → Workflow permissions → Read and write permissions** → Save.

---

## For the web developer (embedding)

The mosaic is a static page; this repository is served by GitHub Pages. Embed it with an iframe:

```html
<iframe src="https://USER.github.io/REPO/" title="FAMUFEST films"
        style="display:block;width:100%;height:100vh;border:0" loading="lazy"></iframe>
```

URL options (combine with `&`):

| Option | Effect |
|---|---|
| `?wheel=ctrl` | the wheel zooms only with Ctrl/⌘ held, so the page keeps scrolling over the block (pinch still zooms). Recommended unless the block is the last thing on the page |
| `?live=4` | how many clips may play at once |

How it loads: on page load only the posters are fetched (130 films × ~40 KB ≈ 5 MB). A clip is downloaded and played only while its film is open, hovered or among the largest frames on screen, at most 4 at a time, and released when the visitor zooms away.

Data: `films.csv` (`video;title;author;duration`, UTF-8, `;` or `,`), videos in `films/`, posters in `posters/<same name>.jpg`. `tools/prepare.py` (run by `.github/workflows/films.yml` on every push, needs ffmpeg) makes missing posters, converts non-H.264 or non-MP4 uploads to H.264 MP4 without audio, and adds unlisted files to `films.csv`. If a poster is missing, the page grabs a frame from the clip itself. GitHub Pages limits: 1 GB site, ~100 GB traffic a month (soft).
