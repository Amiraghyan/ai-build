
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Button } from '@/components/ui/button';
import { ChevronDown, Settings } from 'lucide-react';
import { useState } from 'react';

interface AnalysisParametersProps {
  parameters: any;
  onParametersChange: (params: any) => void;
}

export const AnalysisParameters = ({ parameters, onParametersChange }: AnalysisParametersProps) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const updateParameter = (key: string, value: any) => {
    onParametersChange({
      ...parameters,
      [key]: value
    });
  };

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger asChild>
        <Button variant="ghost" className="w-full justify-between p-0 h-auto">
          <div className="flex items-center space-x-2">
            <Settings className="h-4 w-4" />
            <span className="text-sm font-medium">
              {isOpen ? 'Masquer les paramètres' : 'Afficher les paramètres avancés'}
            </span>
          </div>
          <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </Button>
      </CollapsibleTrigger>
      
      <CollapsibleContent className="space-y-4 mt-4">
        {/* Précision de l'analyse */}
        <div className="space-y-2">
          <Label htmlFor="precision">Précision de l'analyse</Label>
          <Slider
            id="precision"
            min={1}
            max={10}
            step={1}
            value={[parameters.precision || 7]}
            onValueChange={(value) => updateParameter('precision', value[0])}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>Rapide</span>
            <span>Niveau: {parameters.precision || 7}</span>
            <span>Précis</span>
          </div>
        </div>

        {/* Langue du document */}
        <div className="space-y-2">
          <Label htmlFor="language">Langue du document</Label>
          <Select 
            value={parameters.language || 'auto'} 
            onValueChange={(value) => updateParameter('language', value)}
          >
            <SelectTrigger id="language">
              <SelectValue placeholder="Détection automatique" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="auto">Détection automatique</SelectItem>
              <SelectItem value="fr">Français</SelectItem>
              <SelectItem value="en">Anglais</SelectItem>
              <SelectItem value="es">Espagnol</SelectItem>
              <SelectItem value="de">Allemand</SelectItem>
              <SelectItem value="it">Italien</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Type d'analyse */}
        <div className="space-y-2">
          <Label htmlFor="analysis-type">Type d'analyse</Label>
          <Select 
            value={parameters.analysisType || 'comprehensive'} 
            onValueChange={(value) => updateParameter('analysisType', value)}
          >
            <SelectTrigger id="analysis-type">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="comprehensive">Analyse complète</SelectItem>
              <SelectItem value="summary">Résumé uniquement</SelectItem>
              <SelectItem value="extraction">Extraction de données</SelectItem>
              <SelectItem value="classification">Classification</SelectItem>
              <SelectItem value="sentiment">Analyse de sentiment</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Options booléennes */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="extract-tables" className="text-sm font-medium">
              Extraire les tableaux
            </Label>
            <Switch
              id="extract-tables"
              checked={parameters.extractTables || false}
              onCheckedChange={(checked) => updateParameter('extractTables', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="extract-images" className="text-sm font-medium">
              Analyser les images
            </Label>
            <Switch
              id="extract-images"
              checked={parameters.extractImages || false}
              onCheckedChange={(checked) => updateParameter('extractImages', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="generate-keywords" className="text-sm font-medium">
              Générer des mots-clés
            </Label>
            <Switch
              id="generate-keywords"
              checked={parameters.generateKeywords || true}
              onCheckedChange={(checked) => updateParameter('generateKeywords', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="structured-output" className="text-sm font-medium">
              Sortie structurée (JSON)
            </Label>
            <Switch
              id="structured-output"
              checked={parameters.structuredOutput || false}
              onCheckedChange={(checked) => updateParameter('structuredOutput', checked)}
            />
          </div>
        </div>

        {/* Température du modèle */}
        <div className="space-y-2">
          <Label htmlFor="temperature">Créativité du modèle</Label>
          <Slider
            id="temperature"
            min={0}
            max={1}
            step={0.1}
            value={[parameters.temperature || 0.3]}
            onValueChange={(value) => updateParameter('temperature', value[0])}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>Conservateur</span>
            <span>{parameters.temperature || 0.3}</span>
            <span>Créatif</span>
          </div>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
};
