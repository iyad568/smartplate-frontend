// Simple frontend file storage using localStorage
class FileStorage {
  constructor() {
    this.storageKey = 'smartplate_uploaded_files';
  }

  // Save file information to localStorage
  saveFile(serviceType, file) {
    const storedFiles = this.getStoredFiles();
    
    // Create a file reader to convert file to base64
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const fileData = {
          serviceType,
          fileName: file.name,
          fileType: file.type,
          fileSize: file.size,
          base64Data: e.target.result,
          uploadedAt: new Date().toISOString()
        };
        
        storedFiles[serviceType] = fileData;
        localStorage.setItem(this.storageKey, JSON.stringify(storedFiles));
        resolve(fileData);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  // Get all stored files
  getStoredFiles() {
    const stored = localStorage.getItem(this.storageKey);
    return stored ? JSON.parse(stored) : {};
  }

  // Get file for specific service
  getFile(serviceType) {
    const files = this.getStoredFiles();
    return files[serviceType] || null;
  }

  // Get file URL for display
  getFileUrl(serviceType) {
    const file = this.getFile(serviceType);
    return file ? file.base64Data : null;
  }

  // Delete file for specific service
  deleteFile(serviceType) {
    const storedFiles = this.getStoredFiles();
    delete storedFiles[serviceType];
    localStorage.setItem(this.storageKey, JSON.stringify(storedFiles));
  }

  // Clear all files
  clearAllFiles() {
    localStorage.removeItem(this.storageKey);
  }
}

export const fileStorage = new FileStorage();
