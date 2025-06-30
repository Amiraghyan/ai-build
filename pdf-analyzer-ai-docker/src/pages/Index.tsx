/* src/pages/Index.tsx
   Composant page d’accueil — version “connectée” à l’API FastAPI
*/
import { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileUploadZone } from '@/components/FileUploadZone';
import { ModelSelector } from '@/components/ModelSelector';
import { AnalysisParameters } from '@/components/AnalysisParameters';
import { ResultsDisplay } from '@/components/ResultsDisplay';
import { Brain, FileText, Zap, Clock, Award } from 'lucide-react';

/* ------------------------------------------------------------------------- */
/*                               CONFIGURATION                               */
/* ------------------------------------------------------------------------- */

/** URL de base de l’API – injectée par Vite au build via VITE_API_BASE_URL   */
const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

/* ------------------------------------------------------------------------- */
/*                                  TYPES                                    */
/* ------------------------------------------------------------------------- */

type SuccessPayload = {
  summary: string;
  keyPoints: string[];
  confidence: number;
};
type ErrorPayload = { error: string };
type AnalysisResponse = SuccessPayload | ErrorPayload;

/* ------------------------------------------------------------------------- */
/*                                COMPOSANT                                  */
/* ------------------------------------------------------------------------- */

const Index = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedModel, setSelectedModel] = useState('');
  const [parameters, setParameters] = useState<Record<string, unknown>>({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] =
    useState<AnalysisResponse | null>(null);

  /* ------------------------------ HANDLERS ------------------------------ */

  const handleStartAnalysis = async () => {
    if (!selectedFile || !selectedModel) return;

    setIsAnalyzing(true);
    setAnalysisResults(null); // réinitialise l’affichage

    try {
      const formData = new FormData();
      formData.append('pdf', selectedFile);
      formData.append('model', selectedModel);
      formData.append('params', JSON.stringify(parameters));

      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Erreur serveur : ${res.status}`);
      }

      const data: SuccessPayload = await res.json();
      setAnalysisResults(data);
    } catch (err) {
      setAnalysisResults({ error: (err as Error).message });
    } finally {
      setIsAnalyzing(false);
    }
  };

  /* ------------------------------ RENDER ------------------------------ */

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AI PDF Analyzer
              </h1>
            </div>
            <Badge
              variant="secondary"
              className="bg-green-100 text-green-800"
            >
              100% Open Source
            </Badge>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            Analysez vos PDF avec l'Intelligence Artificielle
          </h2>
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Transformez vos documents PDF en insights précieux grâce à nos
            modèles d'IA open source. Extraction intelligente, analyse
            sémantique et résultats personnalisables.
          </p>
        </div>
      </section>

      {/* Main Analysis Interface */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-8">
              {/* -------- Left Column — Configuration -------- */}
              <div className="space-y-6">
                {/* Étape 1 */}
                <Card className="border-0 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <FileText className="h-5 w-5 text-blue-600" />
                      <span>1. Télécharger votre PDF</span>
                    </CardTitle>
                    <CardDescription>
                      Sélectionnez le document PDF à analyser
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <FileUploadZone
                      onFileSelect={setSelectedFile}
                      selectedFile={selectedFile}
                    />
                  </CardContent>
                </Card>

                {/* Étape 2 */}
                <Card className="border-0 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Brain className="h-5 w-5 text-purple-600" />
                      <span>2. Choisir le modèle d'IA</span>
                    </CardTitle>
                    <CardDescription>
                      Sélectionnez le modèle optimal pour votre analyse
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ModelSelector
                      selectedModel={selectedModel}
                      onModelSelect={setSelectedModel}
                    />
                  </CardContent>
                </Card>

                {/* Étape 3 */}
                <Card className="border-0 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Zap className="h-5 w-5 text-yellow-600" />
                      <span>3. Paramètres avancés (optionnel)</span>
                    </CardTitle>
                    <CardDescription>
                      Personnalisez l'analyse selon vos besoins
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <AnalysisParameters
                      parameters={parameters}
                      onParametersChange={setParameters}
                    />
                  </CardContent>
                </Card>

                {/* Bouton lancer l’analyse */}
                <Button
                  onClick={handleStartAnalysis}
                  disabled={
                    !selectedFile || !selectedModel || isAnalyzing
                  }
                  className="w-full py-6 text-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all duration-300"
                  size="lg"
                >
                  {isAnalyzing ? (
                    <>
                      <Clock className="mr-2 h-5 w-5 animate-spin" />
                      Analyse en cours...
                    </>
                  ) : (
                    <>
                      <Brain className="mr-2 h-5 w-5" />
                      Lancer l'analyse
                    </>
                  )}
                </Button>
              </div>

              {/* -------- Right Column — Results -------- */}
              <div>
                <Card className="border-0 shadow-lg h-full">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Award className="h-5 w-5 text-green-600" />
                      <span>Résultats de l'analyse</span>
                    </CardTitle>
                    <CardDescription>
                      Les insights extraits de votre document apparaîtront ici
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="h-full">
                    {/* Message d’erreur en clair si présent */}
                    {analysisResults &&
                      'error' in analysisResults && (
                        <p className="text-red-600 mb-4">
                          Erreur&nbsp;: {analysisResults.error}
                        </p>
                      )}

                    <ResultsDisplay
                      results={
                        analysisResults &&
                        'error' in analysisResults
                          ? null
                          : (analysisResults as SuccessPayload)
                      }
                      isAnalyzing={isAnalyzing}
                    />
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 mt-20">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Brain className="h-6 w-6 text-blue-400" />
            <span className="text-xl font-bold">AI PDF Analyzer</span>
          </div>
          <p className="text-gray-400">
            Propulsé par l'intelligence artificielle open source • Sécurisé •
            Rapide • Précis
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
