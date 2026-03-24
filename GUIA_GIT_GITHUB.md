# 🐶 Guía: Cómo usar Git y GitHub con Code Puppy

> Guía creada para el equipo. Sigue estos pasos y en 15 minutos tendrás tus códigos guardados y compartidos en GitHub.

---

## ¿Qué es Git y para qué sirve?

- **Git** = una máquina del tiempo para tu código. Guarda cada versión de tus archivos.
- **GitHub** = la nube donde vive tu código. Puedes compartirlo con tu equipo.
- **Code Puppy** = tu asistente de IA que crea el código y lo puede guardar en GitHub por ti. 🐾

---

## Paso 1 — Instalar Git en Windows

Abre **PowerShell** y pega este comando (descarga Git desde el artifactory interno de Walmart):

```powershell
$webClient = New-Object System.Net.WebClient
$webClient.Proxy = New-Object System.Net.WebProxy('http://sysproxy.wal-mart.com:8080')
$webClient.DownloadFile(
  'https://generic.ci.artifacts.walmart.com/artifactory/github-releases-generic-release-remote/git-for-windows/git/releases/download/v2.47.1.windows.2/Git-2.47.1.2-64-bit.exe',
  'C:\Users\TU_USUARIO\Downloads\Git-installer.exe'
)
```

Luego instálalo en silencio:

```powershell
C:\Users\TU_USUARIO\Downloads\Git-installer.exe /VERYSILENT /NORESTART
```

> ⚠️ Reemplaza `TU_USUARIO` con tu nombre de usuario de Windows (el que aparece en `C:\Users\`).

---

## Paso 2 — Configurar tu identidad en Git

Esto solo se hace **una vez**. Abre PowerShell y escribe:

```powershell
$git = 'C:\Users\TU_USUARIO\AppData\Local\Programs\Git\cmd\git.exe'

& $git config --global user.name "TU_NOMBRE"
& $git config --global user.email "tu_usuario@walmart.com"
& $git config --global init.defaultBranch main
& $git config --global credential.helper manager
```

> 💡 Reemplaza `TU_NOMBRE` y `tu_usuario@walmart.com` con tus datos reales.

---

## Paso 3 — Crear tu cuenta en GitHub

1. Ve a 👉 **[github.com](https://github.com)** y regístrate
2. Usa tu correo personal o de Walmart
3. Activa la verificación en dos pasos (recomendado)

---

## Paso 4 — Crear un repositorio en GitHub

Un **repositorio** es como una carpeta especial en la nube para tu proyecto.

1. En GitHub, clic en el botón verde **"New"** (arriba a la izquierda)
2. Configúralo así:
   - **Repository name:** `nombre-de-tu-proyecto`
   - **Visibility:** `Private` ✅ (solo tú y quien invites pueden verlo)
   - ⚠️ **NO marques** "Add a README" ni ".gitignore"
3. Clic en **"Create repository"**
4. Copia la URL que te da GitHub, se ve así:
   ```
   https://github.com/TU_USUARIO/nombre-de-tu-proyecto.git
   ```

---

## Paso 5 — Crear tu Token de Acceso (PAT)

GitHub ya no acepta contraseñas normales. Necesitas un **Token Personal**.

1. Ve a 👉 **[github.com/settings/tokens](https://github.com/settings/tokens)**
   - O navega: Foto de perfil → Settings → Developer Settings → Personal access tokens → **Tokens (classic)**
2. Clic en **"Generate new token (classic)"**
3. Configúralo:
   - **Note:** `code-puppy` (o cualquier nombre)
   - **Expiration:** `90 days`
   - **Scopes:** ✅ marca solo **`repo`**
4. Clic en **"Generate token"**
5. **¡CÓPIALO AHORA!** Solo lo ves una vez 👀
   - Se ve así: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Paso 6 — Conectar tu carpeta local con GitHub

En la carpeta de tu proyecto, ejecuta:

```powershell
$git = 'C:\Users\TU_USUARIO\AppData\Local\Programs\Git\cmd\git.exe'
$token = 'ghp_TU_TOKEN_AQUI'
$usuario = 'TU_USUARIO_GITHUB'
$repo = 'nombre-de-tu-proyecto'

# Inicializar Git en la carpeta
Set-Location 'C:\ruta\a\tu\proyecto'
& $git init
& $git add .
& $git commit -m 'Primer commit'

# Conectar con GitHub
& $git remote add origin "https://$usuario`:$token@github.com/$usuario/$repo.git"
& $git push -u origin main
```

> ✅ Si todo sale bien, verás algo como: `* [new branch] main -> main`

---

## 📅 Flujo diario — Guardar y subir cambios

Cada vez que hagas cambios en tu código, usa estos 3 comandos:

```bash
# 1. Ver qué cambió
git status

# 2. Agregar los cambios
git add .

# 3. Guardar con mensaje + subir a GitHub
git commit -m "descripcion de lo que hice"
git push
```

### El atajo en una sola línea 🚀
```bash
git add . && git commit -m "mi mensaje" && git push
```

---

## 📖 Comandos útiles para el día a día

| Comando | ¿Qué hace? |
|---|---|
| `git status` | Ver qué archivos cambiaron |
| `git add .` | Preparar TODOS los cambios |
| `git add archivo.py` | Preparar solo un archivo |
| `git commit -m "mensaje"` | Guardar los cambios con descripción |
| `git push` | Subir a GitHub |
| `git pull` | Bajar cambios de GitHub |
| `git log --oneline` | Ver historial de cambios |
| `git diff` | Ver exactamente qué líneas cambiaron |

---

## 🛡️ ¿Qué archivos NO subir a GitHub?

Crea un archivo llamado `.gitignore` en tu proyecto con esto:

```
# Datos grandes
*.json
*.csv
*.xlsx

# Python
__pycache__/
venv/
.env

# HTML generados
*.html

# Sistema
.DS_Store
Thumbs.db
```

> ⚠️ **Nunca subas** datos con información personal (CURP, RFC, datos de pacientes, etc.)

---

## 💡 Tip: Deja que Code Puppy lo haga por ti

Si estás trabajando con Code Puppy, solo dile:

> *"Guarda los cambios en GitHub"*

y él hace el `add`, `commit` y `push` automáticamente. ¡Para eso está el perrito! 🐾

---

## ❓ ¿Tienes dudas?

- Pregúntale a **Code Puppy** directamente en tu terminal
- Comunidad interna: [Slack #code-puppy](https://walmart.enterprise.slack.com/archives/C094Y1D24JY)
- Aprende más en el doghouse: [puppy.walmart.com/doghouse](https://puppy.walmart.com/doghouse)

---

*Guía generada con ❤️ y Code Puppy 🐶 — Walmart Tech, 2026*
