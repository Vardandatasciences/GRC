require("dotenv").config();
const fs = require("fs");
const S3 = require("aws-sdk/clients/s3");
const S3File = require("../models/S3File");

const bucketName = process.env.AWS_BUCKET_NAME;
const region = process.env.AWS_REGION;
const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;

const s3 = new S3({
  region,
  accessKeyId,
  secretAccessKey,
});

// Content type mapping
const CONTENT_TYPES = {
  // Images
  'jpg': 'image/jpeg',
  'jpeg': 'image/jpeg',
  'png': 'image/png',
  'gif': 'image/gif',
  'webp': 'image/webp',
  
  // Documents
  'pdf': 'application/pdf',
  'doc': 'application/msword',
  'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'xls': 'application/vnd.ms-excel',
  'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'ppt': 'application/vnd.ms-powerpoint',
  'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  
  // Videos
  'mp4': 'video/mp4',
  'mov': 'video/quicktime',
  'avi': 'video/x-msvideo',
  'webm': 'video/webm',
  
  // Audio
  'mp3': 'audio/mpeg',
  'wav': 'audio/wav',
  'ogg': 'audio/ogg',
  
  // Archives
  'zip': 'application/zip',
  'rar': 'application/x-rar-compressed',
  '7z': 'application/x-7z-compressed',
  
  // Text
  'txt': 'text/plain',
  'csv': 'text/csv',
  'json': 'application/json',
  
  // Other
  'xml': 'application/xml',
  'html': 'text/html',
  'css': 'text/css',
  'js': 'application/javascript'
};

/**
 * Upload a file to S3 and store its metadata in MongoDB
 * @param {Object} file - The file object (from multer or similar)
 * @param {string} fileType - The type/extension of the file
 * @param {string} fileName - The name to give the file
 * @param {string} userId - The ID of the user uploading the file
 * @returns {Promise<Object>} The uploaded file metadata
 */
async function uploadFile(file, fileType, fileName, userId) {
  try {
    // Get content type based on file extension
    const extension = fileType.toLowerCase();
    const contentType = CONTENT_TYPES[extension] || 'application/octet-stream';

    // Prepare upload parameters
    const uploadParams = {
      Bucket: bucketName,
      Body: file.buffer || fs.createReadStream(file.path),
      Key: fileName,
      ContentType: contentType,
      // Add ContentDisposition for downloadable files
      ...(isDownloadable(extension) && {
        ContentDisposition: 'attachment'
      })
    };

    // Upload to S3
    const uploadResult = await s3.upload(uploadParams).promise();

    // Create file metadata in MongoDB
    const s3File = await S3File.create({
      url: uploadResult.Location,
      fileType: extension,
      fileName: fileName,
      userId: userId
    });

    return {
      success: true,
      file: {
        id: s3File._id,
        url: s3File.url,
        fileType: s3File.fileType,
        fileName: s3File.fileName,
        uploadedAt: s3File.uploadedAt
      }
    };
  } catch (error) {
    console.error('Error uploading file:', error);
    throw new Error(`Failed to upload file: ${error.message}`);
  }
}

/**
 * Check if file type should be downloadable
 * @param {string} extension - File extension
 * @returns {boolean} Whether the file should be downloadable
 */
function isDownloadable(extension) {
  const downloadableTypes = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'zip', 'rar', '7z', 'txt', 'csv', 'json', 'xml'
  ];
  return downloadableTypes.includes(extension.toLowerCase());
}

/**
 * Delete a file from S3 and its metadata from MongoDB
 * @param {string} fileId - The MongoDB ID of the file
 * @returns {Promise<Object>} Deletion result
 */
async function deleteFile(fileId) {
  try {
    // Get file metadata from MongoDB
    const file = await S3File.findById(fileId);
    if (!file) {
      throw new Error('File not found');
    }

    // Delete from S3
    const deleteParams = {
      Bucket: bucketName,
      Key: file.fileName
    };
    await s3.deleteObject(deleteParams).promise();

    // Delete from MongoDB
    await S3File.findByIdAndDelete(fileId);

    return {
      success: true,
      message: 'File deleted successfully'
    };
  } catch (error) {
    console.error('Error deleting file:', error);
    throw new Error(`Failed to delete file: ${error.message}`);
  }
}

/**
 * Get file metadata by ID
 * @param {string} fileId - The MongoDB ID of the file
 * @returns {Promise<Object>} File metadata
 */
async function getFileMetadata(fileId) {
  try {
    const file = await S3File.findById(fileId);
    if (!file) {
      throw new Error('File not found');
    }

    return {
      success: true,
      file: {
        id: file._id,
        url: file.url,
        fileType: file.fileType,
        fileName: file.fileName,
        uploadedAt: file.uploadedAt
      }
    };
  } catch (error) {
    console.error('Error getting file metadata:', error);
    throw new Error(`Failed to get file metadata: ${error.message}`);
  }
}

/**
 * Get all files uploaded by a user
 * @param {string} userId - The ID of the user
 * @returns {Promise<Object>} List of files
 */
async function getUserFiles(userId) {
  try {
    const files = await S3File.find({ userId }).sort({ uploadedAt: -1 });
    return {
      success: true,
      files: files.map(file => ({
        id: file._id,
        url: file.url,
        fileType: file.fileType,
        fileName: file.fileName,
        uploadedAt: file.uploadedAt
      }))
    };
  } catch (error) {
    console.error('Error getting user files:', error);
    throw new Error(`Failed to get user files: ${error.message}`);
  }
}

module.exports = {
  uploadFile,
  deleteFile,
  getFileMetadata,
  getUserFiles
}; 