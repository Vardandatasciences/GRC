require("dotenv").config();
const express = require('express');
const multer = require('multer');
const fs = require("fs");
const S3 = require("aws-sdk/clients/s3");
const mysql = require('mysql2/promise');
const bodyParser = require('body-parser');

// Configure AWS S3
const bucketName = process.env.AWS_BUCKET_NAME || 'grc-files-vardaan';
const region = process.env.AWS_REGION || 'us-east-1';
const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;

const s3 = new S3({
  region,
  accessKeyId,
  secretAccessKey,
});

// Configure MySQL
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || 'root',
  database: process.env.DB_NAME || 'grc',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

const pool = mysql.createPool(dbConfig);

// Test DB connection
async function testConnection() {
  try {
    const connection = await pool.getConnection();
    console.log('MySQL connected successfully');
    connection.release();
  } catch (error) {
    console.error('MySQL connection failed:', error);
  }
}

testConnection();

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

// Check if file type should be downloadable
function isDownloadable(extension) {
  const downloadableTypes = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'zip', 'rar', '7z', 'txt', 'csv', 'json', 'xml'
  ];
  return downloadableTypes.includes(extension.toLowerCase());
}

// Express app setup
const app = express();
const PORT = process.env.PORT || 3000;

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB limit
  }
});

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Helper function to generate file name with parameters
function generateFileName(baseFileName, params) {
  const timestamp = Date.now();
  let paramString = '';
  
  if (params && Object.keys(params).length > 0) {
    paramString = '_' + Object.entries(params)
      .map(([key, value]) => `${key}-${value}`)
      .join('_');
  }
  
  return `${timestamp}_${baseFileName}${paramString}`;
}

