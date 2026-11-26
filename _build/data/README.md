# Lineup data

`lineups_free.json` feeds the map pages (`/lineups/<map>/`). It holds only the **free** lineups of the
seven Active Duty maps, with cleaned position names, a readable throw and the video file name on the CDN.
Pro lineups are counted (`total`) but their videos are not listed, because this repository is public.

It is made from the app's lineup export (sheet "New Nades Schema" of the app data table, version 1.0.44):
the `landing_start_association` rows joined with `nades`, `start_position` and `landing_position`,
keeping rows where `is_free` is true. To refresh it, export the table again and rebuild this file the same way,
then run `python3 _build/build.py`.

Fields per lineup: `side` (T/CT), `type` (smoke, flash, molotov, he), `from`, `to`, `throw`
(movement · technique), `tag` (Retake, One-way, Insta smoke, Pop flash, Fake, Lurk, Reveal HE or null)
and `video` (file name under `cdn`).
