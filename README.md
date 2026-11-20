## Jak přidat filmy (vše přes web GitHubu, nic se neinstaluje)

1. **Nahrajte videa.** Otevřete složku `films` → **Add file → Upload files** → přetáhněte ukázky → **Commit changes**.
   - Požadavky na videa najdete níže v části „Jaká mají být videa“.
   - Název souboru může být libovolný, např. `Sůl.mp4`.
2. **Počkejte 1–3 minuty.** GitHub (záložka **Actions**) sám vytvoří ke každému videu náhled ve složce `posters` a do tabulky `films.csv` přidá řádek pro každý nový soubor.
3. **STILLS.** Pokud chcete u filmu vlastní obrázek místo automatického náhledu, nahrajte ho do složky `posters` se **stejným názvem jako video**, jen s příponou obrázku: k videu `Sůl.mp4` patří `Sůl.jpg` (nebo `.png`, `.webp`). Velikost nevadí, GitHub ho sám zmenší na 960 px. Still se dá nahrát před videem i po něm a GitHub ho nikdy nepřepíše. Chcete-li ho vyměnit, nahrajte nový se stejným názvem; chcete-li zpět automatický náhled, still smažte.
4. **Vyplňte název, autora a délku.** Otevřete `films.csv` → ikona tužky (**Edit**) → vyplňte řádky → **Commit changes**:

```
video;title;author;duration
Sůl.mp4;Sůl;Jana Nováková;14:26
Noc v lese.mp4;Noc v lese;Petr Svoboda;08:03
```

- `video` je název souboru ve složce `films`. Ten neměňte.
- `title` (název), `author` (autor), `duration` (délka) uvidí návštěvník. 
- Pořadí řádků je pořadí filmů v prostoru.
- Chcete-li film odebrat, smažte jeho soubor ve složce `films` i jeho řádek v `films.csv`.

Změny se na webu objeví 1–2 minuty po **Commit changes**.

## Jaká mají být videa

| | |
|---|---|
| Formát | **MP4 (H.264)** |
| Rozlišení | **1280×720**, na šířku 16:9 |
| Délka | **6–8 sekund**, maximálně 15 |
| Velikost | **do 3 MB**, maximálně 5 MB (datový tok cca 2 Mbit/s) |
| Zvuk | není potřeba, web ho nepřehrává |
| Snímková frekvence | 24 nebo 25 fps |
| Obsah | bez titulků, log a černých políček na začátku a na konci: ukázka se přehrává ve smyčce |

---

## Pro webového vývojáře (vložení na web)

Stránka je statická a běží na GitHub Pages na adrese **https://okp9911.github.io/famufest43/**. Na famufest.cz ji vložte pomocí iframe:

```html
<iframe src="https://okp9911.github.io/famufest43/?wheel=ctrl" title="FAMUFEST films"
        style="display:block;width:100%;height:90vh;border:0" loading="lazy"></iframe>
```

Na telefonu prst uvnitř bloku posouvá prostor filmů místo stránky, proto nechte blok o něco nižší než obrazovku (jako výše, `90vh`)
Parametry v URL (lze kombinovat pomocí `&`):

| Parametr | Co dělá |
|---|---|
| `?wheel=ctrl` | kolečko myši přibližuje jen se stisknutým Ctrl/⌘, takže stránka se nad blokem dál normálně posouvá (gesto sevření na touchpadu přibližuje dál). Doporučeno, pokud blok není úplně dole na stránce |
| `?live=4` | kolik ukázek se může přehrávat najednou |

Jak se stránka načítá: při otevření se stahují jen náhledy (130 filmů × cca 40 KB ≈ 5 MB). Ukázka se stáhne a přehrává, jen když je film otevřený, je na něm kurzor nebo patří k největším ostrým políčkům na obrazovce, maximálně 4 najednou, a po oddálení se zase uvolní.

Data: `films.csv` (`video;title;author;duration`, UTF-8, oddělovač `;` nebo `,`), videa ve složce `films/`, náhledy v `posters/<stejný název>.jpg`. Skript `tools/prepare.py` (spouští ho `.github/workflows/films.yml` při každém nahrání, potřebuje ffmpeg) vytvoří chybějící náhledy, převede videa, která nejsou H.264 MP4, na H.264 MP4 bez zvuku a doplní do `films.csv` soubory, které tam chybí. Pokud náhled chybí, stránka si vezme políčko přímo z ukázky. Limity GitHub Pages: web do 1 GB, provoz cca 100 GB měsíčně (měkký limit).
