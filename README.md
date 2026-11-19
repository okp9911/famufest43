Jak přidat filmy (vše přes web GitHubu, nic se neinstaluje)
Nahrajte videa. Otevřete složku films → Add file → Upload files → přetáhněte ukázky → Commit changes.
Požadavky na videa najdete níže v části „Jaká mají být videa“.
Název souboru může být libovolný, např. Sůl.mp4.
Počkejte 1–3 minuty. GitHub (záložka Actions) sám vytvoří ke každému videu náhled ve složce posters a do tabulky films.csv přidá řádek pro každý nový soubor.
Vyplňte název, autora a délku. Otevřete films.csv → ikona tužky (Edit) → vyplňte řádky → Commit changes:
video;title;author;duration
Sůl.mp4;Sůl;Jana Nováková;14:26
Noc v lese.mp4;Noc v lese;Petr Svoboda;08:03
video je název souboru ve složce films. Ten neměňte.
title (název), author (autor), duration (délka) uvidí návštěvník. Délku pište, jak je vám pohodlné: 14:26 nebo 14 min.
Pořadí řádků je pořadí filmů v prostoru.
Chcete-li film odebrat, smažte jeho soubor ve složce films i jeho řádek v films.csv.

Změny se na webu objeví 1–2 minuty po Commit changes.

Jaká mají být videa
	
Formát	MP4 (H.264)
Rozlišení	1280×720, na šířku 16:9
Délka	6–8 sekund, maximálně 15
Velikost	do 3 MB, maximálně 5 MB (datový tok cca 2 Mbit/s)
Zvuk	není potřeba, web ho nepřehrává
Snímková frekvence	24 nebo 25 fps
Obsah	bez titulků, log a černých políček na začátku a na konci: ukázka se přehrává ve smyčce

Pojistka: pokud je video větší než 5 MB, větší než 1920×1080, delší než 15 sekund nebo není MP4 (H.264), například MOV z iPhonu, GitHub ho po nahrání sám zmenší na 1280×720, zkrátí na 15 sekund a odstraní zvuk. Přes prohlížeč přijímá GitHub soubory do 25 MB, větší nahrát nejde.

První nastavení repozitáře (jednou)
Vytvořit veřejný repozitář na GitHubu a nahrát do něj vše z archivu. Zkontrolovat, že v repozitáři je složka .github/workflows se souborem films.yml. Skryté složky se při přetahování někdy nenahrají; pak klikněte na Add file → Create new file, zadejte název .github/workflows/films.yml a vložte do něj obsah souboru z archivu.
Settings → Pages → Source: Deploy from a branch, větev main, složka / (root) → Save. Za minutu se tam objeví adresa webu ve tvaru https://jmeno.github.io/repozitar/.
Pokud běh na záložce Actions skončí chybou oprávnění: Settings → Actions → General → Workflow permissions → Read and write permissions → Save.
For the web developer (embedding)

The mosaic is a static page; this repository is served by GitHub Pages. Embed it with an iframe:

html
<iframe src="https://USER.github.io/REPO/" title="FAMUFEST films"
        style="display:block;width:100%;height:100vh;border:0" loading="lazy"></iframe>

URL options (combine with &):

Option	Effect
?wheel=ctrl	the wheel zooms only with Ctrl/⌘ held, so the page keeps scrolling over the block (pinch still zooms). Recommended unless the block is the last thing on the page
?live=4	how many clips may play at once

How it loads: on page load only the posters are fetched (130 films × ~40 KB ≈ 5 MB). A clip is downloaded and played only while its film is open, hovered or among the largest frames on screen, at most 4 at a time, and released when the visitor zooms away.

Data: films.csv (video;title;author;duration, UTF-8, ; or ,), videos in films/, posters in posters/<same name>.jpg. tools/prepare.py (run by .github/workflows/films.yml on every push, needs ffmpeg) makes missing posters, converts non-H.264 or non-MP4 uploads to H.264 MP4 without audio, and adds unlisted files to films.csv. If a poster is missing, the page grabs a frame from the clip itself. GitHub Pages limits: 1 GB site, ~100 GB traffic a month (soft).
