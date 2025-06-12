
"use client";

import { useState, ChangeEvent, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { BlazeLogo } from '@/components/icons/BlazeLogo';
import { UploadCloud, FileText, Loader2, DownloadCloud, AlertTriangle, XCircle, Phone, Mail, Linkedin } from 'lucide-react';
import { Separator } from '@/components/ui/separator';

// IMPORTANT: Replace this with your actual Python API base URL
// You can set this in a .env.local file as NEXT_PUBLIC_PYTHON_API_URL=http://your-api-url
const API_BASE_URL = process.env.NEXT_PUBLIC_PYTHON_API_URL || 'http://localhost:8000';

export default function Home() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [excelReady, setExcelReady] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isProcessing && progress < 90) { 
      timer = setTimeout(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 500);
    } else if (isProcessing && progress === 90 && !excelReady) {
        setStatusMessage("Processing almost complete. Preparing download link...");
        setTimeout(() => {
            setExcelReady(true);
            setProgress(95); 
            setStatusMessage("Excel report is ready for download.");
        }, 1000);
    }
    return () => clearTimeout(timer);
  }, [isProcessing, progress, excelReady]);

  useEffect(() => {
    if (typeof window !== 'undefined' && typeof document !== 'undefined') {
      let styleSheet = document.styleSheets[0];
      if (!styleSheet) {
        const styleEl = document.createElement('style');
        document.head.appendChild(styleEl);
        styleSheet = styleEl.sheet;
      }

      if (styleSheet) {
        let hasSpinSlowKeyframes = false;
        let hasSpinSlowClass = false;
        try {
          for (let i = 0; i < styleSheet.cssRules.length; i++) {
            const rule = styleSheet.cssRules[i];
            if (rule instanceof CSSKeyframesRule && rule.name === 'spin-slow') {
              hasSpinSlowKeyframes = true;
            }
            if (rule instanceof CSSStyleRule && rule.selectorText === '.animate-spin-slow') {
              hasSpinSlowClass = true;
            }
          }
        } catch (e) {
          console.warn("Could not access CSS rules.", e);
        }

        if (!hasSpinSlowKeyframes) {
          const keyframes =`
            @keyframes spin-slow {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }`;
          try {
            styleSheet.insertRule(keyframes, styleSheet.cssRules.length);
          } catch (e) {
             console.warn("Could not insert keyframes rule.", e);
          }
        }
        
        if (!hasSpinSlowClass) {
          const spinSlowClass = `.animate-spin-slow { animation: spin-slow 2s linear infinite; }`;
          try {
            styleSheet.insertRule(spinSlowClass, styleSheet.cssRules.length);
          } catch (e) {
            console.warn("Could not insert class rule.", e);
          }
        }
      }
    }
  }, []);


  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const files = Array.from(event.target.files);
      const pdfFiles = files.filter(file => file.type === "application/pdf");
      if (pdfFiles.length !== files.length) {
        toast({
          title: "Invalid File Type",
          description: "Only PDF files are accepted. Non-PDF files were ignored.",
          variant: "destructive",
        });
      }
      setSelectedFiles(prevFiles => [...prevFiles, ...pdfFiles]);
      if(fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const removeFile = (fileName: string) => {
    setSelectedFiles(files => files.filter(file => file.name !== fileName));
  };

  const handleProcessInvoices = async () => {
    if (selectedFiles.length === 0) {
      toast({
        title: "No Files Selected",
        description: "Please upload one or more PDF files to process.",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setExcelReady(false);
    setErrorMessage(null);
    setStatusMessage("Uploading files...");

    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      setProgress(10); 
      const response = await fetch(`${API_BASE_URL}/process-batch`, {
        method: 'POST',
        body: formData,
      });
      setProgress(20);
      setStatusMessage("Upload complete. Server is processing invoices...");

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown server error" }));
        throw new Error(errorData.detail || `Server error: ${response.statusText}`);
      }
      // const result = await response.json(); // Not using result for now
    } catch (error) {
      console.error("Processing error:", error);
      const message = error instanceof Error ? error.message : "An unknown error occurred during processing.";
      setErrorMessage(message);
      toast({
        title: "Processing Failed",
        description: message,
        variant: "destructive",
      });
      setIsProcessing(false);
      setProgress(0);
      setStatusMessage(null);
    }
  };

  const handleDownloadExcel = async () => {
    if (!excelReady) {
         toast({
            title: "File Not Ready",
            description: "The Excel file is not yet available for download.",
            variant: "destructive",
        });
        return;
    }
    setStatusMessage("Downloading Excel file...");
    setProgress(98);

    try {
      const response = await fetch(`${API_BASE_URL}/download-excel`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Excel file not found or error generating it." }));
        throw new Error(errorData.detail || `Failed to download: ${response.statusText}`);
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'invoices_report.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setProgress(100);
      setStatusMessage("Download complete!");
      toast({
        title: "Download Successful",
        description: "Excel report downloaded.",
      });
      setTimeout(() => {
        setIsProcessing(false);
        setSelectedFiles([]);
        setProgress(0);
        setStatusMessage(null);
        setExcelReady(false);
      }, 2000);

    } catch (error) {
      console.error("Download error:", error);
       const message = error instanceof Error ? error.message : "An unknown error occurred during download.";
      setErrorMessage(message);
      toast({
        title: "Download Failed",
        description: message,
        variant: "destructive",
      });
      setIsProcessing(false);
      setProgress(0);
      setExcelReady(false);
      setStatusMessage(null);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };
  
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground p-4 font-body selection:bg-accent selection:text-accent-foreground">
      <header className="mb-8 flex flex-col items-center text-center">
        <BlazeLogo />
        <h1 className="text-5xl md:text-6xl font-headline font-bold text-primary mt-4">
          InvoiceBlaze
        </h1>
        <p className="text-muted-foreground text-lg md:text-xl mt-2 font-medium">
          Ignite Your Invoice Processing
        </p>
      </header>

      <Card className="w-full max-w-2xl p-6 md:p-8 animate-fadeIn">
        <CardHeader className="p-0 mb-6">
          <CardTitle className="text-3xl font-headline text-center text-primary">Upload Your Invoices</CardTitle>
          <CardDescription className="text-center text-muted-foreground mt-1">
            Select multiple PDF files to extract data and generate an Excel report.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0 space-y-6">
          <div className="space-y-4">
            <input
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileChange}
              ref={fileInputRef}
              className="hidden"
              disabled={isProcessing}
            />
            <Button 
              onClick={triggerFileInput} 
              variant="outline" 
              className="w-full text-lg py-6 border-primary hover:bg-primary/10 hover:text-primary transition-colors duration-150 ease-in-out"
              disabled={isProcessing}
            >
              <UploadCloud className="mr-3 h-6 w-6 text-primary" />
              Select PDF Files
            </Button>

            {selectedFiles.length > 0 && (
              <div className="space-y-2 max-h-48 overflow-y-auto p-3 rounded-md border border-input bg-card">
                <h3 className="text-sm font-medium text-muted-foreground">Selected Files ({selectedFiles.length}):</h3>
                <ul className="space-y-1">
                  {selectedFiles.map(file => (
                    <li key={file.name} className="flex items-center justify-between text-xs p-2 rounded bg-muted/30 hover:bg-muted/50 transition-colors">
                      <div className="flex items-center truncate">
                        <FileText className="h-4 w-4 mr-2 shrink-0 text-primary" />
                        <span className="truncate" title={file.name}>{file.name}</span>
                      </div>
                      <Button variant="ghost" size="icon" onClick={() => removeFile(file.name)} disabled={isProcessing} className="h-6 w-6 ml-2 shrink-0 text-destructive/70 hover:text-destructive hover:bg-destructive/10">
                        <XCircle className="h-4 w-4" />
                      </Button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {selectedFiles.length > 0 && !isProcessing && (
            <Button onClick={handleProcessInvoices} className="w-full text-lg py-6 bg-primary hover:bg-primary/90 text-primary-foreground transition-colors duration-150 ease-in-out" disabled={isProcessing}>
              <Loader2 className="mr-3 h-6 w-6 animate-spin-slow" /> 
              Process Invoices
            </Button>
          )}
          
          {isProcessing && (
             <div className="space-y-3 text-center">
                <Progress value={progress} className="w-full h-3 [&>div]:bg-accent" />
                {statusMessage && <p className="text-sm text-accent animate-pulse">{statusMessage}</p>}
             </div>
          )}

          {excelReady && isProcessing && (
             <Button onClick={handleDownloadExcel} className="w-full text-lg py-6 bg-accent hover:bg-accent/90 text-accent-foreground transition-colors duration-150 ease-in-out" disabled={progress < 95}>
                <DownloadCloud className="mr-3 h-6 w-6" />
                Download Excel Report
             </Button>
          )}
          
          {errorMessage && (
            <div className="flex items-center p-3 rounded-md bg-destructive/20 text-destructive border border-destructive">
              <AlertTriangle className="h-5 w-5 mr-2 shrink-0" />
              <p className="text-sm">{errorMessage}</p>
            </div>
          )}
        </CardContent>
      </Card>
      <footer className="mt-12 text-center w-full max-w-2xl">
        <Separator className="my-6" />
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-4 text-primary">Contact Me</h3>
          <div className="space-y-3 text-foreground">
            <p className="flex items-center justify-center">
              <Phone className="mr-2 h-5 w-5 text-primary" />
              <span>8169875922</span>
            </p>
            <p className="flex items-center justify-center">
              <Mail className="mr-2 h-5 w-5 text-primary" />
              <a href="mailto:karnguptaprivate123@gamil.com" className="hover:text-accent hover:underline">
                karnguptaprivate123@gamil.com
              </a>
            </p>
            <Button asChild variant="outline" className="hover:bg-accent hover:text-accent-foreground border-primary text-primary hover:border-accent transition-colors duration-150 ease-in-out group">
              <a href="https://www.linkedin.com/in/karngupta2/" target="_blank" rel="noopener noreferrer">
                <Linkedin className="mr-2 h-5 w-5 text-primary group-hover:text-accent-foreground transition-colors duration-150 ease-in-out" /> LinkedIn
              </a>
            </Button>
          </div>
        </div>
        <Separator className="my-6" />
        <p className="text-xs text-muted-foreground">
          &copy; {new Date().getFullYear()} InvoiceBlaze. All rights reserved.
          <br />
          Ensure your <a href={API_BASE_URL} target="_blank" rel="noopener noreferrer" className="underline hover:text-accent">Python API</a> is running at: {API_BASE_URL}
        </p>
      </footer>
    </div>
  );
}
