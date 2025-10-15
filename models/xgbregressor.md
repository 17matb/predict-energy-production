# XGBoost Regressor (Matthis)

## Préparation des données

1. Je récupère mes données depuis ma base de données. Dans ces données se trouve une colonne `date` que j'utilise pour créer de nouvelles features utilisables avec ce modèle.

2. Après avoir converti la colonne `date` au format datetime, j'isole `year`, `month`, `day_of_year`, `day_of_week` dans de nouvelles colonnes.

3. À partir de ces nouvelles colonnes, j'en crée de nouvelles qui seront le sinus et le cosinus de `month`, `day_of_year`, `day_of_week` et j'en profite pour faire de même avec la colonne `winddirection_10m_dominant`.

```python
self.data['month_sin'] = np.sin(2 * np.pi * self.data['month'] / 12)
self.data['month_cos'] = np.cos(2 * np.pi * self.data['month'] / 12)
```

4. Je me débarrasse ensuite des colonnes qui ne semblent plus être utiles (`date`, `month`, `day_of_year`, `day_of_week`, `winddirection_10m_dominant`)

## Entraînement du modèle

L'idée ici est de tester XGBoost Regressor, un modèle plutôt solide et réputé comme performant sur les problèmes de régression tabulaire.

1. Je sépare donc mes données en jeu d’entraînement (80%) et jeu de test (20%) :

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=1
)
```

2. Ensuite, je configure et entraîne le modèle avec des hyperparamètres assez standards :

- `n_estimators` = 500 -> pour laisser le modèle apprendre suffisamment sans le brider
- `learning_rate` = 0.05 -> un apprentissage progressif pour éviter de diverger
- `max_depth` = 6 -> valeur par défaut, compromis entre capacité d'apprentissage et surapprentissage
- `subsample` = 0.8 -> on introduit un peu d’aléatoire pour la robustesse
- `reg_lambda` = 1.2 -> légère régularisation pour calmer le modèle

## Résultats

Une fois l'entrainement effectué, je génère les prédictions et calcule quelques métriques.

```python
{'mean absolute error': 12.467737278806387, 'mean squared error': 729.6236868283416, 'r squared': 0.29786328130326845, 'root mean squared error': 27.011547286824236}
```

`Mean Absolute Error` : En moyenne, le modèle se trompe de 12.47 unités (en valeur absolue). Chaque prédiction est à plus ou moins 12.47 de la vraie valeur.

`Mean Squared Error` : L'erreur moyenne au carré indique ici la présence d'assez grosses erreurs qu'elle pénalise lourdement.

`Root Mean Squared Error` : Ici le fait que la racine carrée du MSE soit bien supérieure au MAE confirme la présence de grosses erreurs ponctuelles.

`R2` : Ce score nous indique que 29% de la variance est expliquée et donc qu'une grande partie de la tendance réelle échappe au modèle.

## Pistes d'amélioration

Malgré ces résultats peu concluants, on peut mentionner quelques axes d'amélioration.

- Meilleur feature engineering
- Inspection des features les plus importantes
- Tuning d'hyperparamètres sérieux

Je pense que l'on peut conclure en disant que ce modèle n'est pas encore prêt pour performer dans le monde réel mais qu'il peut servir de base afin d'itérer et d'avancer vers notre objectif.
