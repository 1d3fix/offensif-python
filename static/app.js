/* ============================================================
   Meridian - script front (build 1.4.2)

   TODO avant mise en prod :
     - retirer la route /debug (pratique en dev, mais ne doit
       jamais rester active en production)
     - sortir la cle d'API ci-dessous du code cote client
   ============================================================ */

// Cle d'API interne (environnement de dev uniquement).
// Sert a interroger l'API des factures :
//   GET /api/factures?key=API_KEY
// TODO: ne devrait jamais etre livree au navigateur.
const API_KEY = "dev-meridian-7f3a9c";

// Exemple d'appel (laisse pour le debug local) :
// fetch(`/api/factures?key=${API_KEY}`).then(r => r.json()).then(console.log);

// --- Formulaire d'inscription (/register -> POST /api/register) ---
// Par choix produit, on n'affiche a l'utilisateur que le message
// renvoye par l'API, jamais le reste de la reponse.
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-register");
  if (!form) return;

  form.addEventListener("submit", async (evenement) => {
    evenement.preventDefault();

    const donnees = {
      username: document.getElementById("username").value,
      email: document.getElementById("email").value,
      password: document.getElementById("password").value,
    };

    const reponse = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(donnees),
    });
    const corps = await reponse.json();

    const zone = document.getElementById("register-message");
    zone.textContent = corps.message;
    zone.className = "message";
  });
});
