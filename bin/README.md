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


---
# Tests

Pour verifier le bon fonctionnement du nouveau diff de oval,
l'exécution de `oval d` devrait produire :

```
ERROR: oval_test_diff_dict: redefinition of var 3 in output
ERROR: oval_test_diff_dict: redefinition of var1 in reference
oval_test_diff_dict: unexpected var 1
oval_test_diff_dict: for var 3, hello world ! != hello world
oval_test_diff_dict: lacking var1
```

