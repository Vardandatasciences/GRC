const ExcelJS = require('exceljs');
const PDFDocument = require('pdfkit');
const docx = require('docx');
const { uploadFile } = require('./s3Service');
const ExportedFile = require('../models/ExportedFile');
const fs = require('fs');
const path = require('path');
const os = require('os');

class ExportService {
  constructor() {
    this.supportedFormats = {
      'xlsx': this.exportToExcel,
      'pdf': this.exportToPDF,
      'docx': this.exportToWord,
      'csv': this.exportToCSV,
      'json': this.exportToJSON,
      'xml': this.exportToXML,
      'txt': this.exportToText
    };
  }

  /**
   * Export data to specified format
   * @param {Object} data - The data to export
   * @param {string} format - The desired output format
   * @param {string} userId - The user requesting the export
   * @param {Object} options - Additional export options
   * @returns {Promise<Object>} Export result with file URL
   */
  async exportData(data, format, userId, options = {}) {
    let exportRecord = null;
    try {
      // Validate format
      if (!this.supportedFormats[format]) {
        throw new Error(`Unsupported export format: ${format}`);
      }

      // Generate unique filename
      const timestamp = new Date().getTime();
      const fileName = `export_${userId}_${timestamp}.${format}`;

      // Create export record
      exportRecord = await ExportedFile.createExport({
        exportData: data,
        fileType: format,
        userId: userId,
        s3Url: '', // Will be updated after upload
        fileName: fileName,
        recordCount: Array.isArray(data) ? data.length : 1,
        filters: options.filters || {},
        columns: options.columns || []
      });

      // Update status to processing
      await exportRecord.updateStatus('processing');

      // Export to file
      console.log(`Converting data to ${format} format...`);
      const fileBuffer = await this.supportedFormats[format](data, options);
      console.log(`Data converted successfully. File size: ${fileBuffer.length} bytes`);

      // Upload to S3
      console.log(`Uploading file to S3: ${fileName}`);
      const uploadResult = await uploadFile(
        { buffer: fileBuffer },
        format,
        fileName,
        userId
      );
      console.log(`File uploaded successfully to S3: ${uploadResult.file.url}`);

      // Update export record with S3 URL and metadata
      exportRecord.s3Url = uploadResult.file.url;
      await exportRecord.updateMetadata({
        fileSize: fileBuffer.length,
        exportDuration: Date.now() - timestamp,
        s3Metadata: {
          bucket: uploadResult.file.bucket,
          key: uploadResult.file.key,
          region: uploadResult.file.region,
          uploadTime: new Date().toISOString()
        }
      });
      await exportRecord.updateStatus('completed');

      return {
        success: true,
        exportId: exportRecord._id,
        fileUrl: uploadResult.file.url,
        fileName: fileName,
        metadata: {
          fileSize: fileBuffer.length,
          format: format,
          recordCount: Array.isArray(data) ? data.length : 1,
          exportDuration: Date.now() - timestamp
        }
      };

    } catch (error) {
      console.error('Export error:', error);
      if (exportRecord) {
        await exportRecord.updateStatus('failed', error.message);
        await exportRecord.updateMetadata({
          error: {
            message: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString()
          }
        });
      }
      throw error;
    }
  }

  /**
   * Export data to Excel format
   * @private
   */
  async exportToExcel(data, options = {}) {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Export');

    // Add headers
    const headers = options.columns || Object.keys(data[0] || {});
    worksheet.addRow(headers);

    // Add data
    if (Array.isArray(data)) {
      data.forEach(item => {
        worksheet.addRow(headers.map(header => item[header]));
      });
    }

    // Style headers
    worksheet.getRow(1).font = { bold: true };

    // Auto-fit columns
    worksheet.columns.forEach(column => {
      column.width = 15;
    });

    return workbook.xlsx.writeBuffer();
  }

  /**
   * Export data to PDF format
   * @private
   */
  async exportToPDF(data, options = {}) {
    return new Promise((resolve, reject) => {
      const chunks = [];
      const doc = new PDFDocument();

      doc.on('data', chunk => chunks.push(chunk));
      doc.on('end', () => resolve(Buffer.concat(chunks)));
      doc.on('error', reject);

      // Add title
      doc.fontSize(16).text('Export Report', { align: 'center' });
      doc.moveDown();

      // Add data
      if (Array.isArray(data)) {
        data.forEach(item => {
          Object.entries(item).forEach(([key, value]) => {
            doc.fontSize(12).text(`${key}: ${value}`);
          });
          doc.moveDown();
        });
      } else {
        Object.entries(data).forEach(([key, value]) => {
          doc.fontSize(12).text(`${key}: ${value}`);
        });
      }

      doc.end();
    });
  }

