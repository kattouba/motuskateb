from android.media import AudioManager, SoundPool
from os.path import dirname, join
import importlib.resources
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import random
import unicodedata


def enlever_accents(texte):
    """
    Remplace les caractères accentués par leurs équivalents non accentués.
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', texte)
        if unicodedata.category(c) != 'Mn'
    )

def charger_fichier_txt(nom_fichier):
    """
    Charge un fichier texte depuis le dossier resources avec un encodage spécifique.
    """
    with importlib.resources.open_binary("motuskateb.resources", nom_fichier) as f:
        return f.read().decode("latin1").splitlines()

class motuskatebApp(toga.App):
    def startup(self):
        # Initialisation de SoundPool pour jouer les sons
        self.sound_pool = SoundPool(5, AudioManager.STREAM_MUSIC, 0)
        self.sound0 = self.sound_pool.load(join(dirname(__file__), "resources/son0.mp3"), 1)
        self.sound1 = self.sound_pool.load(join(dirname(__file__), "resources/son1.mp3"), 1)
        self.sound2 = self.sound_pool.load(join(dirname(__file__), "resources/son2.mp3"), 1)
        self.sound3 = self.sound_pool.load(join(dirname(__file__), "resources/son3.mp3"), 1)

        # Initialisation des variables de jeu
        self.mot_secret = ""
        self.mot_secret_normalise = ""
        self.essais = 0
        self.historique = []

        # Interface principale
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Sélection de la longueur du mot
        self.longueur_label = toga.Label("Choisissez la longueur du mot :", style=Pack(padding=(0, 5)))
        main_box.add(self.longueur_label)

        self.longueur_input = toga.TextInput(placeholder="Entre 5 et 9", style=Pack(padding=(0, 5)))
        main_box.add(self.longueur_input)

        # Bouton pour commencer le jeu
        self.commencer_button = toga.Button("Commencer", on_press=self.commencer_jeu, style=Pack(padding=(0, 5)))
        main_box.add(self.commencer_button)

        # Résultat
        self.resultat_label = toga.Label("", style=Pack(padding=(0, 5)))
        main_box.add(self.resultat_label)

        # Entrée pour les essais
        self.entree = toga.TextInput(placeholder="Entrez un mot", style=Pack(padding=(0, 5)))
        main_box.add(self.entree)

        # Bouton pour vérifier
        self.verifier_button = toga.Button("Vérifier", on_press=self.verifier_mot, style=Pack(padding=(0, 5)))
        main_box.add(self.verifier_button)

        # Historique des essais
        self.historique_label = toga.Label("", style=Pack(padding=(0, 5)))
        main_box.add(self.historique_label)

        # Espace flexible pour pousser le bouton en bas
        spacer = toga.Box(style=Pack(flex=1))
        main_box.add(spacer)

        # Bouton pour Jouer encore une fois
        self.playagain_button = toga.Button(
            "Jouer une autre fois", 
            on_press=self.commencer_jeu, 
            style=Pack(padding=(0, 5))
        )
        main_box.add(self.playagain_button)

        # Bouton pour expliquer le mot
        self.expliquer_button = toga.Button(
            "Expliquer le mot",
            on_press=self.expliquer_mot,
            style=Pack(padding=(0, 5))
        )
        self.expliquer_button.enabled = False  # Désactivé par défaut
        main_box.add(self.expliquer_button)

        # Ajouter une WebView pour afficher les pages Web
        self.webview = toga.WebView(style=Pack(flex=1))
        self.webview.visible = False
        main_box.add(self.webview)

        # Bouton pour revenir au jeu
        self.retour_button = toga.Button(
            "Retour au jeu",
            on_press=self.retourner_jeu,
            style=Pack(padding=(0, 5))
        )
        self.retour_button.visible = False
        main_box.add(self.retour_button)

        # Fenêtre principale
        self.main_window = toga.MainWindow(title="motuskateb")
        self.main_window.content = main_box
        self.main_window.show()

    def jouer_son(self, sound):
        """
        Joue un son à l'aide de SoundPool.
        """
        self.sound_pool.play(sound, 1.0, 1.0, 0, 0, 1.0)

    def commencer_jeu(self, widget):
        """
        Initialise un nouveau jeu.
        """
        self.essais = 0
        self.historique = []
        self.historique_label.text = ""
        self.expliquer_button.enabled = False  # Désactive le bouton expliquer
        self.webview.visible = False
        self.retour_button.visible = False
        
        # Jouer le Générique
        self.jouer_son(self.sound0)

        longueur = self.longueur_input.value

        if longueur not in ["5", "6" , "7" , "8" , "9"]:
            self.resultat_label.text = "Erreur : Longueur invalide. Entrez entre 5 et 9."
            return
        
        # Charger un mot secret depuis le fichier txt
        fichier_nom = f"data{longueur}.txt"
        try:
            mots = charger_fichier_txt(fichier_nom)
        except FileNotFoundError:
            self.resultat_label.text = f"Erreur : Fichier {fichier_nom} introuvable."
            return

        self.mot_secret = random.choice(mots).strip().lower()
        self.mot_secret = ''.join(filter(str.isalpha, self.mot_secret))  # Supprime les caractères non-alphabétiques
        self.mot_secret_normalise = enlever_accents(self.mot_secret)
        self.resultat_label.text = f"Mot de {longueur} lettres sélectionné ! Essayez maintenant."

    def verifier_mot(self, widget):
        """
        Vérifie le mot entré par l'utilisateur.
        """
        if not self.mot_secret:
            self.resultat_label.text = "Veuillez commencer un jeu d'abord."
            return

        mot = enlever_accents(self.entree.value.strip().lower())
        longueur = len(self.mot_secret_normalise)

        if len(mot) != longueur:
            self.resultat_label.text = f"Erreur : Mot de {longueur} lettres attendu."
            self.entree.value = ""  # Efface la saisie même en cas d'erreur
            self.essais += 1
            if self.essais >= 10:
                self.jouer_son(self.sound3)
                self.resultat_label.text = f"Perdu ! Le mot était : {self.mot_secret}"
            return

        resultat = []
        mot_secret_temp = list(self.mot_secret_normalise)

        # Vérifier les lettres bien placées
        for i in range(len(mot)):
            if mot[i] == self.mot_secret_normalise[i]:
                resultat.append(mot[i].upper())
                mot_secret_temp[i] = None
            else:
                resultat.append(".")

        # Vérifier les lettres mal placées
        for i in range(len(mot)):
            if mot[i] != self.mot_secret_normalise[i] and mot[i] in mot_secret_temp:
                resultat[i] = mot[i]
                mot_secret_temp[mot_secret_temp.index(mot[i])] = None

        # Mettre à jour l'historique
        self.historique.append(f"{mot} -> {' '.join(resultat)}")
        self.historique_label.text = "\n".join(self.historique)

        # Effacer le contenu de la zone de saisie
        self.entree.value = ""

        if mot == self.mot_secret_normalise:
            self.jouer_son(self.sound2)
            self.resultat_label.text = f"Bravo ! Mot trouvé : {self.mot_secret}"
            self.essais = 0
            self.expliquer_button.enabled = True  # Activer le bouton expliquer
        elif self.essais < 10:
            self.jouer_son(self.sound1)
            self.essais += 1
        else:
            self.jouer_son(self.sound3)
            self.resultat_label.text = f"Perdu ! Le mot était : {self.mot_secret}"
            self.expliquer_button.enabled = True  # Activer le bouton expliquer

    def expliquer_mot(self, widget):
        """
        Charge l'explication du mot dans une WebView intégrée, en affichant uniquement les définitions pertinentes.
        """
        # Efface l'historique avant d'expliquer le mot
        self.historique = []
        self.historique_label.text = ""

        base_url = "https://www.littre.org/search/definitions?_hasdata=&f1="
        mot_a_expliquer = self.mot_secret
        url = f"{base_url}{mot_a_expliquer}"

        try:
            custom_script = """
            document.addEventListener('DOMContentLoaded', function() {
                document.body.innerHTML = '';
                var matchingDefinitions = document.querySelector('ol.matching-definitions');
                if (matchingDefinitions) {
                    document.body.appendChild(matchingDefinitions);
                } else {
                    document.body.innerHTML = '<p>Aucune définition trouvée.</p>';
                }
            });
            """
            self.webview.url = url
            self.webview.on_load = lambda _: self.webview.evaluate_javascript(custom_script)
            self.webview.visible = True
            self.retour_button.visible = True
        except Exception as e:
            self.resultat_label.text = "Erreur : Impossible de charger l'explication."
            print(f"Erreur lors du chargement de l'URL : {e}")

    def retourner_jeu(self, widget):
        """
        Cache la WebView, efface son contenu et retourne à l'interface principale.
        """
        self.webview.set_content("", "<html><body></body></html>")  # Réinitialiser le contenu de la WebView
        self.webview.visible = False
        self.retour_button.visible = False

def main():       
    return motuskatebApp()
