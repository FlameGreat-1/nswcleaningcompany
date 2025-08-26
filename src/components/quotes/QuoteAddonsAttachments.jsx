import { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import quotesService from '../../services/quotesService';

const QuoteAddonsAttachments = ({ quoteData, serviceId, onComplete, onBack }) => {
  const [addons, setAddons] = useState([]);
  const [selectedAddons, setSelectedAddons] = useState([]);
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAddons = async () => {
      try {
        const response = await quotesService.getServiceAddons(serviceId);
        setAddons(response.results || response);
      } catch (err) {
        setError('Failed to load add-ons');
        console.error(err);
      }
    };
    
    if (serviceId) {
      fetchAddons();
    }
  }, [serviceId]);

  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'application/pdf': ['.pdf']
    },
    onDrop: acceptedFiles => {
      const newAttachments = acceptedFiles.map(file => ({
        file,
        preview: URL.createObjectURL(file),
        name: file.name,
        size: file.size,
        type: file.type
      }));
      setAttachments(prev => [...prev, ...newAttachments]);
    }
  });

  const toggleAddon = (addon) => {
    setSelectedAddons(prev => {
      const exists = prev.find(item => item.id === addon.id);
      if (exists) {
        return prev.filter(item => item.id !== addon.id);
      } else {
        return [...prev, { ...addon, quantity: 1 }];
      }
    });
  };

  const updateAddonQuantity = (addonId, quantity) => {
    setSelectedAddons(prev => 
      prev.map(item => 
        item.id === addonId ? { ...item, quantity: Math.max(1, quantity) } : item
      )
    );
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    
    try {

      const createdQuote = await quotesService.createQuote(quoteData);
   
      const addonsPromises = selectedAddons.map(addon => 
        quotesService.createQuoteItem({
          quote: createdQuote.id,
          addon: addon.id,
          item_type: 'addon',
          name: addon.name,
          description: addon.description || '',
          quantity: addon.quantity,
          unit_price: addon.price,
          is_optional: true,
          is_taxable: true
        })
      );
      
      await Promise.all(addonsPromises);
      
      const attachmentPromises = attachments.map(attachment => 
        quotesService.uploadQuoteAttachment({
          quote: createdQuote.id,
          file: attachment.file,
          attachment_type: attachment.type.startsWith('image/') ? 'image' : 'document',
          title: attachment.name,
          is_public: true
        })
      );
      
      await Promise.all(attachmentPromises);
      
      onComplete(createdQuote);
    } catch (err) {
      setError('Failed to create quote: ' + (err.message || 'Unknown error'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="theme-card">
      <div className="mb-6">
        <h2 className="text-2xl font-bold app-text-primary mb-2">Add-ons & Attachments</h2>
        <p className="app-text-muted">
          Enhance your quote with add-on services and upload relevant photos or documents.
        </p>
      </div>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          <p className="font-medium">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}
      
      {/* Add-ons section */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold app-text-primary mb-4">Available Add-ons</h3>
        
        {addons.length === 0 ? (
          <p className="app-text-muted">No add-ons available for this service</p>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {addons.map(addon => (
              <div 
                key={addon.id} 
                className={`border app-border rounded-lg p-4 cursor-pointer transition-all ${
                  selectedAddons.some(item => item.id === addon.id) 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                    : 'hover:border-blue-300'
                }`}
                onClick={() => toggleAddon(addon)}
              >
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold app-text-primary">{addon.name}</h4>
                  <span className="text-sm font-medium app-text-primary">
                    ${addon.price}
                  </span>
                </div>
                
                {addon.description && (
                  <p className="text-sm app-text-muted mb-3">{addon.description}</p>
                )}
                
                {selectedAddons.some(item => item.id === addon.id) && (
                  <div className="mt-3 pt-3 border-t app-border">
                    <div className="flex items-center justify-between" onClick={e => e.stopPropagation()}>
                      <span className="text-sm font-medium app-text-primary">Quantity:</span>
                      <div className="flex items-center">
                        <button 
                          className="w-8 h-8 rounded-l-lg app-border app-bg-secondary flex items-center justify-center"
                          onClick={(e) => {
                            e.stopPropagation();
                            updateAddonQuantity(
                              addon.id, 
                              selectedAddons.find(item => item.id === addon.id).quantity - 1
                            );
                          }}
                        >
                          -
                        </button>
                        <span className="w-10 h-8 app-border-y flex items-center justify-center">
                          {selectedAddons.find(item => item.id === addon.id).quantity}
                        </span>
                        <button 
                          className="w-8 h-8 rounded-r-lg app-border app-bg-secondary flex items-center justify-center"
                          onClick={(e) => {
                            e.stopPropagation();
                            updateAddonQuantity(
                              addon.id, 
                              selectedAddons.find(item => item.id === addon.id).quantity + 1
                            );
                          }}
                        >
                          +
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Attachments section */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold app-text-primary mb-4">Upload Photos or Documents</h3>
        
        <div 
          {...getRootProps({ 
            className: "border-2 border-dashed app-border rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-all"
          })}
        >
          <input {...getInputProps()} />
          <div className="mb-3">
            <svg className="w-12 h-12 mx-auto app-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <p className="app-text-primary font-medium mb-1">Drag & drop files here, or click to select files</p>
          <p className="text-sm app-text-muted">Supported formats: JPG, PNG, PDF</p>
        </div>
        
        {attachments.length > 0 && (
          <div className="mt-6 grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {attachments.map((file, index) => (
              <div key={index} className="border app-border rounded-lg overflow-hidden">
                {file.type.startsWith('image/') ? (
                  <div className="h-40 bg-gray-100 dark:bg-gray-800 flex items-center justify-center overflow-hidden">
                    <img 
                      src={file.preview} 
                      alt={file.name} 
                      className="w-full h-full object-cover"
                      onLoad={() => URL.revokeObjectURL(file.preview)}
                    />
                  </div>
                ) : (
                  <div className="h-40 bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                    <svg className="w-16 h-16 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
                <div className="p-3">
                  <div className="flex justify-between items-start">
                    <div className="truncate pr-2">
                      <p className="font-medium app-text-primary text-sm truncate">{file.name}</p>
                      <p className="text-xs app-text-muted">
                        {(file.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <button 
                      onClick={() => setAttachments(prev => prev.filter((_, i) => i !== index))}
                      className="text-red-500 hover:text-red-700"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t app-border">
        <button
          type="button"
          onClick={onBack}
          disabled={loading}
          className="flex-1 px-6 py-2 bg-transparent border-2 app-border-blue app-text-primary rounded-lg font-medium transition-all hover:app-bg-blue hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Back to Details
        </button>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={loading}
          className="flex-1 theme-button disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Creating Quote...' : 'Create Quote'}
        </button>
      </div>
    </div>
  );
};

export default QuoteAddonsAttachments;