  /**
   * Export data to Word format
   * @private
   */
  async exportToWord(data, options = {}) {
    const { Document, Paragraph, TextRun } = docx;
    const doc = new Document();

    const paragraphs = [];

    // Add title
    paragraphs.push(
      new Paragraph({
        children: [
          new TextRun({
            text: 'Export Report',
            bold: true,
            size: 32
          })
        ],
        spacing: { after: 200 }
      })
    );

    // Add data
    if (Array.isArray(data)) {
      data.forEach(item => {
        Object.entries(item).forEach(([key, value]) => {
          paragraphs.push(
            new Paragraph({
              children: [
                new TextRun({
                  text: `${key}: ${value}`,
                  size: 24
                })
              ],
              spacing: { after: 100 }
            })
          );
        });
      });
    } else {
      Object.entries(data).forEach(([key, value]) => {
        paragraphs.push(
          new Paragraph({
            children: [
              new TextRun({
                text: `${key}: ${value}`,
                size: 24
              })
            ],
            spacing: { after: 100 }
          })
        );
      });
    }

    doc.addSection({ children: paragraphs });

    return doc.save();
  }

  /**
   * Export data to CSV format
   * @private
   */
  async exportToCSV(data, options = {}) {
    if (!Array.isArray(data)) {
      data = [data];
    }

    const headers = options.columns || Object.keys(data[0] || {});
    const rows = [
      headers.join(','),
      ...data.map(item => 
        headers.map(header => 
          JSON.stringify(item[header] || '')
        ).join(',')
      )
    ];

    return Buffer.from(rows.join('\n'));
  }

  /**
   * Export data to JSON format
   * @private
   */
  async exportToJSON(data) {
    return Buffer.from(JSON.stringify(data, null, 2));
  }

  /**
   * Export data to XML format
   * @private
   */
  async exportToXML(data) {
    const convertToXML = (obj, rootName = 'root') => {
      let xml = `<?xml version="1.0" encoding="UTF-8"?>\n<${rootName}>\n`;
      
      const addToXML = (item, parentName) => {
        if (Array.isArray(item)) {
          item.forEach((element, index) => {
            xml += `<${parentName}>\n`;
            Object.entries(element).forEach(([key, value]) => {
              if (typeof value === 'object' && value !== null) {
                addToXML(value, key);
              } else {
                xml += `  <${key}>${value}</${key}>\n`;
              }
            });
            xml += `</${parentName}>\n`;
          });
        } else if (typeof item === 'object' && item !== null) {
          Object.entries(item).forEach(([key, value]) => {
            if (typeof value === 'object' && value !== null) {
              addToXML(value, key);
            } else {
              xml += `  <${key}>${value}</${key}>\n`;
            }
          });
        }
      };

      addToXML(data, rootName);
      xml += `</${rootName}>`;
      return xml;
    };

    return Buffer.from(convertToXML(data));
  }

  /**
   * Export data to Text format
   * @private
   */
  async exportToText(data, options = {}) {
    const formatValue = (value) => {
      if (value === null || value === undefined) return '';
      if (typeof value === 'object') return JSON.stringify(value, null, 2);
      return String(value);
    };

    const formatItem = (item, level = 0) => {
      const indent = '  '.repeat(level);
      let text = '';

      if (Array.isArray(item)) {
        item.forEach((element, index) => {
          text += `${indent}Item ${index + 1}:\n`;
          text += formatItem(element, level + 1);
        });
      } else if (typeof item === 'object' && item !== null) {
        Object.entries(item).forEach(([key, value]) => {
          if (typeof value === 'object' && value !== null) {
            text += `${indent}${key}:\n`;
            text += formatItem(value, level + 1);
          } else {
            text += `${indent}${key}: ${formatValue(value)}\n`;
          }
        });
      } else {
        text += `${indent}${formatValue(item)}\n`;
      }

      return text;
    };

    // Add title
    let text = 'Export Report\n';
    text += '='.repeat(50) + '\n\n';

    // Add timestamp
    text += `Generated: ${new Date().toISOString()}\n\n`;

    // Add data
    text += formatItem(data);

    // Add footer
    text += '\n' + '='.repeat(50) + '\n';
    text += 'End of Report';

    return Buffer.from(text);
  }
}

module.exports = new ExportService(); 