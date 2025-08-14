// VERSION=3

function setup() {
    return {
        input: ["B04", "B08", "B11", "SCL", "dataMask"],
        output: [
            { id: "default", bands: 4 },                 // Image NDVI colorée
            { id: "ndvi", bands: 1, sampleType: "FLOAT32" }, // NDVI brut
            { id: "ndmi", bands: 1, sampleType: "FLOAT32" }, // NDMI brut
            { id: "dataMask", bands: 1 }
        ]
    };
}

function evaluatePixel(samples) {
    // Calculs bruts
    let ndviVal = index(samples.B08, samples.B04); // NDVI = (NIR - RED) / (NIR + RED)
    let ndmiVal = index(samples.B08, samples.B11); // NDMI = (NIR - SWIR1) / (NIR + SWIR1)

    // Masque de données valides
    const validPixel = samples.dataMask === 1 && !isCloud(samples.SCL);

    // Encodage couleur NDVI pour la visualisation
    let imgVals;
    if (!validPixel) {
        imgVals = [0, 0, 0, 0]; // Pixel transparent si nuage/ombre
    } else if (ndviVal < 0) {
        imgVals = [0.5, 0.5, 0.5, 1]; // Zones non végétalisées
    } else if (ndviVal < 0.2) {
        imgVals = [1, 0, 0, 1]; // Rouge
    } else if (ndviVal < 0.4) {
        imgVals = [1, 0.65, 0, 1]; // Orange
    } else if (ndviVal < 0.6) {
        imgVals = [0.8, 0.8, 0, 1]; // Jaune
    } else {
        imgVals = [0, 0.6, 0, 1]; // Vert
    }

    // Retourner les valeurs
    return {
        default: imgVals,
        ndvi: [validPixel ? ndviVal : NaN],
        ndmi: [validPixel ? ndmiVal : NaN],
        dataMask: [validPixel ? 1 : 0]
    };
}

// Détection nuages / ombres avec SCL
function isCloud(scl) {
    // Codes nuages / ombres dans Sentinel-2 L2A
    return (
        scl === 3 || // Ombre de nuage
        scl === 7 || // Nuage faible proba
        scl === 8 || // Nuage moyenne proba
        scl === 9 || // Nuage forte proba
        scl === 10 || // Cirrus
        scl === 11   // Neige / glace
    );
}
