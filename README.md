### Workflow scheduler

- 1. Definition der Schichten (Standortleiter)
Für jeden Tag des Zielmonats: welche Schichtarten existieren (Start/Ende, Rolle), und wie viele Slots je Schicht (z. B. 2 Personen parallel).
- 2. Datenaufnahme (Mitarbeitende)
Formular: Name, Standort, Rolle(n)/Skills, min./max. Schichten/Woche, optional Präferenzen (Früh/Spät), sowie Slot-genaue Verfügbarkeit (kann/kann nicht).
- 3. Optimierung
Solver erstellt Zuweisungen, respektiert harte Constraints, optimiert weiche (Fairness, Präferenzen, Kontinuität).
- 4. Output
Dienstplan pro Standort/Woche/Monat (CSV/ICS/PDF) + Konfliktberichte.
