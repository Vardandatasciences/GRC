const mongoose = require('mongoose');

const ExportedFileSchema = new mongoose.Schema({
  // The data that was exported (could be query parameters, filters, etc.)
  exportData: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  
  // The type of file exported (e.g., 'pdf', 'xlsx', 'csv')
  fileType: {
    type: String,
    required: true,
    enum: ['pdf', 'xlsx', 'csv', 'json', 'xml']
  },
  
  // The user who requested the export
  userId: {
    type: String,
    required: true
  },
  
  // The S3 URL where the exported file is stored
  s3Url: {
    type: String,
    required: true
  },
  
  // The name of the file in S3
  fileName: {
    type: String,
    required: true
  },
  
  // Status of the export process
  status: {
    type: String,
    enum: ['pending', 'processing', 'completed', 'failed'],
    default: 'pending'
  },
  
  // Error message if the export failed
  error: {
    type: String,
    default: null
  },
  
  // Metadata about the export
  metadata: {
    recordCount: {
      type: Number,
      default: 0
    },
    fileSize: {
      type: Number,
      default: 0
    },
    exportDuration: {
      type: Number,
      default: 0
    },
    filters: {
      type: mongoose.Schema.Types.Mixed,
      default: {}
    },
    columns: [{
      type: String
    }]
  },
  
  // Timestamps
  createdAt: {
    type: Date,
    default: Date.now
  },
  
  completedAt: {
    type: Date,
    default: null
  }
}, {
  timestamps: true
});

// Indexes for better query performance
ExportedFileSchema.index({ userId: 1, createdAt: -1 });
ExportedFileSchema.index({ status: 1 });
ExportedFileSchema.index({ fileType: 1 });
ExportedFileSchema.index({ 'metadata.recordCount': 1 });

// Static method to create a new export request
ExportedFileSchema.statics.createExport = async function(data) {
  const exportRequest = new this({
    exportData: data.exportData,
    fileType: data.fileType,
    userId: data.userId,
    s3Url: data.s3Url,
    fileName: data.fileName,
    metadata: {
      recordCount: data.recordCount || 0,
      filters: data.filters || {},
      columns: data.columns || []
    }
  });

  return exportRequest.save();
};

// Instance method to update export status
ExportedFileSchema.methods.updateStatus = async function(status, error = null) {
  this.status = status;
  if (error) {
    this.error = error;
  }
  if (status === 'completed') {
    this.completedAt = new Date();
  }
  return this.save();
};

// Instance method to update metadata
ExportedFileSchema.methods.updateMetadata = async function(metadata) {
  this.metadata = {
    ...this.metadata,
    ...metadata
  };
  return this.save();
};

module.exports = mongoose.model('ExportedFile', ExportedFileSchema); 