// Upload file
async function uploadFile(file, fileType, fileName, userId, params = {}) {
  const connection = await pool.getConnection();
  
  try {
    // Get content type based on file extension
    const extension = fileType.toLowerCase();
    const contentType = CONTENT_TYPES[extension] || 'application/octet-stream';

    // Generate unique file name with parameters
    const uniqueFileName = generateFileName(fileName, params);

    // Prepare upload parameters
    const uploadParams = {
      Bucket: bucketName,
      Body: file.buffer || fs.createReadStream(file.path),
      Key: uniqueFileName,
      ContentType: contentType,
      ...(isDownloadable(extension) && {
        ContentDisposition: `attachment; filename="${fileName}"`
      })
    };

    // Upload to S3
    const uploadResult = await s3.upload(uploadParams).promise();
    
    // Check if metadata column exists in the database
    try {
      // Try to insert with metadata first
      const metadataJson = JSON.stringify(params);
      const [result] = await connection.execute(
        'INSERT INTO s3_files (url, file_type, file_name, user_id, metadata) VALUES (?, ?, ?, ?, ?)',
        [uploadResult.Location, extension, fileName, userId, metadataJson]
      );
      
      // Get the inserted record
      const [rows] = await connection.execute(
        'SELECT * FROM s3_files WHERE id = ?',
        [result.insertId]
      );

      const insertedFile = rows[0];
      
      // Check if this is an audit report upload (based on metadata)
      if (params.documentType === 'audit_report' && params.auditId) {
        try {
          console.log(`Starting audit report save process for audit ID: ${params.auditId}`);
          
          // First, fetch policy details from the audit table - note the column case sensitivity!
          // In MySQL, column names in queries are typically case-insensitive, but let's match exactly
          // what's in your audit table schema
          const [auditRows] = await connection.execute(
            'SELECT AuditId, PolicyId, SubPolicyId, FrameworkId FROM audit WHERE AuditId = ?',
            [params.auditId]
          );
          
          // Debug the results more clearly
          console.log('Audit query results:', JSON.stringify(auditRows));
          
          if (auditRows && auditRows.length > 0) {
            const auditInfo = auditRows[0];
            console.log('Found audit details:', JSON.stringify(auditInfo));
            
            // Log the exact values we're using
            console.log('Using values for audit_report:', {
              AuditId: params.auditId,
              Report: uploadResult.Location,
              PolicyId: auditInfo.PolicyId,
              SubPolicyId: auditInfo.SubPolicyId,
              FrameworkId: auditInfo.FrameworkId
            });
            
            // Update the audit_report table with the report URL and details from audit table
            const insertResult = await connection.execute(
              'INSERT INTO audit_report (AuditId, Report, PolicyId, SubPolicyId, FrameworkId) VALUES (?, ?, ?, ?, ?) ' +
              'ON DUPLICATE KEY UPDATE Report = ?',
              [
                params.auditId, 
                uploadResult.Location, 
                auditInfo.PolicyId || null, 
                auditInfo.SubPolicyId || null, 
                auditInfo.FrameworkId || null,
                uploadResult.Location
              ]
            );
            
            console.log(`Saved report URL to audit_report table. Insert result:`, JSON.stringify(insertResult));
          } else {
            console.error(`No audit details found for ID: ${params.auditId}`);
            
            // Fallback: try to insert with just AuditId and Report
            console.log('Attempting fallback insert with only AuditId and Report');
            const fallbackResult = await connection.execute(
              'INSERT INTO audit_report (AuditId, Report) VALUES (?, ?) ' +
              'ON DUPLICATE KEY UPDATE Report = ?',
              [params.auditId, uploadResult.Location, uploadResult.Location]
            );
            
            console.log('Fallback insert result:', JSON.stringify(fallbackResult));
          }
        } catch (reportErr) {
          console.error(`Error saving to audit_report table:`, reportErr);
          console.error(`Error details: ${reportErr.message}`);
          console.error(`Error SQL state: ${reportErr.sqlState}, code: ${reportErr.code}`);
          
          // Continue with the upload response even if this fails
        }
      }
      
      return {
        success: true,
        file: {
          id: insertedFile.id,
          url: insertedFile.url,
          fileType: insertedFile.file_type,
          fileName: insertedFile.file_name,
          uploadedAt: insertedFile.uploaded_at,
          metadata: params,
          s3Key: uniqueFileName
        }
      };
    } 
    catch (dbError) {
      // If metadata column doesn't exist, insert without it
      if (dbError.code === 'ER_BAD_FIELD_ERROR' && dbError.message.includes('metadata')) {
        console.log('Metadata column not found, inserting without metadata');
        
        // Insert without metadata
        const [result] = await connection.execute(
          'INSERT INTO s3_files (url, file_type, file_name, user_id) VALUES (?, ?, ?, ?)',
          [uploadResult.Location, extension, fileName, userId]
        );
        
        // Get the inserted record
        const [rows] = await connection.execute(
          'SELECT * FROM s3_files WHERE id = ?',
          [result.insertId]
        );
  
        const insertedFile = rows[0];
        
        // Check if this is an audit report upload (based on params)
        if (params.documentType === 'audit_report' && params.auditId) {
          try {
            console.log(`Starting audit report save process for audit ID: ${params.auditId}`);
            
            // First, fetch policy details from the audit table - note the column case sensitivity!
            // In MySQL, column names in queries are typically case-insensitive, but let's match exactly
            // what's in your audit table schema
            const [auditRows] = await connection.execute(
              'SELECT AuditId, PolicyId, SubPolicyId, FrameworkId FROM audit WHERE AuditId = ?',
              [params.auditId]
            );
            
            // Debug the results more clearly
            console.log('Audit query results:', JSON.stringify(auditRows));
            
            if (auditRows && auditRows.length > 0) {
              const auditInfo = auditRows[0];
              console.log('Found audit details:', JSON.stringify(auditInfo));
              
              // Log the exact values we're using
              console.log('Using values for audit_report:', {
                AuditId: params.auditId,
                Report: uploadResult.Location,
                PolicyId: auditInfo.PolicyId,
                SubPolicyId: auditInfo.SubPolicyId,
                FrameworkId: auditInfo.FrameworkId
              });
              
              // Update the audit_report table with the report URL and details from audit table
              const insertResult = await connection.execute(
                'INSERT INTO audit_report (AuditId, Report, PolicyId, SubPolicyId, FrameworkId) VALUES (?, ?, ?, ?, ?) ' +
                'ON DUPLICATE KEY UPDATE Report = ?',
                [
                  params.auditId, 
                  uploadResult.Location, 
                  auditInfo.PolicyId || null, 
                  auditInfo.SubPolicyId || null, 
                  auditInfo.FrameworkId || null,
                  uploadResult.Location
                ]
              );
              
              console.log(`Saved report URL to audit_report table. Insert result:`, JSON.stringify(insertResult));
            } else {
              console.error(`No audit details found for ID: ${params.auditId}`);
              
              // Fallback: try to insert with just AuditId and Report
              console.log('Attempting fallback insert with only AuditId and Report');
              const fallbackResult = await connection.execute(
                'INSERT INTO audit_report (AuditId, Report) VALUES (?, ?) ' +
                'ON DUPLICATE KEY UPDATE Report = ?',
                [params.auditId, uploadResult.Location, uploadResult.Location]
              );
              
              console.log('Fallback insert result:', JSON.stringify(fallbackResult));
            }
          } catch (reportErr) {
            console.error(`Error saving to audit_report table:`, reportErr);
            console.error(`Error details: ${reportErr.message}`);
            console.error(`Error SQL state: ${reportErr.sqlState}, code: ${reportErr.code}`);
            
            // Continue with the upload response even if this fails
          }
        }
        
        return {
          success: true,
          file: {
            id: insertedFile.id,
            url: insertedFile.url,
            fileType: insertedFile.file_type,
            fileName: insertedFile.file_name,
            uploadedAt: insertedFile.uploaded_at,
            metadata: params,  // Still return the metadata in the response
            s3Key: uniqueFileName
          }
        };
      } else if (dbError.code === 'ER_NO_SUCH_TABLE' && dbError.message.includes('s3_files')) {
        // If s3_files table doesn't exist but we're uploading an audit report
        if (params.documentType === 'audit_report' && params.auditId) {
          try {
            console.log(`Starting audit report save process for audit ID: ${params.auditId}`);
            
            // First, fetch policy details from the audit table - note the column case sensitivity!
            // In MySQL, column names in queries are typically case-insensitive, but let's match exactly
            // what's in your audit table schema
            const [auditRows] = await connection.execute(
              'SELECT AuditId, PolicyId, SubPolicyId, FrameworkId FROM audit WHERE AuditId = ?',
              [params.auditId]
            );
            
            // Debug the results more clearly
            console.log('Audit query results:', JSON.stringify(auditRows));
            
            if (auditRows && auditRows.length > 0) {
              const auditInfo = auditRows[0];
              console.log('Found audit details:', JSON.stringify(auditInfo));
              
              // Log the exact values we're using
              console.log('Using values for audit_report:', {
                AuditId: params.auditId,
                Report: uploadResult.Location,
                PolicyId: auditInfo.PolicyId,
                SubPolicyId: auditInfo.SubPolicyId,
                FrameworkId: auditInfo.FrameworkId
              });
              
              // Save directly to audit_report table without trying to use s3_files
              await connection.execute(
                'INSERT INTO audit_report (AuditId, Report, PolicyId, SubPolicyId, FrameworkId) VALUES (?, ?, ?, ?, ?) ' +
                'ON DUPLICATE KEY UPDATE Report = ?',
                [
                  params.auditId, 
                  uploadResult.Location, 
                  auditInfo.PolicyId || null, 
                  auditInfo.SubPolicyId || null, 
                  auditInfo.FrameworkId || null,
                  uploadResult.Location
                ]
              );
              console.log(`Saved report URL to audit_report table for audit ${params.auditId}`);
              
              return {
                success: true,
                file: {
                  url: uploadResult.Location,
                  fileType: extension,
                  fileName: fileName,
                  uploadedAt: new Date().toISOString(),
                  metadata: params,
                  s3Key: uniqueFileName
                }
              };
            } else {
              console.error(`No audit details found for ID: ${params.auditId}`);
            }
          } catch (reportErr) {
            console.error(`Error saving to audit_report table:`, reportErr);
            console.error(`Error details: ${reportErr.message}`);
            console.error(`Error SQL state: ${reportErr.sqlState}, code: ${reportErr.code}`);
            // If both tables fail, rethrow the original error
          }
        }
        // If it's a different error, rethrow it
        throw dbError;
      } else {
        // If it's a different error, rethrow it
        throw dbError;
      }
    }
  } catch (error) {
    console.error('Error uploading file:', error);
    throw new Error(`Failed to upload file: ${error.message}`);
  } finally {
    connection.release();
  }
}

