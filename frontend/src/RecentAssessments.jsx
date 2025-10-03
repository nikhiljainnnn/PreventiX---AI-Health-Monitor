import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, TrendingUp, Heart, Activity, AlertCircle, CheckCircle } from 'lucide-react';
import { recentAssessments } from './api';
import toast from 'react-hot-toast';

const RecentAssessments = ({ limit = 10, showViewAll = true }) => {
  const navigate = useNavigate();
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecentAssessments();
  }, [limit]);

  // Add a refresh function that can be called externally
  const refreshAssessments = () => {
    fetchRecentAssessments();
  };

  const fetchRecentAssessments = async () => {
    try {
      setLoading(true);
      console.log('Fetching recent assessments...');
      
      // Check if user is authenticated
      const token = localStorage.getItem('token');
      if (!token) {
        console.log('No authentication token found');
        setAssessments([]);
        return;
      }
      
      const data = await recentAssessments.getRecent(limit);
      console.log('Recent assessments data:', data);
      setAssessments(data);
    } catch (error) {
      console.error('Error fetching recent assessments:', error);
      
      // Check if it's an authentication error
      if (error.response?.status === 401) {
        console.log('Authentication failed, clearing token');
        localStorage.removeItem('token');
        setAssessments([]);
        return;
      }
      
      // For other errors, don't show toast to avoid spam
      console.log('API error:', error.response?.data || error.message);
      setAssessments([]);
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

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Recent Assessments</h2>
        </div>
        <div className="space-y-4">
          {[...Array(3)].map((_, index) => (
            <div key={index} className="animate-pulse">
              <div className="bg-gray-200 h-4 w-24 rounded mb-2"></div>
              <div className="bg-gray-200 h-3 w-48 rounded mb-2"></div>
              <div className="bg-gray-200 h-3 w-16 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (assessments.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Recent Assessments</h2>
        </div>
        <div className="text-center py-8">
          <Activity className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No Assessments Yet</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Complete your first health assessment to start tracking your health journey.
          </p>
          <button
            onClick={() => window.location.href = '/assessment'}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Take Assessment
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">Recent Assessments</h2>
        <div className="flex gap-2">
          <button 
            onClick={refreshAssessments}
            className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-medium text-sm"
          >
            Refresh
          </button>
          {showViewAll && (
            <button 
              onClick={() => navigate('/assessment-history')}
              className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium text-sm"
            >
              View All
            </button>
          )}
        </div>
      </div>
      
      <div className="space-y-4">
        {assessments.map((assessment, index) => (
          <div
            key={assessment.id}
            className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                <span className="font-semibold text-gray-900 dark:text-white">{assessment.date}</span>
              </div>
              <div className="text-right">
                <span className="text-sm text-gray-500 dark:text-gray-400">Score:</span>
                <span className={`ml-1 font-bold ${getScoreColor(assessment.overall_score)}`}>
                  {assessment.overall_score}
                </span>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-3">
              <div className="flex items-center gap-2">
                {getRiskIcon(assessment.diabetes_risk)}
                <span className="text-sm text-gray-600 dark:text-gray-300">Diabetes:</span>
                <span className={`font-semibold ${getRiskColor(assessment.diabetes_risk)}`}>
                  {assessment.diabetes_risk}%
                </span>
              </div>
              <div className="flex items-center gap-2">
                {getRiskIcon(assessment.hypertension_risk)}
                <span className="text-sm text-gray-600 dark:text-gray-300">Hypertension:</span>
                <span className={`font-semibold ${getRiskColor(assessment.hypertension_risk)}`}>
                  {assessment.hypertension_risk}%
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
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
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  assessment.risk_category_diabetes === 'Low Risk' 
                    ? 'bg-green-100 text-green-800'
                    : assessment.risk_category_diabetes === 'Moderate Risk'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {assessment.risk_category_diabetes}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {assessments.length >= limit && (
        <div className="mt-4 text-center">
          <button 
            onClick={() => navigate('/assessment-history')}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium text-sm"
          >
            Load More Assessments
          </button>
        </div>
      )}
    </div>
  );
};

export default RecentAssessments;
