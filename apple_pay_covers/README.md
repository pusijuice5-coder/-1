# Обложки курса «Структура взаимодействия банка-эмитента с Apple Pay»

![Превью](preview.jpg)

## Итоговые изображения (Magnific, 2K)

| | Часть 1 — Apple Wallet и добавление карты | Часть 2 — Платежи и управление картой |
|---|---|---|
| Обложка 16:9 | [открыть](https://www.magnific.com/app/creation/bxzz6l65Y2) | [открыть](https://www.magnific.com/app/creation/vQ99lEXa47) |
| Миниатюра 1:1 | [открыть](https://www.magnific.com/app/creation/N2aaBRZ6D9) | [открыть](https://www.magnific.com/app/creation/fH66S92CDY) |

Модель: Google Nano Banana 2.1, разрешение 2K. Для печати или крупного баннера сделайте апскейл в Magnific.

## Референсы (`refs/`)

| Файл | Что это |
|---|---|
| `apple_logo.png` | изумрудное яблоко с логотипом банка |
| `wallet.png` | изумрудный кошелёк |
| `apple_digit.png` | изумрудное яблоко с цифрой |
| `line_pattern.png` | фирменный паттерн из линий |
| `logo_light.png` | логотип для светлого фона: «ipak yuli» чёрным, «bank» и линии зелёным |

## Как это собрано

1. **Базовая сцена (text-to-image).** Белый фон с тонкими вертикальными линиями, серебристый iPhone, предметы из гранёного изумруда, размытые зелёные пятна, левая половина пустая под текст:

   ```
   Wide presentation cover in a clean minimalist Apple-keynote style. Pure white background, divided into five equal columns by very thin, barely visible light-grey vertical lines, like a layout grid. Right half of the frame: a silver iPhone with a plain black screen (no interface), tilted about 30 degrees to the right, floating. In front of the phone, lower left of it, floats a classic wallet with rounded corners and a small snap strap, sculpted from polished emerald crystal ... Two large, very out-of-focus dark-green blurred circles (bokeh) peek in from the top-left edge and the bottom edge. The entire left half of the image is empty white space reserved for a title. Soft even studio lighting, crisp high-end CGI product render, ultra sharp, premium. No text, no letters, no logos.
   ```

2. **Заголовки.** Базовая сцена идёт референсом с промтом «Keep the reference image exactly as it is … and only add typography in the empty white left half: a lime (#E2E860) pill "Часть 1", a thin light-weight sans-serif headline "Apple Pay" / "для банка-эмитента", a subtitle "Apple Wallet и добавление карты"».

3. **Фирменные объекты.** К обложке с текстом добавляются референсы из `refs/` и промт: «Keep image 1 exactly … Replace every apple gem with the exact emerald apple from image N, including the "ipak yuli bank" logo … Place the bank logo from image M small in the top-left corner above the lime pill … Replace the wallet with an exact copy of the emerald wallet from image K».

4. **Миниатюры.** Референсом служит `apple_digit.png`: «the exact emerald apple from image 2 — same shape, stem, no bite — with the number "2" instead of "0", in exactly the same white bold sans-serif style». Миниатюра «1» делается с готовой «2» в качестве референса, чтобы серия была единой.
