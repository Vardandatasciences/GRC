/**
 * KPI Functions for Performance Analysis
 * This file contains utility functions and data transformations for KPIs
 */
import axios from 'axios';

// API base URL
const API_BASE_URL = '/api';

// Calculate completion percentage
export const calculateCompletionPercentage = (completed, planned) => {
  if (!planned || planned === 0) return 0;
  return Math.round((completed / planned) * 100);
};

// Convert percentage to gauge rotation degrees
export const calculateGaugeRotation = (percentage) => {
  // Convert percentage to rotation degrees (0% = -90deg, 100% = 90deg)
  return (percentage / 100) * 180 - 90;
};

// Determine status class based on percentage and target
export const getStatusClass = (percentage, target) => {
  if (percentage >= target) {
    return 'success';
  } else if (percentage >= target * 0.85) {
    return 'warning';
  } else {
    return 'danger';
  }
};

// Determine status text based on percentage and target
export const getStatusText = (percentage, target) => {
  if (percentage >= target) {
    return 'Target Achieved';
  } else if (percentage >= target * 0.85) {
    return 'Near Target';
  } else {
    return 'Below Target';
  }
};

// Fetch KPI data from the API
export const fetchKpiData = async (kpiType, params = {}) => {
  try {
    let endpoint = '';
    
    switch (kpiType) {
      case 'auditCompletion':
        endpoint = `${API_BASE_URL}/kpi/audit-completion/`;
        break;
      case 'auditCompletionTrend':
        endpoint = `${API_BASE_URL}/kpi/audit-completion-trend/`;
        break;
      default:
        throw new Error(`Unknown KPI type: ${kpiType}`);
    }
    
    // Add query parameters if any
    const queryParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
      queryParams.append(key, params[key]);
    });
    
    if (queryParams.toString()) {
      endpoint += `?${queryParams.toString()}`;
    }
    
    const response = await axios.get(endpoint);
    return response.data;
  } catch (error) {
    console.error(`Error fetching ${kpiType} KPI data:`, error);
    throw error;
  }
};

// Transform raw data for visualization
export const prepareKpiVisualizationData = (rawData, kpiType) => {
  let percentage;
  
  switch (kpiType) {
    case 'auditCompletion':
      // The backend now calculates this, but we'll keep the function for potential client-side processing
      percentage = rawData.completion_percentage;
      return {
        ...rawData,
        completionPercentage: percentage,
        gaugeRotation: calculateGaugeRotation(percentage),
        maxBarValue: Math.max(rawData.planned, rawData.completed)
      };
    default:
      return rawData;
  }
};

// Helper function to format date for API requests
export const formatDateForApi = (date) => {
  if (!date) return '';
  if (typeof date === 'string') return date;
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
};

// Helper function to format data for different time periods
export const formatDataByTimePeriod = (data, timePeriod) => {
  // Implementation would depend on specific requirements
  console.log(`Formatting data for period: ${timePeriod}`);
  return data;
}; 