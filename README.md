# claude-code Skills

> claude code best practice 


--- 

## Statusline Claude Code

<img width="1279" height="55" alt="image" src="https://github.com/user-attachments/assets/f9a913af-5206-407b-94ef-c09924f4ba5e" />

Script de barre de statut pour Claude Code. Il lit le JSON de session que Claude Code envoie sur stdin et affiche une ligne unique, colorée (palette 256 couleurs).

### Aperçu

```
✦ Opus 4.5  projet/sous-dossier  ✓ feature/ma-branche ⇡2  $0.842  +120/-34  ◧ ▓▓▓░░░░░ 38% (76.1k)  ∑ 1.2M/j +48.3M cache
```

### Ce qui est affiché

| Segment | Contenu |
|---|---|
| `✦ Modèle` | Nom d'affichage du modèle actif |
| Dossier | Dossier courant. Si vous êtes dans un sous-dossier du projet, affiche `projet/sous-dossier` |
| Git | Branche (ou SHA court en detached HEAD), `✓` si propre, `●` si modifications en cours, `⇡n` / `⇣n` pour les commits en avance / en retard sur l'upstream |
| Coût | Coût cumulé de la session en USD, sur 3 décimales |
| Lignes | Lignes ajoutées / supprimées pendant la session |
| Contexte | Jauge de 8 cellules, pourcentage et taille du contexte courant. Vert-cyan sous 50 %, orange à partir de 50 %, rouge à partir de 80 % |
| Jour | Tokens consommés aujourd'hui sur toutes les sessions (`input + output + cache_creation`), suivis des relectures de cache (`cache_read`) à part |

Les segments sans donnée (pas de dépôt git, coût absent, aucun token) sont simplement omis.

### Prérequis

- bash
- `jq`
- `awk`
- `git` (pour le segment Git)

### Installation

1. Copier le script et le rendre exécutable :

   ```bash
   cp statusline.sh ~/.claude/statusline.sh
   chmod +x ~/.claude/statusline.sh
   ```

2. Le déclarer dans `~/.claude/settings.json` :

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "~/.claude/statusline.sh"
     }
   }
   ```

3. Relancer Claude Code.

### Test en local

```bash
echo '{"model":{"display_name":"Opus 4.5"},"workspace":{"current_dir":"'"$PWD"'"},"cost":{"total_cost_usd":0.842,"total_lines_added":120,"total_lines_removed":34}}' | ~/.claude/statusline.sh
```

### Détails de fonctionnement

- Fenêtre de contexte : 1M tokens si le nom du modèle contient `1M`, 200k sinon. Le pourcentage est calculé sur cette base, la taille du contexte étant celle de la dernière entrée du transcript (`input + cache_read + cache_creation`).
- Total journalier : calculé en parcourant `~/.claude/projects/*/*.jsonl` pour les entrées horodatées du jour. Le résultat est mis en cache 15 secondes dans `/tmp/cc-statusline-day-AAAA-MM-JJ` pour éviter de rescanner les transcripts à chaque rendu.
- Les relectures de cache sont comptées séparément car elles gonflent fortement le total tout en étant facturées environ dix fois moins.


## Audit Web

Skill qui réalise l'audit d'un projet web (technique, SEO, UX/UI, sécurité) à partir d'un ticket Jira, d'une carte Trello ou d'un simple descriptif. Il produit un artifact de présentation qui détaille chaque étape, ce qui reste à faire, et une estimation tâche par tâche en jours-hommes et en temps Claude Code.

### Utilisation

```
/audit-web PROJ-123
/audit-web https://trello.com/c/xxxx
/audit-web "Site e-commerce en baisse de trafic depuis la refonte"
```

### Méthodologie

| Étape | Contenu | Référence |
|---|---|---|
| 01 Cadrage | Motif de l'audit, périmètre global ou ciblé | 1 j |
| 02 Collecte | Crawl, Search Console / Analytics, inventaire pages, code, dépendances | 2,5 j |
| 03 Diagnostic | Technique, SEO, UX/UI, sécurité | 5 j |
| 04 Synthèse | Causes profondes, impact business | 1,25 j |
| 05 Plan d'action | Feuille de route (quick wins / moyen terme / refonte), rapport, restitution | 3,25 j |

Soit **13 jours-hommes** de référence, contre environ **24 h** avec Claude Code (hors tâches humaines : réunions, heatmaps, restitution orale). Le skill adapte ces tâches et recalcule les totaux selon le ticket.

### Contenu

| Fichier | Rôle |
|---|---|
| `skills/audit-web/SKILL.md` | Déroulé du skill |
| `skills/audit-web/references/methodology.md` | Les 5 étapes, tâches T1.1 → T5.4 et estimations de référence |
| `skills/audit-web/assets/audit-web-grid.html` | Gabarit de l'artifact (clair / sombre) |

### Installation

```bash
cp -r skills/audit-web ~/.claude/skills/
```

Puis relancer Claude Code. L'audit est rédigé dans la langue du ticket.


---
