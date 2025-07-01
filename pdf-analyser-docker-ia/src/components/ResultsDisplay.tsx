
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { 
  FileText, 
  Download, 
  Copy, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  Eye,
  Tag
} from 'lucide-react';
import { useState } from 'react';

type SuccessPayload = {
  filename: string;
  pages: number;
  chars_sent: number;
  summary: string;
};

interface ResultsDisplayProps {
  results: SuccessPayload | null;
  isAnalyzing: boolean;
}

export const ResultsDisplay = ({ results, isAnalyzing }: ResultsDisplayProps) => {
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  const handleCopy = (text: string, section: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  if (isAnalyzing) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12">
        <div className="w-16 h-16 mb-6 relative">
          <div className="absolute inset-0 border-4 border-blue-200 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
        </div>
        <h3 className="text-lg font-medium text-gray-700 mb-2">
          Analyse en cours...
        </h3>
        <p className="text-gray-500 text-center mb-6">
          Notre IA traite votre document avec attention
        </p>
        <Progress value={75} className="w-full max-w-xs" />
        <p className="text-xs text-gray-400 mt-2">Extraction des insights...</p>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 text-center">
        <FileText className="h-16 w-16 text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-500 mb-2">
          En attente d'analyse
        </h3>
        <p className="text-gray-400 max-w-sm">
          Téléchargez un PDF et sélectionnez un modèle pour commencer l'analyse
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header avec informations du document */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="font-medium text-green-800">Analyse terminée</span>
          </div>
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            {results.pages} pages
          </Badge>
        </div>
        <div className="text-sm text-gray-600">
          <p><strong>Fichier:</strong> {results.filename}</p>
          <p><strong>Caractères traités:</strong> {results.chars_sent.toLocaleString()}</p>
        </div>
      </div>

      {/* Résumé principal */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-lg">
            <div className="flex items-center space-x-2">
              <Eye className="h-5 w-5 text-blue-600" />
              <span>Résumé du document</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleCopy(results.summary, 'summary')}
            >
              {copiedSection === 'summary' ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 leading-relaxed">{results.summary}</p>
        </CardContent>
      </Card>

      {/* Informations du document */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center space-x-2 text-lg">
            <TrendingUp className="h-5 w-5 text-purple-600" />
            <span>Détails du document</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center text-xs font-medium text-purple-600">
                1
              </div>
              <p className="text-gray-700 flex-1">Nom du fichier: {results.filename}</p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center text-xs font-medium text-purple-600">
                2
              </div>
              <p className="text-gray-700 flex-1">Nombre de pages: {results.pages}</p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center text-xs font-medium text-purple-600">
                3
              </div>
              <p className="text-gray-700 flex-1">Caractères analysés: {results.chars_sent.toLocaleString()}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Mots-clés */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center space-x-2 text-lg">
            <Tag className="h-5 w-5 text-orange-600" />
            <span>Catégories identifiées</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {['Document PDF', 'Analyse IA', 'Extraction de texte', 'Traitement automatique'].map((keyword, index) => (
              <Badge key={index} variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
                {keyword}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button className="flex-1" variant="default">
          <Download className="mr-2 h-4 w-4" />
          Télécharger le rapport
        </Button>
        <Button 
          className="flex-1" 
          variant="outline"
          onClick={() => handleCopy(results.summary, 'full')}
        >
          {copiedSection === 'full' ? (
            <CheckCircle className="mr-2 h-4 w-4 text-green-600" />
          ) : (
            <Copy className="mr-2 h-4 w-4" />
          )}
          Copier le résumé
        </Button>
      </div>

      {/* Statistiques */}
      <Card className="bg-gray-50">
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">{results.pages}</div>
              <div className="text-xs text-gray-500">Pages analysées</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">{Math.round(results.chars_sent / 1000)}k</div>
              <div className="text-xs text-gray-500">Caractères traités</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
