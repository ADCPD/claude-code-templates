# CLAUDE CODE

Installation de Claude Code

### Prérequis

Node.js 18+

#### Vérifiez d'abord si Node.js est installé :

```bash 
node --version
```

#### Installation de Claude Code via npm :

```bash 
npm install -g @anthropic-ai/claude-code
```

#### Tester si Claude est bien installé : 

```bash 
claude --version
```

#### Dans votre dossier system : 

```bash 
C://Users/_USER_/.claude/settings.json
```

#### Ajouter cette configuration : remplacer la valeur de la clé `"ANTHROPIC_AUTH_TOKEN"`

```json
{
  "env": {
    "CLAUDE_CODE_GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe",
    "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
    "ANTHROPIC_AUTH_TOKEN": "#MON TOKEN GENERER à PARTIR DE https://openrouter.ai/",
    "ANTHROPIC_API_KEY": "",
    "ANTHROPIC_MODEL": "openrouter/free"
  },
  "autoUpdatesChannel": "latest",
  "effortLevel": "high"
}

```

Si vous n'avez pas encore une clé `"ANTHROPIC_AUTH_TOKEN"`, rendez-vous au `https://openrouter.ai/`. 
Ensuite demander la création d'une nouvelle `API KEY`, definisser un NOM pour votre api et garder tout les autres champs par defaut.

#### Lancer claude : 

```bash
cd C://Users/_USER_

# si claude deja ouvert 
claude logout

# relance Claude
claude
```


