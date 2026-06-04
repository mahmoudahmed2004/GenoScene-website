# GenoScene AI deployment

The production prediction flow is:

1. `training/train_phenotype_model.py` trains from `ai/final_merged_3.csv`.
2. The compact trained artifact is saved to `model/phenotype-model.json`.
3. `api/analyze.js` loads that artifact and performs inference in a Vercel Function.
4. `script.js` sends uploaded SNP CSV rows to `/api/analyze` and renders the returned probabilities.

The large Python experiment server is not started on Vercel. Training happens
before deployment, while production requests only run the compact model.

## Retrain

```powershell
pip install -r requirements.txt
npm run train:model
npm test
```

Commit the updated `model/phenotype-model.json` after retraining.

For local development, run `npm run dev` and open `http://localhost:3000`.

## Deploy with GitHub and Vercel

1. Push the repository to GitHub.
2. Import that repository in Vercel and keep the project root as the root directory.
3. Vercel will serve the static site and automatically deploy `api/analyze.js` as `/api/analyze`.
4. No environment variables or build command are required.

`.vercelignore` keeps the training dataset and research code out of the public
deployment. The trained model artifact is included with the API.