// Delete file
async function deleteFile(fileId) {
  const connection = await pool.getConnection();
  
  try {
    // Get file metadata from MySQL
    const [rows] = await connection.execute(
      'SELECT * FROM s3_files WHERE id = ?',
      [fileId]
    );

    if (rows.length === 0) {
      throw new Error('File not found');
    }

    const file = rows[0];

    // Extract S3 key from URL
    const s3Key = file.url.split('/').pop();

    // Delete from S3
    const deleteParams = {
      Bucket: bucketName,
      Key: s3Key
    };
    await s3.deleteObject(deleteParams).promise();

    // Delete from MySQL
    await connection.execute(
      'DELETE FROM s3_files WHERE id = ?',
      [fileId]
    );

    return {
      success: true,
      message: 'File deleted successfully'
    };
  } catch (error) {
    console.error('Error deleting file:', error);
    throw new Error(`Failed to delete file: ${error.message}`);
  } finally {
    connection.release();
  }
}

// Get file metadata
async function getFileMetadata(fileId) {
  const connection = await pool.getConnection();
  
  try {
    const [rows] = await connection.execute(
      'SELECT * FROM s3_files WHERE id = ?',
      [fileId]
    );

    if (rows.length === 0) {
      throw new Error('File not found');
    }

    const file = rows[0];
    const metadata = file.metadata ? JSON.parse(file.metadata) : {};

    return {
      success: true,
      file: {
        id: file.id,
        url: file.url,
        fileType: file.file_type,
        fileName: file.file_name,
        uploadedAt: file.uploaded_at,
        metadata: metadata
      }
    };
  } catch (error) {
    console.error('Error getting file metadata:', error);
    throw new Error(`Failed to get file metadata: ${error.message}`);
  } finally {
    connection.release();
  }
}

