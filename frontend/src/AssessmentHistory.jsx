import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar, Heart, Activity, TrendingUp, AlertCircle, CheckCircle, Download, FileText, BarChart3, Eye } from 'lucide-react';
import { recentAssessments } from './api';
import toast from 'react-hot-toast';

const AssessmentHistory = () => {
  const navigate = useNavigate();
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showDetailedReport, setShowDetailedReport] = useState(false);
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [downloadingPDF, setDownloadingPDF] = useState(new Set());

  useEffect(() => {
    fetchAllAssessments();
  }, []);

  const fetchAllAssessments = async () => {
    try {
      setLoading(true);
      console.log('Fetching all assessments...');
      
      const data = await recentAssessments.getRecent(50); // Get more assessments
      console.log('All assessments data:', data);
      setAssessments(data);
    } catch (error) {
      console.error('Error fetching assessments:', error);
      toast.error('Failed to load assessment history');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk) => {
    if (risk >= 70) return 'text-red-600';
    if (risk >= 40) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getRiskIcon = (risk) => {
    if (risk >= 70) return <AlertCircle className="w-4 h-4 text-red-600" />;
    if (risk >= 40) return <AlertCircle className="w-4 h-4 text-yellow-600" />;
    return <CheckCircle className="w-4 h-4 text-green-600" />;
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskCategoryColor = (category) => {
    if (category === 'Low Risk') return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200';
    if (category === 'Moderate Risk') return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200';
    return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200';
  };

  const handleViewDetailedReport = (assessment) => {
    setSelectedAssessment(assessment);
    setShowDetailedReport(true);
  };

  const handleDownloadPDF = async (assessment) => {
    try {
      // Add this assessment to the downloading set
      setDownloadingPDF(prev => new Set([...prev, assessment.id]));
      
      // Check if we have the required health data
      if (!assessment.input_data || Object.keys(assessment.input_data).length === 0) {
        toast.error('No health data available for this assessment');
        return;
      }
      
      // Use the assessment's input data to generate PDF
      const healthData = assessment.input_data;
      
      // Ensure we have the minimum required fields for PDF generation
      const requiredFields = ['age', 'gender', 'bmi', 'blood_pressure', 'cholesterol_level', 'glucose_level', 'physical_activity', 'smoking_status', 'alcohol_intake', 'family_history'];
      const missingFields = requiredFields.filter(field => !(field in healthData));
      
      if (missingFields.length > 0) {
        console.warn(`Missing required fields for PDF generation: ${missingFields.join(', ')}`);
        // Use default values for missing fields
        const defaultValues = {
          age: 45,
          gender: 1,
          bmi: 25,
          blood_pressure: 120,
          cholesterol_level: 200,
          glucose_level: 100,
          physical_activity: 5,
          smoking_status: 0,
          alcohol_intake: 0,
          family_history: 0
        };
        
        // Fill in missing fields with defaults
        missingFields.forEach(field => {
          healthData[field] = defaultValues[field];
        });
      }
      
      // Call the PDF download API directly
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/predict/current-pdf`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(healthData)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Create and download the PDF
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `health_report_${assessment.date}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('PDF downloaded successfully!');
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error('Failed to download PDF report');
    } finally {
      // Remove this assessment from the downloading set
      setDownloadingPDF(prev => {
        const newSet = new Set(prev);
        newSet.delete(assessment.id);
        return newSet;
      });
    }
  };

  const getHealthTrend = (currentAssessment, previousAssessment) => {
    if (!previousAssessment) return 'new';
    
    const currentScore = currentAssessment.overall_score;
    const previousScore = previousAssessment.overall_score;
    const difference = currentScore - previousScore;
    
    if (difference > 5) return 'improving';
    if (difference < -5) return 'declining';
    return 'stable';
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'improving':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'declining':
        return <TrendingUp className="w-4 h-4 text-red-600 rotate-180" />;
      case 'stable':
        return <Activity className="w-4 h-4 text-blue-600" />;
      default:
        return <Activity className="w-4 h-4 text-gray-600 dark:text-gray-300" />;
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'improving':
        return 'text-green-600 dark:text-green-400';
      case 'declining':
        return 'text-red-600 dark:text-red-400';
      case 'stable':
        return 'text-blue-600 dark:text-blue-400';
      default:
        return 'text-gray-600 dark:text-gray-300 dark:text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 text-gray-600 dark:text-gray-300 hover:text-gray-800 transition-colors mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Assessment History</h1>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, index) => (
              <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-pulse">
                <div className="bg-gray-200 h-4 w-24 rounded mb-4"></div>
                <div className="space-y-3">
                  <div className="bg-gray-200 h-3 w-full rounded"></div>
                  <div className="bg-gray-200 h-3 w-3/4 rounded"></div>
                  <div className="bg-gray-200 h-3 w-1/2 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (assessments.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 text-gray-600 dark:text-gray-300 hover:text-gray-800 transition-colors mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Assessment History</h1>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Assessments Found</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Complete your first health assessment to start tracking your health journey.
            </p>
            <button
              onClick={() => navigate('/assessment')}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Take Assessment
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-900 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 text-gray-600 dark:text-gray-300 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </button>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Assessment History</h1>
            <p className="text-gray-600 dark:text-gray-300 dark:text-gray-300 mt-2">View all your health assessments and track your progress over time.</p>
          <div className="mt-4 flex items-center gap-4 text-sm text-gray-600 dark:text-gray-300 dark:text-gray-300">
            <span>Total Assessments: <span className="font-semibold text-gray-900 dark:text-white">{assessments.length}</span></span>
            <span>•</span>
            <span>Latest: <span className="font-semibold text-gray-900 dark:text-white">{assessments[0]?.date || 'N/A'}</span></span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assessments.map((assessment, index) => {
            const trend = getHealthTrend(assessment, assessments[index + 1]);
            return (
            <div
              key={assessment.id}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                  <span className="font-semibold text-gray-900 dark:text-white">{assessment.date}</span>
                  {getTrendIcon(trend)}
                </div>
                <div className="text-right">
                  <span className="text-sm text-gray-500 dark:text-gray-400">Score:</span>
                  <span className={`ml-1 font-bold ${getScoreColor(assessment.overall_score)}`}>
                    {assessment.overall_score}
                  </span>
                </div>
              </div>
              
              <div className="space-y-3 mb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getRiskIcon(assessment.diabetes_risk)}
                    <span className="text-sm text-gray-600 dark:text-gray-300 dark:text-gray-300">Diabetes:</span>
                    <span className={`font-semibold ${getRiskColor(assessment.diabetes_risk)}`}>
                      {assessment.diabetes_risk}%
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getRiskIcon(assessment.hypertension_risk)}
                    <span className="text-sm text-gray-600 dark:text-gray-300 dark:text-gray-300">Hypertension:</span>
                    <span className={`font-semibold ${getRiskColor(assessment.hypertension_risk)}`}>
                      {assessment.hypertension_risk}%
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <Heart className="w-4 h-4" />
                    <span>Cardio: {assessment.cardiovascular_health_score}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    <span>Metabolic: {assessment.metabolic_health_score}</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskCategoryColor(assessment.risk_category_diabetes)}`}>
                    {assessment.risk_category_diabetes}
                  </span>
                  <span className={`text-xs font-medium ${getTrendColor(trend)}`}>
                    {trend === 'new' ? 'New Assessment' : 
                     trend === 'improving' ? 'Improving' :
                     trend === 'declining' ? 'Declining' : 'Stable'}
                  </span>
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => handleViewDetailedReport(assessment)}
                    className="flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm font-medium px-3 py-1 rounded-md hover:bg-blue-50 transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    View Report
                  </button>
                  
                  <button
                    onClick={() => handleDownloadPDF(assessment)}
                    disabled={downloadingPDF.has(assessment.id)}
                    className="flex items-center gap-1 text-green-600 hover:text-green-700 text-sm font-medium px-3 py-1 rounded-md hover:bg-green-50 transition-colors disabled:opacity-50"
                  >
                    <Download className="w-4 h-4" />
                    {downloadingPDF.has(assessment.id) ? 'Downloading...' : 'Download PDF'}
                  </button>
                </div>
              </div>
            </div>
            );
          })}
        </div>
        
        {assessments.length >= 50 && (
          <div className="mt-8 text-center">
            <button
              onClick={fetchAllAssessments}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Load More Assessments
            </button>
          </div>
        )}
      </div>
      
      {/* Detailed Report Modal */}
      {showDetailedReport && selectedAssessment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Detailed Health Report</h2>
                <button
                  onClick={() => {
                    setShowDetailedReport(false);
                    setSelectedAssessment(null);
                  }}
                  className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:text-gray-300 dark:hover:text-gray-300"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <p className="text-gray-600 dark:text-gray-300 dark:text-gray-300 mt-2">Assessment from {selectedAssessment.date}</p>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Health Scores Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-300" />
                    <span className="font-semibold text-blue-900 dark:text-blue-200">Overall Score</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-900 dark:text-blue-200">{selectedAssessment.overall_score}</div>
                  <div className="text-sm text-blue-700 dark:text-blue-300">Health Status</div>
                </div>
                
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Heart className="w-5 h-5 text-green-600 dark:text-green-300" />
                    <span className="font-semibold text-green-900 dark:text-green-200">Cardiovascular</span>
                  </div>
                  <div className="text-2xl font-bold text-green-900 dark:text-green-200">{selectedAssessment.cardiovascular_health_score}</div>
                  <div className="text-sm text-green-700 dark:text-green-300">Heart Health</div>
                </div>
                
                <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-300" />
                    <span className="font-semibold text-purple-900 dark:text-purple-200">Metabolic</span>
                  </div>
                  <div className="text-2xl font-bold text-purple-900 dark:text-purple-200">{selectedAssessment.metabolic_health_score}</div>
                  <div className="text-sm text-purple-700 dark:text-purple-300">Metabolism</div>
                </div>
              </div>
              
              {/* Risk Analysis */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-orange-600" />
                    Diabetes Risk Analysis
                  </h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600 dark:text-gray-300">Risk Level:</span>
                      <span className={`font-semibold ${getRiskColor(selectedAssessment.diabetes_risk)}`}>
                        {selectedAssessment.diabetes_risk}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600 dark:text-gray-300">Category:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskCategoryColor(selectedAssessment.risk_category_diabetes)}`}>
                        {selectedAssessment.risk_category_diabetes}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                    <Heart className="w-5 h-5 text-red-600" />
                    Hypertension Risk Analysis
                  </h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600 dark:text-gray-300">Risk Level:</span>
                      <span className={`font-semibold ${getRiskColor(selectedAssessment.hypertension_risk)}`}>
                        {selectedAssessment.hypertension_risk}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600 dark:text-gray-300">Category:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskCategoryColor(selectedAssessment.risk_category_hypertension)}`}>
                        {selectedAssessment.risk_category_hypertension}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Health Data Summary */}
              {selectedAssessment.input_data && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                    Health Data Summary
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    {selectedAssessment.input_data.age && (
                      <div>
                        <span className="text-gray-600 dark:text-gray-300">Age:</span>
                        <span className="font-semibold ml-1">{selectedAssessment.input_data.age} years</span>
                      </div>
                    )}
                    {selectedAssessment.input_data.bmi && (
                      <div>
                        <span className="text-gray-600 dark:text-gray-300">BMI:</span>
                        <span className="font-semibold ml-1">{selectedAssessment.input_data.bmi}</span>
                      </div>
                    )}
                    {selectedAssessment.input_data.blood_pressure && (
                      <div>
                        <span className="text-gray-600 dark:text-gray-300">BP:</span>
                        <span className="font-semibold ml-1">{selectedAssessment.input_data.blood_pressure} mmHg</span>
                      </div>
                    )}
                    {selectedAssessment.input_data.glucose_level && (
                      <div>
                        <span className="text-gray-600 dark:text-gray-300">Glucose:</span>
                        <span className="font-semibold ml-1">{selectedAssessment.input_data.glucose_level} mg/dL</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleDownloadPDF(selectedAssessment)}
                  disabled={downloadingPDF.has(selectedAssessment.id)}
                  className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  <Download className="w-4 h-4" />
                  {downloadingPDF.has(selectedAssessment.id) ? 'Downloading...' : 'Download Full Report'}
                </button>
                <button
                  onClick={() => {
                    setShowDetailedReport(false);
                    setSelectedAssessment(null);
                  }}
                  className="flex items-center gap-2 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AssessmentHistory;
