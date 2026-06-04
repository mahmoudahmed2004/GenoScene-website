import pandas as pd

def phenotypic_prediction(args):
    sample_id = args[0]
    sample_csv = pd.read_csv(args[1], header=0)
    
    df_prediction = sample_csv[['sampleid', 'PBlueEye', 'PIntermediateEye', 'PBrownEye', 
                               'PBlondHair', 'PBrownHair', 'PRedHair', 'PBlackHair', 
                               'PLightHair', 'PDarkHair', 'PVeryPaleSkin', 'PPaleSkin', 
                               'PIntermediateSkin', 'PDarkSkin', 'PDarktoBlackSkin']].copy()
    df_prediction.set_index('sampleid', inplace=True)
    df_prediction = df_prediction.round(3)
    
    def predict_eye_colour(row):
        PBlueEye, PIntermediateEye, PBrownEye = row['PBlueEye'], row['PIntermediateEye'], row['PBrownEye']
        if PBlueEye > PIntermediateEye and PBlueEye > PBrownEye and PBlueEye >= 0.7:
            return "Blue"
        elif PIntermediateEye > PBlueEye and PIntermediateEye > PBrownEye and PIntermediateEye >= 0.7:
            return "Intermediate"
        elif PBrownEye > PIntermediateEye and PBrownEye > PBlueEye and PBrownEye >= 0.7:
            return "Brown"
        else:
            return "Not predicted"
    
    df_prediction['predicted_eye_colour'] = df_prediction.apply(predict_eye_colour, axis=1)
    
    def predict_hair_colour(row):
        PBlondHair, PBrownHair, PRedHair, PBlackHair, PLightHair, PDarkHair = (
            row['PBlondHair'], row['PBrownHair'], row['PRedHair'], 
            row['PBlackHair'], row['PLightHair'], row['PDarkHair']
        )
        
        if (PBlackHair > PBlondHair and PBlackHair > PBrownHair and PBlackHair > PRedHair and 
            PBlackHair >= 0.7 and PDarkHair >= 0.5):
            return "Black"
        elif (PBlackHair > PBlondHair and PBlackHair > PBrownHair and PBlackHair > PRedHair and 
              PBlackHair >= 0.7 and PDarkHair < 0.5):
            return "Black"
        elif (PBlackHair > PBlondHair and PBlackHair > PBrownHair and PBlackHair > PRedHair and 
              PBlackHair < 0.7 and PDarkHair >= 0.5):
            return "Black"
        elif (PBlackHair > PBlondHair and PBlackHair > PBrownHair and PBlackHair > PRedHair and 
              PBlackHair < 0.7 and PDarkHair < 0.5):
            return "Dark brown/black"
        elif (PBlondHair > PBlackHair and PBlondHair > PBrownHair and PBlondHair > PRedHair and 
              PBlondHair >= 0.7 and PLightHair >= 0.95):
            return "Blond"
        elif (PBlondHair > PBlackHair and PBlondHair > PBrownHair and PBlondHair > PRedHair and 
              PBlondHair >= 0.7 and PLightHair < 0.95):
            return "Blond"
        elif (PBlondHair > PBlackHair and PBlondHair > PBrownHair and PBlondHair > PRedHair and 
              PBlondHair < 0.7 and PLightHair >= 0.9):
            return "Blond"
        elif (PBlondHair > PBlackHair and PBlondHair > PBrownHair and PBlondHair > PRedHair and 
              PBlondHair < 0.7 and PLightHair < 0.9):
            return "Dark blond"
        elif (PBrownHair > PBlackHair and PBrownHair > PBlondHair and PBrownHair > PRedHair and 
              PBrownHair >= 0.7 and PLightHair >= 0.8):
            return "Brown"
        elif (PBrownHair > PBlackHair and PBrownHair > PBlondHair and PBrownHair > PRedHair and 
              PBrownHair >= 0.7 and PLightHair < 0.8):
            return "Brown/dark brown"
        elif (PBrownHair > PBlackHair and PBrownHair > PBlondHair and PBrownHair > PRedHair and 
              PBrownHair < 0.7 and PLightHair >= 0.8):
            return "Brown/dark brown"
        elif (PBrownHair > PBlackHair and PBrownHair > PBlondHair and PBrownHair > PRedHair and 
              PBrownHair < 0.7 and PLightHair < 0.8):
            return "Dark brown/black"
        elif (PRedHair > PBlackHair and PRedHair > PBlondHair and PRedHair > PBrownHair and 
              PRedHair >= 0.7 and PLightHair >= 0.9):
            return "Red"
        elif (PRedHair > PBlackHair and PRedHair > PBlondHair and PRedHair > PBrownHair and 
              PRedHair >= 0.7 and PLightHair < 0.9):
            return "Red"
        elif (PRedHair > PBlackHair and PRedHair > PBlondHair and PRedHair > PBrownHair and 
              PRedHair < 0.7 and PLightHair >= 0.9):
            return "Red"
        elif (PRedHair > PBlackHair and PRedHair > PBlondHair and PRedHair > PBrownHair and 
              PRedHair < 0.7 and PLightHair < 0.9):
            return "Red"
        else:
            return "Not predicted"
    
    df_prediction['predicted_hair_colour'] = df_prediction.apply(predict_hair_colour, axis=1)
    
    def predict_skin_colour(row):
        PVeryPaleSkin, PPaleSkin, PIntermediateSkin, PDarkSkin, PDarktoBlackSkin = (
            row['PVeryPaleSkin'], row['PPaleSkin'], row['PIntermediateSkin'], 
            row['PDarkSkin'], row['PDarktoBlackSkin']
        )
        
        if (PVeryPaleSkin > PPaleSkin and PVeryPaleSkin > PIntermediateSkin and 
            PVeryPaleSkin > PDarkSkin and PVeryPaleSkin > PDarktoBlackSkin and 
            PVeryPaleSkin >= 0.9):
            return "Very pale"
        elif (PVeryPaleSkin > PPaleSkin and PVeryPaleSkin > PIntermediateSkin and 
              PVeryPaleSkin > PDarkSkin and PVeryPaleSkin > PDarktoBlackSkin and 
              PVeryPaleSkin >= 0.7 and 
              (PPaleSkin >= 0.15 or PIntermediateSkin >= 0.15 or PDarkSkin >= 0.15 or PDarktoBlackSkin >= 0.15)):
            return "Pale"
        elif (PVeryPaleSkin > PPaleSkin and PVeryPaleSkin > PIntermediateSkin and 
              PVeryPaleSkin > PDarkSkin and PVeryPaleSkin > PDarktoBlackSkin and 
              PVeryPaleSkin >= 0.7 and 
              (PPaleSkin < 0.15 and PIntermediateSkin < 0.15 and PDarkSkin < 0.15 and PDarktoBlackSkin < 0.15)):
            return "Very pale"
        elif (PVeryPaleSkin > PPaleSkin and PVeryPaleSkin > PIntermediateSkin and 
              PVeryPaleSkin > PDarkSkin and PVeryPaleSkin > PDarktoBlackSkin and 
              PVeryPaleSkin >= 0.5):
            return "Very pale"
        elif (PPaleSkin > PVeryPaleSkin and PPaleSkin > PIntermediateSkin and 
              PPaleSkin > PDarkSkin and PPaleSkin > PDarktoBlackSkin and 
              PPaleSkin >= 0.9):
            return "Pale"
        elif (PPaleSkin > PVeryPaleSkin and PPaleSkin > PIntermediateSkin and 
              PPaleSkin > PDarkSkin and PPaleSkin > PDarktoBlackSkin and 
              PPaleSkin >= 0.7 and PVeryPaleSkin >= 0.15):
            return "Pale"
        elif (PPaleSkin > PVeryPaleSkin and PPaleSkin > PIntermediateSkin and 
              PPaleSkin > PDarkSkin and PPaleSkin > PDarktoBlackSkin and 
              PPaleSkin >= 0.7 and 
              (PIntermediateSkin >= 0.15 or PDarkSkin >= 0.15 or PDarktoBlackSkin >= 0.15)):
            return "Intermediate"
        elif (PPaleSkin > PVeryPaleSkin and PPaleSkin > PIntermediateSkin and 
              PPaleSkin > PDarkSkin and PPaleSkin > PDarktoBlackSkin and 
              PPaleSkin >= 0.7 and 
              (PVeryPaleSkin < 0.15 and PIntermediateSkin < 0.15 and PDarkSkin < 0.15 and PDarktoBlackSkin < 0.15)):
            return "Pale"
        elif (PPaleSkin > PVeryPaleSkin and PPaleSkin > PIntermediateSkin and 
              PPaleSkin > PDarkSkin and PPaleSkin > PDarktoBlackSkin and 
              PPaleSkin >= 0.5 and 
              (PVeryPaleSkin > PIntermediateSkin and PVeryPaleSkin > PDarkSkin and PVeryPaleSkin > PDarktoBlackSkin)):
            return "Pale"
        elif (PPaleSkin > PVeryPaleSkin and PPaleSkin > PIntermediateSkin and 
              PPaleSkin > PDarkSkin and PPaleSkin > PDarktoBlackSkin and 
              PPaleSkin >= 0.5 and 
              (PIntermediateSkin > PVeryPaleSkin or PDarkSkin > PVeryPaleSkin or PDarktoBlackSkin > PVeryPaleSkin)):
            return "Pale"
        elif (PIntermediateSkin > PVeryPaleSkin and PIntermediateSkin > PPaleSkin and 
              PIntermediateSkin > PDarkSkin and PIntermediateSkin > PDarktoBlackSkin and 
              PIntermediateSkin >= 0.9 and 
              PDarktoBlackSkin > PVeryPaleSkin and PDarktoBlackSkin > PPaleSkin and PDarktoBlackSkin > PDarkSkin):
            return "Dark"
        elif (PIntermediateSkin > PVeryPaleSkin and PIntermediateSkin > PPaleSkin and 
              PIntermediateSkin > PDarkSkin and PIntermediateSkin > PDarktoBlackSkin and 
              PIntermediateSkin >= 0.9 and 
              (PDarktoBlackSkin < PVeryPaleSkin or PDarktoBlackSkin < PPaleSkin or PDarktoBlackSkin < PDarkSkin)):
            return "Intermediate"
        elif (PIntermediateSkin > PVeryPaleSkin and PIntermediateSkin > PPaleSkin and 
              PIntermediateSkin > PDarkSkin and PIntermediateSkin > PDarktoBlackSkin and 
              PIntermediateSkin >= 0.7 and 
              (PVeryPaleSkin >= 0.15 or PPaleSkin >= 0.15) and 
              (PDarkSkin < 0.15 and PDarktoBlackSkin < 0.15)):
            return "Pale"
        elif (PIntermediateSkin > PVeryPaleSkin and PIntermediateSkin > PPaleSkin and 
              PIntermediateSkin > PDarkSkin and PIntermediateSkin > PDarktoBlackSkin and 
              PIntermediateSkin >= 0.7 and 
              (PVeryPaleSkin < 0.15 and PPaleSkin < 0.15) and 
              (PDarkSkin >= 0.15 or PDarktoBlackSkin >= 0.15)):
            return "Dark"
        elif (PIntermediateSkin > PVeryPaleSkin and PIntermediateSkin > PPaleSkin and 
              PIntermediateSkin > PDarkSkin and PIntermediateSkin > PDarktoBlackSkin and 
              PIntermediateSkin >= 0.7 and 
              (PVeryPaleSkin < 0.15 and PPaleSkin < 0.15 and PDarkSkin < 0.15 and PDarktoBlackSkin < 0.15)):
            return "Intermediate"
        elif (PIntermediateSkin > PVeryPaleSkin and PIntermediateSkin > PPaleSkin and 
              PIntermediateSkin > PDarkSkin and PIntermediateSkin > PDarktoBlackSkin and 
              PIntermediateSkin >= 0.5 and 
              (PDarktoBlackSkin > PVeryPaleSkin and PDarktoBlackSkin > PPaleSkin or 
               PDarkSkin > PVeryPaleSkin and PDarkSkin > PPaleSkin)):
            return "Dark"
        elif (PIntermediateSkin > PVeryPaleSkin and PIntermediateSkin > PPaleSkin and 
              PIntermediateSkin > PDarkSkin and PIntermediateSkin > PDarktoBlackSkin and 
              PIntermediateSkin >= 0.5 and 
              (PDarktoBlackSkin < PVeryPaleSkin or PDarktoBlackSkin < PPaleSkin or 
               PDarkSkin < PVeryPaleSkin or PDarkSkin < PPaleSkin)):
            return "Intermediate"
        elif (PDarkSkin > PVeryPaleSkin and PDarkSkin > PPaleSkin and 
              PDarkSkin > PIntermediateSkin and PDarkSkin > PDarktoBlackSkin and 
              PDarkSkin >= 0.9):
            return "Dark"
        elif (PDarkSkin > PVeryPaleSkin and PDarkSkin > PPaleSkin and 
              PDarkSkin > PIntermediateSkin and PDarkSkin > PDarktoBlackSkin and 
              PDarkSkin >= 0.7 and 
              PDarktoBlackSkin > PVeryPaleSkin and PDarktoBlackSkin > PPaleSkin and PDarktoBlackSkin > PIntermediateSkin):
            return "Dark to black"
        elif (PDarkSkin > PVeryPaleSkin and PDarkSkin > PPaleSkin and 
              PDarkSkin > PIntermediateSkin and PDarkSkin > PDarktoBlackSkin and 
              PDarkSkin >= 0.5 and 
              PDarktoBlackSkin > PVeryPaleSkin and PDarktoBlackSkin > PPaleSkin and PDarktoBlackSkin > PIntermediateSkin):
            return "Dark to black"
        elif (PDarkSkin > PVeryPaleSkin and PDarkSkin > PPaleSkin and 
              PDarkSkin > PIntermediateSkin and PDarkSkin > PDarktoBlackSkin and 
              PDarkSkin >= 0.5 and 
              PVeryPaleSkin > PPaleSkin and PVeryPaleSkin > PIntermediateSkin and PVeryPaleSkin > PDarktoBlackSkin):
            return "Intermediate"
        elif (PDarkSkin > PVeryPaleSkin and PDarkSkin > PPaleSkin and 
              PDarkSkin > PIntermediateSkin and PDarkSkin > PDarktoBlackSkin and 
              PDarkSkin >= 0.5 and 
              PPaleSkin > PVeryPaleSkin and PPaleSkin > PIntermediateSkin and PPaleSkin > PDarktoBlackSkin):
            return "Dark"
        elif (PDarkSkin > PVeryPaleSkin and PDarkSkin > PPaleSkin and 
              PDarkSkin > PIntermediateSkin and PDarkSkin > PDarktoBlackSkin and 
              PDarkSkin >= 0.5 and 
              PIntermediateSkin > PVeryPaleSkin and PIntermediateSkin > PPaleSkin and PIntermediateSkin > PDarktoBlackSkin):
            return "Dark"
        elif (PDarktoBlackSkin > PVeryPaleSkin and PDarktoBlackSkin > PPaleSkin and 
              PDarktoBlackSkin > PIntermediateSkin and PDarktoBlackSkin > PDarkSkin and 
              PDarktoBlackSkin >= 0.9):
            return "Dark to black"
        elif (PDarktoBlackSkin > PVeryPaleSkin and PDarktoBlackSkin > PPaleSkin and 
              PDarktoBlackSkin > PIntermediateSkin and PDarktoBlackSkin > PDarkSkin and 
              PDarktoBlackSkin >= 0.7):
            return "Dark to black"
        elif (PDarktoBlackSkin > PVeryPaleSkin and PDarktoBlackSkin > PPaleSkin and 
              PDarktoBlackSkin > PIntermediateSkin and PDarktoBlackSkin > PDarkSkin and 
              PDarktoBlackSkin >= 0.5 and 
              PVeryPaleSkin > PPaleSkin and PVeryPaleSkin > PIntermediateSkin and PVeryPaleSkin > PDarkSkin):
            return "Intermediate"
        elif (PDarktoBlackSkin > PVeryPaleSkin and PDarktoBlackSkin > PPaleSkin and 
              PDarktoBlackSkin > PIntermediateSkin and PDarktoBlackSkin > PDarkSkin and 
              PDarktoBlackSkin >= 0.5 and 
              PPaleSkin > PVeryPaleSkin and PPaleSkin > PIntermediateSkin and PPaleSkin > PDarkSkin):
            return "Intermediate"
        elif (PDarktoBlackSkin > PVeryPaleSkin and PDarktoBlackSkin > PPaleSkin and 
              PDarktoBlackSkin > PIntermediateSkin and PDarktoBlackSkin > PDarkSkin and 
              PDarktoBlackSkin >= 0.5 and 
              PIntermediateSkin > PVeryPaleSkin and PIntermediateSkin > PPaleSkin and PIntermediateSkin > PDarkSkin):
            return "Dark"
        elif (PDarktoBlackSkin > PVeryPaleSkin and PDarktoBlackSkin > PPaleSkin and 
              PDarktoBlackSkin > PIntermediateSkin and PDarktoBlackSkin > PDarkSkin and 
              PDarktoBlackSkin >= 0.5 and 
              PDarkSkin > PVeryPaleSkin and PDarkSkin > PPaleSkin and PDarkSkin > PIntermediateSkin):
            return "Dark to black"
        else:
            return "Not predicted"
    
    df_prediction['predicted_skin_colour'] = df_prediction.apply(predict_skin_colour, axis=1)
    df_prediction.to_csv(f"{sample_id}_phenotypicPrediction.csv", sep=';')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Predict phenotypes')
    parser.add_argument('sample_id', help='Sample ID')
    parser.add_argument('sample_csv', help='Sample CSV file path')
    
    args = parser.parse_args()
    phenotypic_prediction([args.sample_id, args.sample_csv])