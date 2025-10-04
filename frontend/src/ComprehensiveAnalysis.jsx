import React, { useState } from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  Heart, 
  Activity, 
  TrendingUp, 
  Brain, 
  Clock, 
  Users,
  ArrowRight,
  Info,
  AlertCircle
} from 'lucide-react';

const ComprehensiveAnalysis = ({ analysis, onClose }) => {
  const [activeTab, setActiveTab] = useState('diabetes');

  // Debug logging
  console.log('ComprehensiveAnalysis received analysis:', analysis);
  console.log('Analysis type:', typeof analysis);
  console.log('Analysis keys:', analysis ? Object.keys(analysis) : 'null/undefined');

  if (!analysis) {
    console.log('No analysis data provided, showing fallback');
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Comprehensive Health Analysis</h2>
            <button
              onClick={onClose}
              className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="text-center py-8">
            <AlertCircle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Analysis Data Not Available</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              The comprehensive analysis data is not available for this assessment. 
              This might be due to the assessment being completed before this feature was added.
            </p>
            <button
              onClick={onClose}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  const getRiskColor = (level) => {
    switch (level) {
      case 'Critical': return 'text-red-600 bg-red-50 border-red-200 dark:text-red-200 dark:bg-red-900/30 dark:border-red-700';
      case 'High': return 'text-orange-600 bg-orange-50 border-orange-200 dark:text-orange-200 dark:bg-orange-900/30 dark:border-orange-700';
      case 'Moderate': return 'text-yellow-600 bg-yellow-50 border-yellow-200 dark:text-yellow-200 dark:bg-yellow-900/30 dark:border-yellow-700';
      case 'Low': return 'text-green-600 bg-green-50 border-green-200 dark:text-green-200 dark:bg-green-900/30 dark:border-green-700';
      default: return 'text-gray-600 bg-gray-50 border-gray-200 dark:text-gray-300 dark:bg-gray-800 dark:border-gray-600';
    }
  };

  const getImpactIcon = (impact) => {
    switch (impact) {
      case 'Critical': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'High': return <AlertCircle className="w-4 h-4 text-orange-600" />;
      case 'Moderate': return <Info className="w-4 h-4 text-yellow-600" />;
      case 'Protective': return <CheckCircle className="w-4 h-4 text-green-600" />;
      default: return <Info className="w-4 h-4 text-gray-600" />;
    }
  };

  const renderRiskFactors = (factors, title, icon) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center gap-3 mb-4">
        {icon}
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">({factors.length} factors)</span>
      </div>
      
      {factors.length === 0 ? (
        <div className="text-center py-8">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
          <p className="text-gray-600 dark:text-gray-300">No significant risk factors identified</p>
        </div>
      ) : (
        <div className="space-y-4">
          {factors.map((factor, index) => (
            <div key={index} className={`p-4 rounded-lg border ${getRiskColor(factor.impact)}`}>
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getImpactIcon(factor.impact)}
                  <span className="font-semibold">{factor.factor}</span>
                </div>
                <span className="text-sm font-medium">{factor.value}</span>
              </div>
              <p className="text-sm text-gray-700 mb-2">{factor.explanation}</p>
              <div className="flex items-center gap-2 text-sm">
                <ArrowRight className="w-3 h-3" />
                <span className="font-medium">{factor.recommendation}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderHealthAnalysis = (analysis, title, icon) => (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-4">
        {icon}
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <span className="text-sm text-gray-500">Score: {analysis.score || 'N/A'}</span>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {analysis.concerns && analysis.concerns.length > 0 && (
          <div>
            <h4 className="font-medium text-red-600 mb-2">Concerns</h4>
            <ul className="space-y-1">
              {analysis.concerns.map((concern, index) => (
                <li key={index} className="text-sm text-red-600 flex items-start gap-2">
                  <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                  {concern}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {analysis.strengths && analysis.strengths.length > 0 && (
          <div>
            <h4 className="font-medium text-green-600 mb-2">Strengths</h4>
            <ul className="space-y-1">
              {analysis.strengths.map((strength, index) => (
                <li key={index} className="text-sm text-green-600 flex items-start gap-2">
                  <CheckCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                  {strength}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      {analysis.recommendations && (
        <div className="mt-4">
          <h4 className="font-medium text-blue-600 mb-2">Recommendations</h4>
          <ul className="space-y-1">
            {analysis.recommendations.map((rec, index) => (
              <li key={index} className="text-sm text-blue-600 flex items-start gap-2">
                <ArrowRight className="w-3 h-3 mt-0.5 flex-shrink-0" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderLifestyleAnalysis = (analysis) => (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-4">
        <Activity className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">Lifestyle Impact</h3>
        <span className="text-sm text-gray-500">Score: {analysis.lifestyle_score}</span>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {analysis.positive_factors && analysis.positive_factors.length > 0 && (
          <div>
            <h4 className="font-medium text-green-600 mb-2">Positive Factors</h4>
            <ul className="space-y-1">
              {analysis.positive_factors.map((factor, index) => (
                <li key={index} className="text-sm text-green-600 flex items-start gap-2">
                  <CheckCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {analysis.negative_factors && analysis.negative_factors.length > 0 && (
          <div>
            <h4 className="font-medium text-red-600 mb-2">Areas for Improvement</h4>
            <ul className="space-y-1">
              {analysis.negative_factors.map((factor, index) => (
                <li key={index} className="text-sm text-red-600 flex items-start gap-2">
                  <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      {analysis.recommendations && (
        <div className="mt-4">
          <h4 className="font-medium text-blue-600 mb-2">Lifestyle Recommendations</h4>
          <ul className="space-y-1">
            {analysis.recommendations.map((rec, index) => (
              <li key={index} className="text-sm text-blue-600 flex items-start gap-2">
                <ArrowRight className="w-3 h-3 mt-0.5 flex-shrink-0" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderAgeGenderConsiderations = (considerations) => (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-4">
        <Users className="w-5 h-5 text-purple-600" />
        <h3 className="text-lg font-semibold text-gray-900">Age & Gender Considerations</h3>
      </div>
      
      <div className="space-y-4">
        {considerations.map((consideration, index) => (
          <div key={index} className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded">
                {consideration.category}
              </span>
            </div>
            <p className="text-sm text-gray-700 mb-2">{consideration.message}</p>
            <div className="flex items-center gap-2 text-sm text-purple-600">
              <span className="font-medium">Focus:</span>
              <span>{consideration.focus}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Comprehensive Health Analysis</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Tab Navigation */}
          <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
            {[
              { id: 'diabetes', label: 'Diabetes Risk', icon: <TrendingUp className="w-4 h-4" /> },
              { id: 'hypertension', label: 'Hypertension Risk', icon: <Heart className="w-4 h-4" /> },
              { id: 'metabolic', label: 'Metabolic Health', icon: <Brain className="w-4 h-4" /> },
              { id: 'cardiovascular', label: 'Cardiovascular', icon: <Activity className="w-4 h-4" /> },
              { id: 'lifestyle', label: 'Lifestyle', icon: <Clock className="w-4 h-4" /> },
              { id: 'considerations', label: 'Considerations', icon: <Users className="w-4 h-4" /> }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
          
          {/* Tab Content */}
          <div className="space-y-6">
            {activeTab === 'diabetes' && (
              <div className="space-y-6">
                {renderRiskFactors(
                  analysis.diabetes_risk_factors?.critical_concerns || [],
                  'Critical Concerns',
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                )}
                {renderRiskFactors(
                  analysis.diabetes_risk_factors?.risk_factors || [],
                  'Risk Factors',
                  <AlertCircle className="w-5 h-5 text-orange-600" />
                )}
                {renderRiskFactors(
                  analysis.diabetes_risk_factors?.moderate_concerns || [],
                  'Moderate Concerns',
                  <Info className="w-5 h-5 text-yellow-600" />
                )}
                {renderRiskFactors(
                  analysis.diabetes_risk_factors?.protective_factors || [],
                  'Protective Factors',
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
              </div>
            )}
            
            {activeTab === 'hypertension' && (
              <div className="space-y-6">
                {renderRiskFactors(
                  analysis.hypertension_risk_factors?.critical_concerns || [],
                  'Critical Concerns',
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                )}
                {renderRiskFactors(
                  analysis.hypertension_risk_factors?.risk_factors || [],
                  'Risk Factors',
                  <AlertCircle className="w-5 h-5 text-orange-600" />
                )}
                {renderRiskFactors(
                  analysis.hypertension_risk_factors?.moderate_concerns || [],
                  'Moderate Concerns',
                  <Info className="w-5 h-5 text-yellow-600" />
                )}
                {renderRiskFactors(
                  analysis.hypertension_risk_factors?.protective_factors || [],
                  'Protective Factors',
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
              </div>
            )}
            
            {activeTab === 'metabolic' && (
              renderHealthAnalysis(
                analysis.metabolic_health_analysis,
                'Metabolic Health Analysis',
                <Brain className="w-5 h-5 text-green-600" />
              )
            )}
            
            {activeTab === 'cardiovascular' && (
              renderHealthAnalysis(
                analysis.cardiovascular_health_analysis,
                'Cardiovascular Health Analysis',
                <Heart className="w-5 h-5 text-red-600" />
              )
            )}
            
            {activeTab === 'lifestyle' && (
              renderLifestyleAnalysis(analysis.lifestyle_impact_analysis)
            )}
            
            {activeTab === 'considerations' && (
              renderAgeGenderConsiderations(analysis.age_gender_considerations || [])
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComprehensiveAnalysis;

