### Workflow scheduler

# Definition der Schichten (Standortleiter)
Für jeden Tag des Zielmonats: welche Schichtarten existieren (Start/Ende, Rolle), und wie viele Slots je Schicht (z. B. 2 Personen parallel).
Datenaufnahme (Mitarbeitende)
Formular: Name, Standort, Rolle(n)/Skills, min./max. Schichten/Woche, optional Präferenzen (Früh/Spät), sowie Slot-genaue Verfügbarkeit (kann/kann nicht).
Optimierung
Solver erstellt Zuweisungen, respektiert harte Constraints, optimiert weiche (Fairness, Präferenzen, Kontinuität).
Output
Dienstplan pro Standort/Woche/Monat (CSV/ICS/PDF) + Konfliktberichte.
