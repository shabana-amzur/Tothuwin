'use client';

import { useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

interface ImageValidationPageProps {
  token: string | null;
}

export default function ImageValidationPage({ token }: ImageValidationPageProps) {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<'invoice' | 'receipt' | 'id_card'>('invoice');
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<string | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
      if (validTypes.includes(file.type)) {
        setSelectedImage(file);
        // Create preview
        const reader = new FileReader();
        reader.onloadend = () => {
          setImagePreview(reader.result as string);
        };
        reader.readAsDataURL(file);
      } else {
        alert('Please select an image file (JPG, PNG, WEBP)');
      }
    }
  };

  const validateImage = async () => {
    if (!token || !selectedImage) return;

    setIsValidating(true);
    setValidationResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedImage);
      formData.append('document_type', documentType);

      const response = await fetch('http://localhost:8001/api/image-validation/validate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to validate image');
      }

      const result = await response.json();
      
      // Format the validation result
      let resultMessage = `## 📋 Image Validation Results\n\n`;
      resultMessage += `**Document Type:** ${documentType}\n`;
      resultMessage += `**Overall Status:** ${result.overall_status === 'VALID' ? '✅ VALID' : '❌ INVALID'}\n`;
      resultMessage += `**Confidence Score:** ${(result.confidence_score * 100).toFixed(1)}%\n\n`;
      
      resultMessage += `### Extracted Data:\n\`\`\`json\n${JSON.stringify(result.extracted_data, null, 2)}\n\`\`\`\n\n`;
      
      resultMessage += `### Validation Results:\n\n`;
      result.validation_results.forEach((vr: any) => {
        const icon = vr.status === 'PASS' ? '✅' : '❌';
        resultMessage += `${icon} **${vr.field}** (${vr.rule_type}): ${vr.status}`;
        if (vr.reason) {
          resultMessage += `\n   - _${vr.reason}_`;
        }
        resultMessage += '\n\n';
      });

      setValidationResult(resultMessage);
    } catch (error) {
      console.error('Image validation error:', error);
      const errorMessage = `## ❌ Validation Error\n\n${error instanceof Error ? error.message : 'An error occurred during validation'}`;
      setValidationResult(errorMessage);
    } finally {
      setIsValidating(false);
    }
  };

  const clearImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setValidationResult(null);
    if (imageInputRef.current) {
      imageInputRef.current.value = '';
    }
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold text-white mb-2">🖼️ Image Validation</h2>
        <p className="text-gray-400 mb-8">Upload an invoice, receipt, or ID card to extract and validate data</p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Upload & Info (Sticky) */}
          <div className="lg:col-span-1 space-y-6 self-start lg:sticky lg:top-6">
            {/* Upload Section */}
            <div className="bg-[#181818] rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">📤 Upload Document</h3>
              
              {/* Document Type Selector */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-300 mb-2">Document Type</label>
                <select
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value as any)}
                  className="w-full px-4 py-2 bg-[#0f0f0f] text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ec6438]"
                >
                  <option value="invoice">Invoice</option>
                  <option value="receipt">Receipt</option>
                  <option value="id_card">ID Card</option>
                </select>
              </div>

              {/* File Input */}
              <div className="mb-4">
                <input
                  ref={imageInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="image-upload"
                />
                <label
                  htmlFor="image-upload"
                  className="flex items-center justify-center w-full px-4 py-3 bg-[#ec6438] hover:bg-[#d65430] rounded-lg cursor-pointer transition-colors"
                >
                  <span className="text-white font-medium">
                    {selectedImage ? '✓ Change Image' : '📁 Select Image'}
                  </span>
                </label>
              </div>

              {/* Image Preview */}
              {imagePreview && (
                <div className="mb-4">
                  <img 
                    src={imagePreview} 
                    alt="Preview" 
                    className="w-full h-48 object-contain bg-[#0f0f0f] rounded-lg"
                  />
                  <p className="text-sm text-gray-400 mt-2">{selectedImage?.name}</p>
                </div>
              )}

              {/* Validate Button */}
              <button
                onClick={validateImage}
                disabled={!selectedImage || isValidating}
                className="w-full bg-[#ec6438] hover:bg-[#d65430] disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors"
              >
                {isValidating ? '⏳ Validating...' : '🔍 Validate Document'}
              </button>

              {/* Clear Button */}
              {selectedImage && (
                <button
                  onClick={clearImage}
                  className="w-full mt-2 bg-[#0f0f0f] hover:bg-[#252525] text-white font-semibold py-2 px-6 rounded-lg transition-colors"
                >
                  🗑️ Clear
                </button>
              )}
            </div>

            {/* Validation Rules */}
            <div className="bg-[#181818] rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-3">✅ Validation Rules</h3>
              <div className="text-sm text-gray-300 space-y-3">
                <div>
                  <p className="font-medium" style={{ color: '#ec6438' }}>Invoice:</p>
                  <ul className="list-disc list-inside ml-2 text-xs space-y-1 mt-1">
                    <li>Invoice number required</li>
                    <li>Valid date format</li>
                    <li>Total amount in range</li>
                    <li>Currency specified</li>
                    <li>Vendor name required</li>
                  </ul>
                </div>
                <div>
                  <p className="font-medium" style={{ color: '#ec6438' }}>Receipt:</p>
                  <ul className="list-disc list-inside ml-2 text-xs space-y-1 mt-1">
                    <li>Receipt number or order ID</li>
                    <li>Date validation</li>
                    <li>Total amount present</li>
                    <li>Merchant name required</li>
                  </ul>
                </div>
                <div>
                  <p className="font-medium" style={{ color: '#ec6438' }}>ID Card:</p>
                  <ul className="list-disc list-inside ml-2 text-xs space-y-1 mt-1">
                    <li>ID number required</li>
                    <li>Full name present</li>
                    <li>Date of birth format</li>
                    <li>Expiry date validation</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2">
            {validationResult ? (
              <div className="bg-[#181818] rounded-lg p-6">
                <div className="prose prose-invert max-w-none validation-results">
                  <ReactMarkdown>{validationResult}</ReactMarkdown>
                </div>
              </div>
            ) : (
              <div className="bg-[#181818] rounded-lg p-12 text-center">
                <div className="text-6xl mb-4">🖼️</div>
                <h3 className="text-xl font-semibold text-white mb-2">No Results Yet</h3>
                <p className="text-gray-400">Upload a document and click "Validate Document" to see results here</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <style jsx global>{`
        .validation-results h2 {
          color: #fff;
          font-size: 1.5rem;
          font-weight: 700;
          margin-bottom: 1rem;
        }
        .validation-results h3 {
          color: #ec6438;
          font-size: 1.25rem;
          font-weight: 600;
          margin-top: 1.5rem;
          margin-bottom: 0.75rem;
        }
        .validation-results p {
          color: #d1d5db;
          margin-bottom: 0.5rem;
        }
        .validation-results strong {
          color: #fff;
          font-weight: 600;
        }
        .validation-results code {
          background-color: #1f2937;
          padding: 0.125rem 0.375rem;
          border-radius: 0.25rem;
          font-size: 0.875rem;
        }
        .validation-results pre {
          background-color: #1f2937;
          padding: 1rem;
          border-radius: 0.5rem;
          overflow-x: auto;
          margin: 0.5rem 0;
        }
        .validation-results pre code {
          background-color: transparent;
          padding: 0;
        }
        .validation-results ul {
          list-style-type: none;
          padding-left: 0;
        }
        .validation-results li {
          margin-bottom: 0.5rem;
        }
      `}</style>
    </div>
  );
}
