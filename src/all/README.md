Zone de développement.

La première étape ci-dessous est nécessaire (`source...`),
parce qu'elle définit `PYTHONPATH` afin de réutiliser
les bibliothèques de `/src/begin` et `/src/end`.

Pour vérifier l'état du code :
* `source ../../bin/env.sh``
* `oval r` : execute tous les tests du répertoire (actuellement find_stars.py)
* `oval d` : comparer la sortie du dernier run ci-dessus avec la reference

Si les différences de sortie sont voulues, on peut faire de
la dernière sortie la nouvelle référence avec `oval v`.

