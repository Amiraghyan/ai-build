
import { useCallback, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Upload, FileText, X } from 'lucide-react';

interface FileUploadZoneProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
}

export const FileUploadZone = ({ onFileSelect, selectedFile }: FileUploadZoneProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'application/pdf') {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  const handleRemoveFile = useCallback(() => {
    onFileSelect(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [onFileSelect]);

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  if (selectedFile) {
    return (
      <Card className="p-6 bg-green-50 border-green-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileText className="h-8 w-8 text-green-600" />
            <div>
              <p className="font-medium text-green-800">{selectedFile.name}</p>
              <p className="text-sm text-green-600">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              PDF Sélectionné
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRemoveFile}
              className="text-green-600 hover:text-green-800"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className="border-2 border-dashed border-blue-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer bg-blue-50/50"
    >
      <Upload className="h-12 w-12 text-blue-400 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-700 mb-2">
        Glissez-déposez votre PDF ici
      </h3>
      <p className="text-gray-500 mb-4">
        ou cliquez pour sélectionner un fichier
      </p>
      
      <Button 
        variant="outline" 
        className="cursor-pointer"
        onClick={handleButtonClick}
      >
        <Upload className="mr-2 h-4 w-4" />
        Choisir un fichier
      </Button>
      
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileInput}
        className="hidden"
      />
      
      <p className="text-xs text-gray-400 mt-4">
        Formats acceptés: PDF • Taille max: 50MB
      </p>
    </div>
  );
};
