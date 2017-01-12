# Quelques utilitaires pour se faciliter la vie

* env.sh : à sourcer dans son bash.
* anarun.sh : pour lancer une commande dans une image docker anaconda 2 ou 3.
* oval.py : traitement de commandes de masse.

## env.sh

Un fichier à sourcer dans son shell.
Rend quelques services :

1. Définit la variable NPAC_ROOT, censée contenir le répertoire local
   racine dans lequel vous devez cloner vos dépôt NPAC, sans changer
   leur nom.
2. Ajoute $NPAC_ROOT/PyPlotCode/bin devant votre PATH
3. Définit quelques alias pour pouvoir taper "oval" au lieu de "oval.py"
   et "anarun" au lieu de "anarun.sh".

## oval.py

Un utilitaire pour émettre des commandes de masse.
EN CHANTIER.

## anarun.sh

Un utilitaire pour lancer un conteneur anaconda 2 ou 3.
EN CHANTIER.