// Get user files
async function getUserFiles(userId, filters = {}) {
  const connection = await pool.getConnection();
  
  try {
    // Check if the metadata column exists by querying the table structure
    const [columns] = await connection.execute(
      "SHOW COLUMNS FROM s3_files LIKE 'metadata'"
    );
    
    const hasMetadataColumn = columns.length > 0;
    
    let query = 'SELECT * FROM s3_files WHERE user_id = ?';
    const queryParams = [userId];
    
    // Add filter by metadata only if the column exists
    if (hasMetadataColumn && filters && Object.keys(filters).length > 0) {
      query += ' AND metadata LIKE ?';
      queryParams.push(`%${JSON.stringify(filters).slice(1, -1)}%`);
    }
    
    query += ' ORDER BY uploaded_at DESC';
    
    const [rows] = await connection.execute(query, queryParams);

    return {
      success: true,
      files: rows.map(file => ({
        id: file.id,
        url: file.url,
        fileType: file.file_type,
        fileName: file.file_name,
        uploadedAt: file.uploaded_at,
        metadata: hasMetadataColumn && file.metadata ? JSON.parse(file.metadata) : {}
      }))
    };
  } catch (error) {
    console.error('Error getting user files:', error);
    throw new Error(`Failed to get user files: ${error.message}`);
  } finally {
    connection.release();
  }
}

