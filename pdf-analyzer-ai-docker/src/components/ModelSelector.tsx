
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Brain, Zap, Award, Clock } from 'lucide-react';

interface ModelSelectorProps {
  selectedModel: string;
  onModelSelect: (model: string) => void;
}

const models = [
  {
    id: 'llama-3.1-8b',
    name: 'Llama 3.1 8B',
    description: 'Modèle équilibré, idéal pour l\'analyse générale de documents',
    icon: Brain,
    performance: 'Rapide',
    accuracy: 'Élevée',
    specialty: 'Polyvalent',
    color: 'blue'
  },
  {
    id: 'mistral-7b',
    name: 'Mistral 7B',
    description: 'Optimisé pour l\'extraction d\'informations structurées',
    icon: Zap,
    performance: 'Très rapide',
    accuracy: 'Très élevée',
    specialty: 'Extraction',
    color: 'purple'
  },
  {
    id: 'phi-3-mini',
    name: 'Phi-3 Mini',
    description: 'Compact mais puissant, parfait pour les documents courts',
    icon: Clock,
    performance: 'Ultra rapide',
    accuracy: 'Élevée',
    specialty: 'Documents courts',
    color: 'green'
  },
  {
    id: 'code-llama-13b',
    name: 'CodeLlama 13B',
    description: 'Spécialisé dans l\'analyse de documents techniques et code',
    icon: Award,
    performance: 'Modéré',
    accuracy: 'Très élevée',
    specialty: 'Technique',
    color: 'orange'
  }
];

export const ModelSelector = ({ selectedModel, onModelSelect }: ModelSelectorProps) => {
  return (
    <div className="space-y-3">
      {models.map((model) => {
        const Icon = model.icon;
        const isSelected = selectedModel === model.id;
        
        return (
          <Card 
            key={model.id} 
            className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
              isSelected 
                ? 'ring-2 ring-blue-500 bg-blue-50 border-blue-200' 
                : 'hover:border-gray-300'
            }`}
            onClick={() => onModelSelect(model.id)}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className={`p-2 rounded-lg bg-${model.color}-100`}>
                    <Icon className={`h-5 w-5 text-${model.color}-600`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-medium text-gray-900">{model.name}</h4>
                      {isSelected && (
                        <Badge variant="default" className="bg-blue-600">
                          Sélectionné
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{model.description}</p>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="outline" className="text-xs">
                        ⚡ {model.performance}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        🎯 {model.accuracy}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        🔧 {model.specialty}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
      
      {!selectedModel && (
        <div className="text-center py-4 text-gray-500">
          <Brain className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">Sélectionnez un modèle pour continuer</p>
        </div>
      )}
    </div>
  );
};
