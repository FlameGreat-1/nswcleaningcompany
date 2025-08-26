import { useState, useCallback } from 'react';
import { FILE_UPLOAD } from '../utils/constants.js';
import { validateFiles, isValidFileType, isValidFileSize } from '../utils/validation.js';

const useImageUpload = (maxFiles = FILE_UPLOAD.maxFiles) => {
  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [errors, setErrors] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});

  const createPreview = useCallback((file) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve({
        id: Date.now() + Math.random(),
        file,
        preview: e.target.result,
        name: file.name,
        size: file.size,
        type: file.type
      });
      reader.readAsDataURL(file);
    });
  }, []);

  const addFiles = useCallback(async (newFiles) => {
    const fileArray = Array.from(newFiles);
    const validationError = validateFiles(fileArray, maxFiles, FILE_UPLOAD.maxSize, FILE_UPLOAD.allowedTypes);
    
    if (validationError) {
      setErrors(prev => [...prev, validationError]);
      return false;
    }

    if (files.length + fileArray.length > maxFiles) {
      setErrors(prev => [...prev, `Maximum ${maxFiles} files allowed`]);
      return false;
    }

    setErrors([]);
    
    const newPreviews = await Promise.all(
      fileArray.map(file => createPreview(file))
    );

    setFiles(prev => [...prev, ...fileArray]);
    setPreviews(prev => [...prev, ...newPreviews]);
    return true;
  }, [files.length, maxFiles, createPreview]);

  const removeFile = useCallback((index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setPreviews(prev => prev.filter((_, i) => i !== index));
    setErrors([]);
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
    setPreviews([]);
    setErrors([]);
    setUploadProgress({});
  }, []);

  const uploadFiles = useCallback(async (uploadUrl, additionalData = {}) => {
    if (files.length === 0) return { success: false, error: 'No files to upload' };

    setUploading(true);
    setErrors([]);

    try {
      const formData = new FormData();
      
      files.forEach((file, index) => {
        formData.append(`files`, file);
      });

      Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
      });

      const response = await fetch(uploadUrl, {
        method: 'POST',
        body: formData,
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(prev => ({ ...prev, overall: progress }));
        }
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      setUploading(false);
      
      return { success: true, data: result };
    } catch (error) {
      setUploading(false);
      setErrors(prev => [...prev, error.message]);
      return { success: false, error: error.message };
    }
  }, [files]);

  const validateFile = useCallback((file) => {
    const typeValid = isValidFileType(file, FILE_UPLOAD.allowedTypes);
    const sizeValid = isValidFileSize(file, FILE_UPLOAD.maxSize);
    
    return {
      valid: typeValid && sizeValid,
      errors: [
        !typeValid && 'Invalid file type',
        !sizeValid && 'File too large'
      ].filter(Boolean)
    };
  }, []);

  const getFileInfo = useCallback(() => {
    return {
      count: files.length,
      totalSize: files.reduce((sum, file) => sum + file.size, 0),
      types: [...new Set(files.map(file => file.type))]
    };
  }, [files]);

  return {
    files,
    previews,
    uploading,
    errors,
    uploadProgress,
    addFiles,
    removeFile,
    clearFiles,
    uploadFiles,
    validateFile,
    getFileInfo,
    hasFiles: files.length > 0,
    canAddMore: files.length < maxFiles
  };
};

export default useImageUpload;