// Generate download URL - fix the URL encoding issue
async function getDownloadUrl(fileId, expiresIn = 3600) {
  const connection = await pool.getConnection();
  
  try {
    const [rows] = await connection.execute(
      'SELECT * FROM s3_files WHERE id = ?',
      [fileId]
    );

    if (rows.length === 0) {
      throw new Error('File not found');
    }

    const file = rows[0];
    
    // Extract S3 key from URL and fully decode it to avoid double-encoding
    const urlParts = file.url.split('/');
    const encodedKey = urlParts[urlParts.length - 1];
    
    // Make sure to properly decode the key
    let s3Key;
    try {
      // First try to decode it in case it's encoded
      s3Key = decodeURIComponent(encodedKey);
    } catch (e) {
      // If decoding fails, use the original key
      s3Key = encodedKey;
      console.log('Key could not be decoded, using as is');
    }
    
    console.log('Original S3 key from URL:', encodedKey);
    console.log('Decoded S3 key for download:', s3Key);

    // Generate pre-signed URL
    const params = {
      Bucket: bucketName,
      Key: s3Key,
      Expires: expiresIn,
      ResponseContentDisposition: `attachment; filename="${file.file_name}"`
    };

    const downloadUrl = s3.getSignedUrl('getObject', params);
    console.log('Generated download URL:', downloadUrl);

    return {
      success: true,
      downloadUrl: downloadUrl,
      fileName: file.file_name,
      s3Key: s3Key
    };
  } catch (error) {
    console.error('Error generating download URL:', error);
    throw new Error(`Failed to generate download URL: ${error.message}`);
  } finally {
    connection.release();
  }
}

// API Routes
app.post('/api/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const { originalname, mimetype } = req.file;
    const userId = req.body.userId || 'default-user';
    const fileExtension = originalname.split('.').pop().toLowerCase();
    const fileName = req.body.fileName || originalname;
    
    // Extract all parameters from the request body
    const params = {};
    for (const key in req.body) {
      if (key !== 'userId' && key !== 'fileName') {
        params[key] = req.body[key];
      }
    }

    const result = await uploadFile(req.file, fileExtension, fileName, userId, params);
    res.json(result);
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/files/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    // Get filters from query parameters
    const filters = req.query;
    const result = await getUserFiles(userId, filters);
    res.json(result);
  } catch (error) {
    console.error('Get files error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/file/:fileId', async (req, res) => {
  try {
    const { fileId } = req.params;
    const result = await getFileMetadata(fileId);
    res.json(result);
  } catch (error) {
    console.error('Get file metadata error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/download/:fileId', async (req, res) => {
  try {
    const { fileId } = req.params;
    const expiresIn = req.query.expiresIn ? parseInt(req.query.expiresIn) : 3600;
    const result = await getDownloadUrl(fileId, expiresIn);
    
    if (req.query.redirect === 'true') {
      res.redirect(result.downloadUrl);
    } else {
      res.json(result);
    }
  } catch (error) {
    console.error('Download error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.delete('/api/file/:fileId', async (req, res) => {
  try {
    const { fileId } = req.params;
    const result = await deleteFile(fileId);
    res.json(result);
  } catch (error) {
    console.error('Delete error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Internal Server Error',
    message: err.message 
  });
});

app.listen(PORT, () => {
  console.log(`S3 Microservice running on port ${PORT}`);
});

module.exports = {
  uploadFile,
  deleteFile,
  getFileMetadata,
  getUserFiles,
  getDownloadUrl
};
