import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, ArrowLeft, Activity, Droplet, Scale, TrendingUp, AlertCircle, Download, MessageCircle } from 'lucide-react';
import { predictionAPI } from './api';
import { useSettings } from './SettingsContext';
import toast from 'react-hot-toast';
import HealthQA from './HealthQA';
import RecentAssessments from './RecentAssessments';
import ComprehensiveAnalysis from './ComprehensiveAnalysis';

const HealthAssessment = () => {
  const navigate = useNavigate();
  const { getRiskThreshold, shouldShowNotification } = useSettings();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showQA, setShowQA] = useState(false);
  const [showComprehensiveAnalysis, setShowComprehensiveAnalysis] = useState(false);

  // Load saved assessment result on component mount
  useEffect(() => {
    const savedResult = localStorage.getItem('latestAssessmentResult');
    if (savedResult) {
      try {
        const parsedResult = JSON.parse(savedResult);
        setResult(parsedResult);
        console.log('Restored assessment result from localStorage:', parsedResult);
      } catch (error) {
        console.error('Error parsing saved assessment result:', error);
        localStorage.removeItem('latestAssessmentResult');
      }
    }
  }, []);

  // Save assessment result to localStorage whenever it changes
  useEffect(() => {
    if (result) {
      localStorage.setItem('latestAssessmentResult', JSON.stringify(result));
      console.log('Saved assessment result to localStorage:', result);
    }
  }, [result]);

  // Cleanup function to clear saved result when component unmounts (optional)
  useEffect(() => {
    return () => {
      // Optional: Clear saved result when component unmounts
      // Uncomment the line below if you want to clear the result when leaving the page
      // localStorage.removeItem('latestAssessmentResult');
    };
  }, []);

  // Fallback function to generate basic analysis if comprehensive_analysis is missing
  const generateFallbackAnalysis = (result) => {
    console.log('Generating fallback analysis for result:', result);
    
    const diabetesRisk = result.diabetes_risk || 0;
    const hypertensionRisk = result.hypertension_risk || 0;
    
    return {
      diabetes_risk_factors: {
        critical_concerns: diabetesRisk > 0.7 ? [{
          factor: "High Diabetes Risk",
          value: `${(diabetesRisk * 100).toFixed(1)}%`,
          explanation: "Your diabetes risk is significantly elevated based on your health profile.",
          recommendation: "Consult with a healthcare provider immediately for diabetes screening and management.",
          impact: "Critical"
        }] : [],
        risk_factors: diabetesRisk > 0.3 ? [{
          factor: "Moderate Diabetes Risk",
          value: `${(diabetesRisk * 100).toFixed(1)}%`,
          explanation: "Your diabetes risk is elevated and requires attention.",
          recommendation: "Focus on lifestyle modifications including diet and exercise.",
          impact: "High"
        }] : [],
        protective_factors: diabetesRisk < 0.3 ? [{
          factor: "Low Diabetes Risk",
          value: `${(diabetesRisk * 100).toFixed(1)}%`,
          explanation: "Your current health profile shows good protection against diabetes.",
          recommendation: "Continue maintaining your healthy lifestyle habits.",
          impact: "Protective"
        }] : []
      },
      hypertension_risk_factors: {
        critical_concerns: hypertensionRisk > 0.7 ? [{
          factor: "High Hypertension Risk",
          value: `${(hypertensionRisk * 100).toFixed(1)}%`,
          explanation: "Your hypertension risk is significantly elevated.",
          recommendation: "Schedule immediate consultation with a healthcare provider.",
          impact: "Critical"
        }] : [],
        risk_factors: hypertensionRisk > 0.3 ? [{
          factor: "Moderate Hypertension Risk",
          value: `${(hypertensionRisk * 100).toFixed(1)}%`,
          explanation: "Your hypertension risk is elevated and needs attention.",
          recommendation: "Focus on blood pressure management through lifestyle changes.",
          impact: "High"
        }] : [],
        protective_factors: hypertensionRisk < 0.3 ? [{
          factor: "Low Hypertension Risk",
          value: `${(hypertensionRisk * 100).toFixed(1)}%`,
          explanation: "Your current health profile shows good cardiovascular protection.",
          recommendation: "Continue your healthy lifestyle to maintain low risk.",
          impact: "Protective"
        }] : []
      },
      metabolic_health_analysis: {
        score: result.metabolic_health_score || 75,
        concerns: diabetesRisk > 0.5 ? ["Elevated diabetes risk", "Blood sugar management needed"] : [],
        strengths: diabetesRisk < 0.3 ? ["Good metabolic health", "Low diabetes risk"] : [],
        recommendations: diabetesRisk > 0.3 ? [
          "Focus on blood sugar control",
          "Maintain healthy weight",
          "Regular physical activity"
        ] : [
          "Continue current healthy habits",
          "Regular health monitoring"
        ]
      },
      cardiovascular_health_analysis: {
        score: result.cardiovascular_health_score || 80,
        concerns: hypertensionRisk > 0.5 ? ["Elevated blood pressure risk", "Cardiovascular monitoring needed"] : [],
        strengths: hypertensionRisk < 0.3 ? ["Good cardiovascular health", "Low blood pressure risk"] : [],
        recommendations: hypertensionRisk > 0.3 ? [
          "Focus on blood pressure management",
          "Heart-healthy diet",
          "Regular cardiovascular exercise"
        ] : [
          "Continue heart-healthy lifestyle",
          "Regular cardiovascular monitoring"
        ]
      },
      lifestyle_impact_analysis: {
        lifestyle_score: 75,
        positive_factors: ["Regular health monitoring", "Health assessment completion"],
        negative_factors: diabetesRisk > 0.5 || hypertensionRisk > 0.5 ? ["High disease risk factors"] : [],
        recommendations: [
          "Maintain regular health checkups",
          "Focus on preventive health measures",
          "Continue health monitoring"
        ]
      },
      age_gender_considerations: [
        {
          category: "Health Monitoring",
          message: "Regular health assessments help track your health progress over time.",
          focus: "Continue monitoring your health metrics regularly"
        }
      ]
    };
  };
  const [formData, setFormData] = useState({
    age: '',
    gender: 1,
    bmi: '',
    blood_pressure: '',
    cholesterol_level: '',
    glucose_level: '',
    physical_activity: 5,
    smoking_status: 0,
    alcohol_intake: 0,
    family_history: 0,
    hba1c: '',
    daily_steps: 7000,
    sleep_hours: 7,
    sleep_quality: 7,
    stress_level: 5
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: parseFloat(value) || value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Prepare data matching backend HealthInput model exactly
      const assessmentData = {
        age: parseFloat(formData.age),
        gender: parseFloat(formData.gender), // 0 or 1
        bmi: parseFloat(formData.bmi),
        blood_pressure: parseFloat(formData.blood_pressure),
        cholesterol_level: parseFloat(formData.cholesterol_level),
        glucose_level: parseFloat(formData.glucose_level),
        physical_activity: parseFloat(formData.physical_activity),
        smoking_status: parseFloat(formData.smoking_status),
        alcohol_intake: parseFloat(formData.alcohol_intake),
        family_history: parseFloat(formData.family_history),
        // Optional fields
        ...(formData.hba1c && { hba1c: parseFloat(formData.hba1c) }),
        ...(formData.daily_steps && { daily_steps: parseFloat(formData.daily_steps) }),
        ...(formData.sleep_hours && { sleep_hours: parseFloat(formData.sleep_hours) }),
        ...(formData.sleep_quality && { sleep_quality: parseFloat(formData.sleep_quality) }),
        ...(formData.stress_level && { stress_level: parseFloat(formData.stress_level) })
      };
  
      console.log('Sending assessment data:', assessmentData); // Debug log
      
      const response = await predictionAPI.predict(assessmentData);
      setResult(response);
      toast.success('Health assessment completed successfully!');
      
      // Check for risk alerts based on user settings
      const riskThreshold = getRiskThreshold();
      const diabetesRisk = response.diabetes_risk || 0;
      const hypertensionRisk = response.hypertension_risk || 0;
      
      if (shouldShowNotification('riskAlerts')) {
        if (diabetesRisk > riskThreshold) {
          if (window.notificationManager) {
            window.notificationManager.showRiskAlert('diabetes', Math.round(diabetesRisk * 100));
          }
        }
        if (hypertensionRisk > riskThreshold) {
          if (window.notificationManager) {
            window.notificationManager.showRiskAlert('hypertension', Math.round(hypertensionRisk * 100));
          }
        }
      }
    } catch (error) {
      console.error('Assessment error:', error.response?.data || error);
      
      // Handle validation errors properly
      let errorMessage = 'Failed to complete assessment. Please try again.';
      
      if (error.response?.status === 422) {
        // Handle validation errors
        const validationErrors = error.response?.data?.detail;
        if (Array.isArray(validationErrors)) {
          errorMessage = validationErrors.map(err => `${err.loc?.join('.')}: ${err.msg}`).join(', ');
        } else if (typeof validationErrors === 'string') {
          errorMessage = validationErrors;
        }
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleStartNewAssessment = () => {
    // Clear the saved result and reset form
    localStorage.removeItem('latestAssessmentResult');
    setResult(null);
    setFormData({
      age: '',
      gender: 1,
      bmi: '',
      blood_pressure: '',
      cholesterol_level: '',
      glucose_level: '',
      physical_activity: '',
      smoking_status: 0,
      alcohol_intake: 0,
      family_history: 0,
      hba1c: '',
      daily_steps: '',
      sleep_hours: '',
      sleep_quality: '',
      stress_level: ''
    });
    toast.success('Starting new assessment...');
  };

  const getRiskColor = (risk) => {
    if (risk < 0.25) return 'text-green-600 bg-green-50 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-700';
    if (risk < 0.5) return 'text-yellow-600 bg-yellow-50 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-700';
    if (risk < 0.75) return 'text-orange-600 bg-orange-50 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-700';
    return 'text-red-600 bg-red-50 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-700';
  };

  if (result) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-dark-900 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={handleStartNewAssessment}
            className="mb-6 flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            New Assessment
          </button>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Your Health Assessment Results</h2>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className={`p-6 rounded-xl border-2 ${getRiskColor(result.diabetes_risk)}`}>
                <div className="flex items-center justify-between mb-4">
                  <Activity className="w-8 h-8" />
                  <span className="text-sm font-semibold">DIABETES RISK</span>
                </div>
                <p className="text-4xl font-bold mb-2">{(result.diabetes_risk * 100).toFixed(1)}%</p>
                <p className="text-sm mb-1">{result.risk_category_diabetes}</p>
                <p className="text-xs opacity-75">Confidence: {result.diabetes_confidence}</p>
              </div>

              <div className={`p-6 rounded-xl border-2 ${getRiskColor(result.hypertension_risk)}`}>
                <div className="flex items-center justify-between mb-4">
                  <Heart className="w-8 h-8" />
                  <span className="text-sm font-semibold">HYPERTENSION RISK</span>
                </div>
                <p className="text-4xl font-bold mb-2">{(result.hypertension_risk * 100).toFixed(1)}%</p>
                <p className="text-sm mb-1">{result.risk_category_hypertension}</p>
                <p className="text-xs opacity-75">Confidence: {result.hypertension_confidence}</p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="p-6 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
                <p className="text-sm text-blue-600 dark:text-blue-300 font-semibold mb-2">Metabolic Health Score</p>
                <p className="text-3xl font-bold text-blue-900 dark:text-blue-200">{result.metabolic_health_score}</p>
                <div className="mt-3 w-full bg-blue-200 dark:bg-blue-800 rounded-full h-2">
                  <div 
                    className="bg-blue-600 dark:bg-blue-400 h-2 rounded-full transition-all"
                    style={{ width: `${result.metabolic_health_score}%` }}
                  ></div>
                </div>
              </div>

              <div className="p-6 bg-purple-50 dark:bg-purple-900/20 rounded-xl">
                <p className="text-sm text-purple-600 dark:text-purple-300 font-semibold mb-2">Cardiovascular Health Score</p>
                <p className="text-3xl font-bold text-purple-900 dark:text-purple-200">{result.cardiovascular_health_score}</p>
                <div className="mt-3 w-full bg-purple-200 dark:bg-purple-800 rounded-full h-2">
                  <div 
                    className="bg-purple-600 dark:bg-purple-400 h-2 rounded-full transition-all"
                    style={{ width: `${result.cardiovascular_health_score}%` }}
                  ></div>
                </div>
              </div>
            </div>
            {/* Action Buttons */}
            <div className="mb-8 flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => setShowQA(true)}
                className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <MessageCircle className="w-5 h-5" />
                Ask Questions About Your Report
              </button>
              
              <button
                onClick={() => {
                  console.log('Comprehensive Analysis button clicked');
                  console.log('Result data:', result);
                  console.log('Comprehensive analysis data:', result?.comprehensive_analysis);
                  setShowComprehensiveAnalysis(true);
                }}
                className="flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                <Activity className="w-5 h-5" />
                Detailed Analysis
              </button>
              
              <button
                onClick={async () => {
                  try {
                    // Prepare the same data that was sent for prediction
                    const assessmentData = {
                      age: parseFloat(formData.age),
                      gender: parseFloat(formData.gender),
                      bmi: parseFloat(formData.bmi),
                      blood_pressure: parseFloat(formData.blood_pressure),
                      cholesterol_level: parseFloat(formData.cholesterol_level),
                      glucose_level: parseFloat(formData.glucose_level),
                      physical_activity: parseFloat(formData.physical_activity),
                      smoking_status: parseFloat(formData.smoking_status),
                      alcohol_intake: parseFloat(formData.alcohol_intake),
                      family_history: parseFloat(formData.family_history),
                      ...(formData.hba1c && { hba1c: parseFloat(formData.hba1c) }),
                      ...(formData.daily_steps && { daily_steps: parseFloat(formData.daily_steps) }),
                      ...(formData.sleep_hours && { sleep_hours: parseFloat(formData.sleep_hours) }),
                      ...(formData.stress_level && { stress_level: parseFloat(formData.stress_level) })
                    };
                    
                    await predictionAPI.downloadPDF(assessmentData);
                    toast.success('PDF downloaded successfully!');
                  } catch (error) {
                    console.error('PDF download error:', error);
                    toast.error('Failed to download PDF');
                  }
                }}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Download className="w-5 h-5" />
                Download PDF Report
              </button>
            </div>
            
            {/* Additional action buttons */}
            <div className="mt-6 flex justify-center">
              <button
                onClick={handleStartNewAssessment}
                className="flex items-center gap-2 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                Start New Assessment
              </button>
            </div>
            <div className="mb-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Personalized Recommendations</h3>
              
              <div className="space-y-4">
                {result.nutrition_recommendations?.primary && result.nutrition_recommendations.primary.length > 0 && (
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-700">
                    <p className="font-semibold text-green-900 dark:text-green-200 mb-2">Nutrition</p>
                    <ul className="space-y-1">
                      {result.nutrition_recommendations.primary.map((rec, idx) => (
                        <li key={idx} className="text-sm text-green-800 dark:text-green-100">• {rec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.fitness_recommendations?.primary && result.fitness_recommendations.primary.length > 0 && (
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-700">
                    <p className="font-semibold text-blue-900 dark:text-blue-200 mb-2">Fitness</p>
                    <ul className="space-y-1">
                      {result.fitness_recommendations.primary.map((rec, idx) => (
                        <li key={idx} className="text-sm text-blue-800 dark:text-blue-100">• {rec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.lifestyle_recommendations && result.lifestyle_recommendations.length > 0 && (
                  <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-xl border border-purple-200 dark:border-purple-700">
                    <p className="font-semibold text-purple-900 dark:text-purple-200 mb-2">Lifestyle</p>
                    <ul className="space-y-1">
                      {result.lifestyle_recommendations.slice(0, 3).map((rec, idx) => (
                        <li key={idx} className="text-sm text-purple-800 dark:text-purple-100">• {rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={() => navigate('/dashboard')}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transition-all"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
        
        {/* Recent Assessments Section */}
        <div className="mt-8">
          <RecentAssessments limit={3} showViewAll={false} />
        </div>
        
        {/* Q&A Modal */}
        {showQA && result && (
          <HealthQA
            healthData={{
              // Include original input data
              age: parseFloat(formData.age),
              gender: parseFloat(formData.gender),
              bmi: parseFloat(formData.bmi),
              blood_pressure: parseFloat(formData.blood_pressure),
              cholesterol_level: parseFloat(formData.cholesterol_level),
              glucose_level: parseFloat(formData.glucose_level),
              physical_activity: parseFloat(formData.physical_activity),
              smoking_status: parseFloat(formData.smoking_status),
              alcohol_intake: parseFloat(formData.alcohol_intake),
              family_history: parseFloat(formData.family_history),
              ...(formData.hba1c && { hba1c: parseFloat(formData.hba1c) }),
              ...(formData.daily_steps && { daily_steps: parseFloat(formData.daily_steps) }),
              ...(formData.sleep_hours && { sleep_hours: parseFloat(formData.sleep_hours) }),
              ...(formData.sleep_quality && { sleep_quality: parseFloat(formData.sleep_quality) }),
              ...(formData.stress_level && { stress_level: parseFloat(formData.stress_level) }),
              
              // Include actual assessment results for personalized answers
              diabetes_risk: result.diabetes_risk,
              hypertension_risk: result.hypertension_risk,
              metabolic_health_score: result.metabolic_health_score,
              cardiovascular_health_score: result.cardiovascular_health_score,
              overall_health_score: result.overall_health_score,
              risk_level: result.risk_level,
              comprehensive_analysis: result.comprehensive_analysis
            }}
            onClose={() => setShowQA(false)}
          />
        )}
        
        {/* Comprehensive Analysis Modal */}
        {showComprehensiveAnalysis && result && (
          <ComprehensiveAnalysis
            analysis={result.comprehensive_analysis || generateFallbackAnalysis(result)}
            onClose={() => setShowComprehensiveAnalysis(false)}
          />
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-900 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <button
          onClick={() => navigate('/dashboard')}
          className="mb-6 flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Dashboard
        </button>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Health Risk Assessment</h1>
            <p className="text-gray-600 dark:text-gray-400">Provide your health information for personalized risk analysis</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Age</label>
                <input
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                  required
                  min="0"
                  max="120"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Gender</label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                >
                  <option value={0}>Female</option>
                  <option value={1}>Male</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">BMI</label>
                <input
                  type="number"
                  step="0.1"
                  name="bmi"
                  value={formData.bmi}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                  required
                  min="10"
                  max="60"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Blood Pressure (mmHg)</label>
                <input
                  type="number"
                  name="blood_pressure"
                  value={formData.blood_pressure}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                  required
                  min="80"
                  max="200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Cholesterol (mg/dL)</label>
                <input
                  type="number"
                  name="cholesterol_level"
                  value={formData.cholesterol_level}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                  required
                  min="100"
                  max="400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Glucose Level (mg/dL)</label>
                <input
                  type="number"
                  name="glucose_level"
                  value={formData.glucose_level}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                  required
                  min="50"
                  max="300"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Physical Activity (0-10)</label>
                <input
                  type="range"
                  name="physical_activity"
                  value={formData.physical_activity}
                  onChange={handleChange}
                  className="w-full"
                  min="0"
                  max="10"
                />
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Current: {formData.physical_activity}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Smoking Status</label>
                <select
                  name="smoking_status"
                  value={formData.smoking_status}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                >
                  <option value={0}>Never</option>
                  <option value={1}>Former</option>
                  <option value={2}>Current</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Alcohol Intake (0-5)</label>
                <input
                  type="range"
                  name="alcohol_intake"
                  value={formData.alcohol_intake}
                  onChange={handleChange}
                  className="w-full"
                  min="0"
                  max="5"
                />
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Current: {formData.alcohol_intake}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Family History</label>
                <select
                  name="family_history"
                  value={formData.family_history}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                >
                  <option value={0}>No</option>
                  <option value={1}>Yes</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">HbA1c (%)</label>
                <input
                  type="number"
                  step="0.1"
                  name="hba1c"
                  value={formData.hba1c}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                  min="3.0"
                  max="15.0"
                  placeholder="e.g., 5.7"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Optional: Long-term blood sugar control indicator</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Daily Steps</label>
                <input
                  type="number"
                  name="daily_steps"
                  value={formData.daily_steps}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                  min="0"
                  max="30000"
                  placeholder="e.g., 8000"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Average steps per day</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sleep Hours</label>
                <input
                  type="number"
                  step="0.5"
                  name="sleep_hours"
                  value={formData.sleep_hours}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                  min="3"
                  max="12"
                  placeholder="e.g., 7.5"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Average hours of sleep per night</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sleep Quality (1-10)</label>
                <input
                  type="range"
                  name="sleep_quality"
                  value={formData.sleep_quality}
                  onChange={handleChange}
                  className="w-full"
                  min="1"
                  max="10"
                />
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Current: {formData.sleep_quality}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Stress Level (1-10)</label>
                <input
                  type="range"
                  name="stress_level"
                  value={formData.stress_level}
                  onChange={handleChange}
                  className="w-full"
                  min="1"
                  max="10"
                />
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Current: {formData.stress_level}</p>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Get Health Assessment'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default HealthAssessment;