Fichiers destinés aux étudiants.

Pour vérifier l'état du code, en partant de ce répertoire :
* `cd ../..`
* `source bin/env.sh`
* `anarun 3 bash`
* `source bin/env.sh`
* `cd src/skeletons`
* `oval r` : execute tous les tests du répertoire
* `oval d` : comparer la sortie du dernier run ci-dessus avec la reference

Si les différences de sortie sont voulues, on peut faire de
la dernière sortie la nouvelle référence avec `oval v`.

