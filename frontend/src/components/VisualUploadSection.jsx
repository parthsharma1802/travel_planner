import React, { useState } from "react";
import { Upload, Camera, Sparkles, CheckCircle2, ArrowRight, Layers } from "lucide-react";
import { CANONICAL_LANDMARKS } from "../data/mockData";

export default function VisualUploadSection({ onSelectLandmark }) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzedResult, setAnalyzedResult] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);

  const handleSampleSelect = (landmark) => {
    setIsAnalyzing(true);
    setPreviewImage(landmark.image_url);
    setAnalyzedResult(null);

    setTimeout(() => {
      setIsAnalyzing(false);
      setAnalyzedResult(landmark);
    }, 800);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewImage(url);
      setIsAnalyzing(true);
      setAnalyzedResult(null);

      setTimeout(() => {
        setIsAnalyzing(false);
        // Match Qutub Minar sample mock result
        setAnalyzedResult(CANONICAL_LANDMARKS[0]);
      }, 1000);
    }
  };

  return (
    <section className="bg-[#f5f5f7] py-16 border-t border-b border-[#e0e0e0]">
      <div className="max-w-5xl mx-auto px-6">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-semibold text-[#1d1d1f] tracking-tight">
            Visual Landmark Search Engine
          </h2>
          <p className="text-sm text-[#7a7a7a] mt-2">
            Upload an image or pick a test sample to extract 512-d embeddings & search FAISS vector index
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Upload Card */}
          <div className="lg:col-[#span-7] bg-white rounded-2xl p-6 border border-gray-200/80 shadow-sm">
            <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center bg-[#fafafc] hover:bg-white hover:border-[#0066cc] transition-all cursor-pointer relative">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              />
              <div className="w-12 h-12 rounded-full bg-blue-50 text-[#0066cc] flex items-center justify-center mx-auto mb-3">
                <Upload className="w-6 h-6" />
              </div>
              <p className="text-sm font-semibold text-[#1d1d1f]">
                Drag and drop your monument photo here
              </p>
              <p className="text-xs text-[#7a7a7a] mt-1">
                Supports JPG, PNG, WEBP (Targeted 224x224 RGB ImageNet normalization)
              </p>
            </div>

            {/* Test Samples Selector */}
            <div className="mt-6">
              <p className="text-xs font-semibold text-[#7a7a7a] uppercase tracking-wider mb-3">
                Or Click a Sample Test Query:
              </p>
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
                {CANONICAL_LANDMARKS.map((lm) => (
                  <button
                    key={lm.id}
                    onClick={() => handleSampleSelect(lm)}
                    className="relative group rounded-lg overflow-hidden border border-gray-200 h-16 focus:outline-none focus:ring-2 focus:ring-[#0066cc]"
                  >
                    <img src={lm.image_url} alt={lm.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                    <div className="absolute inset-0 bg-black/30 group-hover:bg-black/10 transition-colors flex items-end p-1">
                      <span className="text-[10px] font-medium text-white truncate">{lm.name}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Live Results Panel */}
          <div className="lg:col-span-5 bg-white rounded-2xl p-6 border border-gray-200/80 shadow-sm flex flex-col justify-between min-h-[360px]">
            {isAnalyzing ? (
              <div className="my-auto text-center py-12">
                <div className="w-10 h-10 border-3 border-[#0066cc] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-sm font-semibold text-[#1d1d1f]">Extracting 512-d Visual Vectors...</p>
                <p className="text-xs text-[#7a7a7a] mt-1">Searching FAISS IndexFlatIP (3,572 Vectors)</p>
              </div>
            ) : analyzedResult ? (
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-gray-100">
                  <div className="flex items-center space-x-2 text-emerald-600 text-xs font-semibold">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Match Found (Score: {analyzedResult.similarity_score})</span>
                  </div>
                  <span className="text-[10px] font-mono bg-blue-50 text-[#0066cc] px-2 py-0.5 rounded">
                    {analyzedResult.id}
                  </span>
                </div>

                <div className="mt-4 flex space-x-4">
                  <img
                    src={previewImage || analyzedResult.image_url}
                    alt={analyzedResult.name}
                    className="w-24 h-24 rounded-xl object-cover border border-gray-200"
                  />
                  <div>
                    <h3 className="text-lg font-semibold text-[#1d1d1f]">{analyzedResult.name}</h3>
                    <p className="text-xs text-[#7a7a7a]">{analyzedResult.city}, {analyzedResult.state}</p>
                    <p className="text-xs font-semibold text-[#0066cc] mt-1">{analyzedResult.category}</p>
                    <div className="mt-2 flex items-center space-x-1 text-xs">
                      <span>⭐ {analyzedResult.rating}</span>
                      <span className="text-gray-400">({analyzedResult.reviews_count.toLocaleString()} reviews)</span>
                    </div>
                  </div>
                </div>

                {/* ResNet-18 Top-3 Probabilities */}
                <div className="mt-5 bg-[#f5f5f7] p-3 rounded-xl">
                  <p className="text-[11px] font-semibold text-[#7a7a7a] uppercase tracking-wider mb-2">
                    ResNet-18 Top-3 Predicted Probabilities:
                  </p>
                  <div className="space-y-1.5">
                    {analyzedResult.top_3_classes.map((cls, idx) => (
                      <div key={cls.name} className="flex items-center justify-between text-xs">
                        <span className="text-[#1d1d1f] font-medium">{idx + 1}. {cls.name}</span>
                        <span className="font-mono text-[#0066cc] font-semibold">{cls.confidence.toFixed(2)}%</span>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  onClick={() => onSelectLandmark(analyzedResult)}
                  className="mt-5 w-full apple-btn-primary flex items-center justify-center space-x-2 py-2 text-xs"
                >
                  <span>Inspect Full Tourism Metadata</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <div className="my-auto text-center py-12 text-[#7a7a7a]">
                <Layers className="w-8 h-8 text-[#0066cc] mx-auto mb-3 opacity-60" />
                <p className="text-sm font-medium text-[#1d1d1f]">No image analyzed yet</p>
                <p className="text-xs mt-1">Upload a photo or select a test sample above to inspect similarity scores</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
