# Page Settings в Tilda · Open Graph + SEO (12 курсов)

Canonical у вас уже на **https**. Ниже — что выровнять в **Страница → Настройки страницы → SEO / Social** (или «Соцсети») для каждой страницы.

Правило: **Title = og:title**, **Description = og:description**, **og:url = canonical https**, **og:image = обложка курса (webp)**.

| URL | Title (и og:title) | Description (и og:description) | og:image |
|-----|--------------------|--------------------------------|----------|
| `/1-klass` | Курс литературного чтения · 1 класс — Читательство | 8 сказок из школьных списков для 1 класса — видео, задания на понимание и личная страница прогресса. Онлайн-школа Читательство. | `https://api.chitatelstvo.ru/assets/course-cover-grade-1.webp` |
| `/2-klass` | Курс литературного чтения · 2 класс — Читательство | 8 сказок и повестей для 2 класса — от Пушкина до Андерсена. Видеоуроки, вопросы на смысл, прогресс на платформе Читательство. | `https://api.chitatelstvo.ru/assets/course-cover-grade-2.webp` |
| `/3-klass` | Курс литературного чтения · 3 класс — Читательство | 8 произведений для 3 класса — от пушкинских сказок до «Королевства кривых зеркал». Онлайн-курс Читательство. | `https://api.chitatelstvo.ru/assets/course-cover-grade-3.webp` |
| `/4-klass` | Курс литературного чтения · 4 класс — Читательство | 8 книг для 4 класса — от бажовских сказов до «Пеппи» и Гулливера. Курс литературного чтения Читательство. | `https://api.chitatelstvo.ru/assets/course-cover-grade-4.webp` |
| `/6-8-let` | Курс по внеклассному чтению 6–8 лет — Читательство | 8 любимых книг для детей 6–8 лет — от Плюшевого зайца до Чарли. Внеклассное чтение на платформе Читательство. | `https://api.chitatelstvo.ru/assets/course-cover-extra-6-8.webp` |
| `/9-11-let` | Курс по внеклассному чтению 9–11 лет — Читательство | 8 повестей для детей 9–11 лет — Янссон, Пеннак, Лагерлеф. Внеклассное чтение Читательство. | `https://api.chitatelstvo.ru/assets/course-cover-extra-9-11.webp` |
| `/bukvy-ozhivayut` | Буквы оживают — чтение с 4 лет \| Читательство | Буквы оживают — курс чтения с 4 лет: звук, буква, слог, слово со Словиком. Первая школа, которая готовит читателя с дошкольного возраста. | `https://api.chitatelstvo.ru/assets/course-cover-letters.webp` |
| `/pervye-istorii` | Первые истории — чтение со смыслом \| Читательство | Первые истории — короткие тексты для детей 5–7 лет. Ребёнок читает предложения, понимает смысл и собирает полку книжек со Словиком. | `https://api.chitatelstvo.ru/assets/course-cover-stories.webp` |
| `/veter-v-ivah` | Ветер в ивах — Читательство | Медленное чтение «Ветер в ивах» для детей 6–9 лет — четыре занятия на платформе Читательство. | `https://api.chitatelstvo.ru/assets/course-cover-wind.webp` |
| `/tainstvenny-sad` | Таинственный сад — Читательство | Медленное чтение «Тайного сада» для детей 10–12 лет — четыре занятия, школа Читательство. | `https://api.chitatelstvo.ru/assets/course-cover-garden.webp` |
| `/russkie-skazki-6-9` | Русские сказки — Читательство | Курс «Русские сказки» для детей 6–9 лет — народные и авторские сказки, четыре занятия. | `https://api.chitatelstvo.ru/assets/course-cover-rus-6-9.webp` |
| `/russkie-skazki-10-12` | Русские сказки — Читательство | Курс «Русские сказки» для детей 10–12 лет — разбор сюжета, образов и авторского стиля. | `https://api.chitatelstvo.ru/assets/course-cover-rus-10-12.webp` |

## Чеклист на каждую страницу (2 минуты)

1. Canonical: `https://chitatelstvo.ru/<slug>` (без http, без слэша в конце).
2. Title / Description / Keywords — как в таблице (Keywords — из `SEO-TABLE.md`).
3. Social / OG: title и description **скопировать из SEO**, url = canonical, image = webp из таблицы.
4. Zero Block: вставить свежий файл из `tilda-redirects/` (`v=20260824m`) — внутри уже **Course+Offer, FAQPage, BreadcrumbList**.
5. Опубликовать страницу.

## llms.txt

1. Создать страницу с адресом **`llms.txt`**.
2. Вставить HTML из `tilda-redirects/llms-txt.html` (блок T123 / Zero Block).
3. Опубликовать → проверить `https://chitatelstvo.ru/llms.txt`.
4. Зеркало text/plain: `https://api.chitatelstvo.ru/llms.txt`.

## Индексация (Вебмастер / Search Console)

1. Яндекс.Вебмастер → Переобход → URL `https://chitatelstvo.ru/1-klass` … и остальные 11 + `/llms.txt`.
2. Google Search Console → URL Inspection → Request indexing для тех же https-URL.
3. Sitemap: сейчас в `https://chitatelstvo.ru/sitemap.xml` ещё **http://** — в Tilda: **Настройки сайта → SEO** включить/пересобрать sitemap на **https** (или «сайт только по HTTPS»).
4. Через 2–3 дня: «Страницы в поиске» — нет дублей http/https.
