import { FORM_VALIDATION } from './constants.js';

export const validateEmail = (email) => {
  if (!email) return 'Email is required';
  if (!FORM_VALIDATION.email.test(email)) return 'Please enter a valid email address';
  return null;
};

export const validatePhone = (phone) => {
  if (!phone) return 'Phone number is required';
  const cleanPhone = phone.replace(/\s/g, '');
  if (!FORM_VALIDATION.phone.test(cleanPhone)) return 'Please enter a valid Australian phone number';
  return null;
};

export const validateName = (name) => {
  if (!name) return 'Name is required';
  if (name.length < 2) return 'Name must be at least 2 characters';
  if (name.length > 50) return 'Name must be less than 50 characters';
  if (!/^[a-zA-Z\s'-]+$/.test(name)) return 'Name can only contain letters, spaces, hyphens and apostrophes';
  return null;
};

export const validateMessage = (message) => {
  if (!message) return 'Message is required';
  if (message.length < 10) return 'Message must be at least 10 characters';
  if (message.length > 1000) return 'Message must be less than 1000 characters';
  return null;
};

export const validateSuburb = (suburb) => {
  if (!suburb) return 'Suburb is required';
  if (suburb.length < 2) return 'Suburb must be at least 2 characters';
  if (suburb.length > 50) return 'Suburb must be less than 50 characters';
  return null;
};

export const validateNDISNumber = (ndisNumber) => {
  if (!ndisNumber) return 'NDIS number is required';
  if (!FORM_VALIDATION.ndisNumber.test(ndisNumber)) return 'NDIS number must be 9 digits';
  return null;
};

export const validateABN = (abn) => {
  if (!abn) return 'ABN is required';
  if (!FORM_VALIDATION.abn.test(abn)) return 'ABN must be 11 digits';
  return null;
};

export const validatePostcode = (postcode) => {
  if (!postcode) return 'Postcode is required';
  if (!/^\d{4}$/.test(postcode)) return 'Postcode must be 4 digits';
  const code = parseInt(postcode);
  if (code < 1000 || code > 9999) return 'Please enter a valid Australian postcode';
  return null;
};

export const validateAddress = (address) => {
  if (!address) return 'Address is required';
  if (address.length < 5) return 'Address must be at least 5 characters';
  if (address.length > 100) return 'Address must be less than 100 characters';
  return null;
};

export const validateRooms = (rooms) => {
  const totalRooms = Object.values(rooms).reduce((sum, count) => sum + count, 0);
  if (totalRooms === 0) return 'Please select at least one room';
  if (totalRooms > 20) return 'Maximum 20 rooms allowed';
  return null;
};

export const validateCleaningType = (cleaningType) => {
  if (!cleaningType) return 'Please select a cleaning type';
  return null;
};

export const validateUrgency = (urgency) => {
  if (!urgency) return 'Please select urgency level';
  return null;
};

export const validateFile = (file, maxSize, allowedTypes) => {
  if (!file) return 'File is required';
  
  if (!allowedTypes.includes(file.type)) {
    return `File type not allowed. Please upload: ${allowedTypes.join(', ')}`;
  }
  
  if (file.size > maxSize) {
    const maxSizeMB = Math.round(maxSize / (1024 * 1024));
    return `File size too large. Maximum size: ${maxSizeMB}MB`;
  }
  
  return null;
};

export const validateFiles = (files, maxFiles, maxSize, allowedTypes) => {
  if (!files || files.length === 0) return null;
  
  if (files.length > maxFiles) {
    return `Too many files. Maximum ${maxFiles} files allowed`;
  }
  
  for (let i = 0; i < files.length; i++) {
    const fileError = validateFile(files[i], maxSize, allowedTypes);
    if (fileError) return fileError;
  }
  
  return null;
};

export const validateQuoteForm = (formData) => {
  const errors = {};
  
  const nameError = validateName(formData.name);
  if (nameError) errors.name = nameError;
  
  const emailError = validateEmail(formData.email);
  if (emailError) errors.email = emailError;
  
  const phoneError = validatePhone(formData.phone);
  if (phoneError) errors.phone = phoneError;
  
  const suburbError = validateSuburb(formData.suburb);
  if (suburbError) errors.suburb = suburbError;
  
  const cleaningTypeError = validateCleaningType(formData.cleaningType);
  if (cleaningTypeError) errors.cleaningType = cleaningTypeError;
  
  const roomsError = validateRooms(formData.rooms);
  if (roomsError) errors.rooms = roomsError;
  
  const urgencyError = validateUrgency(formData.urgency);
  if (urgencyError) errors.urgency = urgencyError;
  
  if (formData.ndisNumber) {
    const ndisError = validateNDISNumber(formData.ndisNumber);
    if (ndisError) errors.ndisNumber = ndisError;
  }
  
  return Object.keys(errors).length > 0 ? errors : null;
};

export const validateContactForm = (formData) => {
  const errors = {};
  
  const nameError = validateName(formData.name);
  if (nameError) errors.name = nameError;
  
  const emailError = validateEmail(formData.email);
  if (emailError) errors.email = emailError;
  
  const phoneError = validatePhone(formData.phone);
  if (phoneError) errors.phone = phoneError;
  
  const messageError = validateMessage(formData.message);
  if (messageError) errors.message = messageError;
  
  return Object.keys(errors).length > 0 ? errors : null;
};

export const validateNDISForm = (formData) => {
  const errors = {};
  
  const nameError = validateName(formData.participantName);
  if (nameError) errors.participantName = nameError;
  
  const emailError = validateEmail(formData.email);
  if (emailError) errors.email = emailError;
  
  const phoneError = validatePhone(formData.phone);
  if (phoneError) errors.phone = phoneError;
  
  const ndisError = validateNDISNumber(formData.ndisNumber);
  if (ndisError) errors.ndisNumber = ndisError;
  
  const addressError = validateAddress(formData.address);
  if (addressError) errors.address = addressError;
  
  return Object.keys(errors).length > 0 ? errors : null;
};

export const sanitizeFormData = (formData) => {
  const sanitized = {};
  
  Object.keys(formData).forEach(key => {
    const value = formData[key];
    if (typeof value === 'string') {
      sanitized[key] = value.trim().replace(/[<>]/g, '');
    } else {
      sanitized[key] = value;
    }
  });
  
  return sanitized;
};

export const isFormValid = (errors) => {
  return !errors || Object.keys(errors).length === 0;
};
