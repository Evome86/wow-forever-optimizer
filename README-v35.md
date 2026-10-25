# Forever Optimizer v3.5 – Referenz-Harness

Kumulatives Overlay einschließlich v3.4. ZIP entpacken und Ordnerstruktur in Repository-Root übernehmen.

GitHub Actions → **Forever v3.5 Reference Harness** → Run workflow → Artefakt `forever-v35-reference-harness`.

## Prüffälle
- Skyborne-Horde (2^33), Skyborne-Allianz (2^32), Kombinationen, leere Maske, hohe/kleine Bits.
- `preQuestSingle`: ODER; `preQuestGroup`: UND; beide zusammen; negative Gruppen-IDs.
- Alternative `exclusiveTo`-Erfüllung ist **eine noch nicht gegen vollständigen Quellcode verifizierte Modellannahme**.

**Wichtig:** Das Harness testet ein separates Python-Referenzmodell, **nicht** die originalen Questie-Lua-Funktionen und **nicht** den Spielclient. Grüne Tests sind kein Beweis für Quest-Freigabe. Gate bleibt `BLOCKED_RUNTIME_AND_INGAME_VALIDATION`. Für die nächste Stufe müssen wir die echten Lua-Funktionen in isolierter Laufzeit mit Mocks ausführen und gegen die Referenzfälle vergleichen.
