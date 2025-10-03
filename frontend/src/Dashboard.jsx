import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import SettingsModal from './SettingsModal';
import RecentAssessments from './RecentAssessments';
import { recentAssessments } from './api';
import { Heart, Activity, TrendingUp, Calendar, User, LogOut, BarChart3, Bell, Settings, Plus, ChevronRight, Droplet, Zap } from 'lucide-react';

const Dashboard = () => {
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [showSettings, setShowSettings] = useState(false);
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    diabetesRisk: 0,
    hypertensionRisk: 0,
    metabolicScore: 0,
    cardiovascularScore: 0,
    diabetesImprovement: 0,
    hypertensionImprovement: 0,
    metabolicImprovement: 0,
    cardiovascularImprovement: 0
  });

  // Fetch assessments data
  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        setLoading(true);
        const data = await recentAssessments.getRecent(10); // Get last 10 assessments
        setAssessments(data);
        
        if (data.length > 0) {
          calculateStats(data);
        }
      } catch (error) {
        console.error('Failed to fetch assessments:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAssessments();
  }, []);

  const calculateStats = (assessmentData) => {
    if (assessmentData.length === 0) return;

    // Get latest assessment
    const latest = assessmentData[0];
    
    // Calculate improvements (compare with previous assessment)
    const previous = assessmentData.length > 1 ? assessmentData[1] : null;
    
    const newStats = {
      diabetesRisk: latest.diabetes_risk / 100, // Convert percentage to decimal
      hypertensionRisk: latest.hypertension_risk / 100,
      metabolicScore: latest.metabolic_health_score || 0,
      cardiovascularScore: latest.cardiovascular_health_score || 0,
      diabetesImprovement: previous ? 
        ((previous.diabetes_risk - latest.diabetes_risk) / previous.diabetes_risk * 100) : 0,
      hypertensionImprovement: previous ? 
        ((previous.hypertension_risk - latest.hypertension_risk) / previous.hypertension_risk * 100) : 0,
      metabolicImprovement: previous ? 
        ((latest.metabolic_health_score - (previous.metabolic_health_score || 0)) / (previous.metabolic_health_score || 1) * 100) : 0,
      cardiovascularImprovement: previous ? 
        ((latest.cardiovascular_health_score - (previous.cardiovascular_health_score || 0)) / (previous.cardiovascular_health_score || 1) * 100) : 0
    };

    setStats(newStats);
  };

  const recommendations = [
    { category: 'Nutrition', text: 'Increase fiber intake to 25-30g daily', priority: 'high' },
    { category: 'Fitness', text: 'Aim for 150 minutes of moderate exercise weekly', priority: 'medium' },
    { category: 'Lifestyle', text: 'Maintain consistent sleep schedule (7-9 hours)', priority: 'medium' }
  ];

  const getRiskColor = (risk) => {
    if (risk < 0.25) return 'text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400';
    if (risk < 0.5) return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20 dark:text-yellow-400';
    if (risk < 0.75) return 'text-orange-600 bg-orange-50 dark:bg-orange-900/20 dark:text-orange-400';
    return 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400';
  };

  const getRiskLabel = (risk) => {
    if (risk < 0.25) return 'Low Risk';
    if (risk < 0.5) return 'Moderate Risk';
    if (risk < 0.75) return 'High Risk';
    return 'Very High Risk';
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading your health data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {/* Settings Modal */}
      <SettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} />

      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <Heart className="w-8 h-8 text-blue-600 dark:text-blue-400" fill="currentColor" />
              <span className="text-2xl font-bold text-gray-800 dark:text-white">PreventiX</span>
            </div>
            
            <div className="flex items-center gap-4">
              <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors relative">
                <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <button 
                onClick={() => setShowSettings(true)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <Settings className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
              <div className="flex items-center gap-3 pl-4 border-l border-gray-200 dark:border-gray-700">
                <div className="w-9 h-9 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
                <button 
                  onClick={handleLogout}
                  className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome back, {user?.full_name || 'User'}!
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {assessments.length > 0 
              ? "Here's your personalized health summary" 
              : "Complete your first health assessment to see personalized insights"
            }
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-xl ${getRiskColor(stats.diabetesRisk)}`}>
                <Activity className="w-6 h-6" />
              </div>
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">DIABETES</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {(stats.diabetesRisk * 100).toFixed(0)}%
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{getRiskLabel(stats.diabetesRisk)}</p>
            <div className="mt-3 flex items-center text-xs">
              {stats.diabetesImprovement > 0 ? (
                <div className="flex items-center text-green-600 dark:text-green-400">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  <span>{stats.diabetesImprovement.toFixed(1)}% improvement</span>
                </div>
              ) : stats.diabetesImprovement < 0 ? (
                <div className="flex items-center text-red-600 dark:text-red-400">
                  <TrendingUp className="w-3 h-3 mr-1 rotate-180" />
                  <span>{Math.abs(stats.diabetesImprovement).toFixed(1)}% increase</span>
                </div>
              ) : (
                <div className="flex items-center text-gray-600 dark:text-gray-400">
                  <span>No change</span>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-xl ${getRiskColor(stats.hypertensionRisk)}`}>
                <Heart className="w-6 h-6" />
              </div>
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">HYPERTENSION</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {(stats.hypertensionRisk * 100).toFixed(0)}%
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{getRiskLabel(stats.hypertensionRisk)}</p>
            <div className="mt-3 flex items-center text-xs">
              {stats.hypertensionImprovement > 0 ? (
                <div className="flex items-center text-green-600 dark:text-green-400">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  <span>{stats.hypertensionImprovement.toFixed(1)}% improvement</span>
                </div>
              ) : stats.hypertensionImprovement < 0 ? (
                <div className="flex items-center text-red-600 dark:text-red-400">
                  <TrendingUp className="w-3 h-3 mr-1 rotate-180" />
                  <span>{Math.abs(stats.hypertensionImprovement).toFixed(1)}% increase</span>
                </div>
              ) : (
                <div className="flex items-center text-gray-600 dark:text-gray-400">
                  <span>No change</span>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400">
                <BarChart3 className="w-6 h-6" />
              </div>
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">METABOLIC</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {stats.metabolicScore}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Health Score</p>
            <div className="mt-3 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${stats.metabolicScore}%` }}
              ></div>
            </div>
            <div className="mt-2 flex items-center text-xs">
              {stats.metabolicImprovement > 0 ? (
                <div className="flex items-center text-green-600 dark:text-green-400">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  <span>{stats.metabolicImprovement.toFixed(1)}% improvement</span>
                </div>
              ) : stats.metabolicImprovement < 0 ? (
                <div className="flex items-center text-red-600 dark:text-red-400">
                  <TrendingUp className="w-3 h-3 mr-1 rotate-180" />
                  <span>{Math.abs(stats.metabolicImprovement).toFixed(1)}% decrease</span>
                </div>
              ) : (
                <div className="flex items-center text-gray-600 dark:text-gray-400">
                  <span>No change</span>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400">
                <Heart className="w-6 h-6" />
              </div>
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">CARDIOVASCULAR</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {stats.cardiovascularScore}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Health Score</p>
            <div className="mt-3 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-purple-500 to-purple-600 h-2 rounded-full transition-all"
                style={{ width: `${stats.cardiovascularScore}%` }}
              ></div>
            </div>
            <div className="mt-2 flex items-center text-xs">
              {stats.cardiovascularImprovement > 0 ? (
                <div className="flex items-center text-green-600 dark:text-green-400">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  <span>{stats.cardiovascularImprovement.toFixed(1)}% improvement</span>
                </div>
              ) : stats.cardiovascularImprovement < 0 ? (
                <div className="flex items-center text-red-600 dark:text-red-400">
                  <TrendingUp className="w-3 h-3 mr-1 rotate-180" />
                  <span>{Math.abs(stats.cardiovascularImprovement).toFixed(1)}% decrease</span>
                </div>
              ) : (
                <div className="flex items-center text-gray-600 dark:text-gray-400">
                  <span>No change</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Trend Graphs Section */}
        {assessments && assessments.length > 1 && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Health Trends Over Time</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Diabetes Trend */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Droplet className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-gray-900 dark:text-white">Diabetes Risk Trend</span>
                </div>
                <div className="h-32 bg-gray-50 dark:bg-gray-700 rounded-lg p-4 flex items-end gap-1">
                  {assessments && assessments.slice(0, 5).reverse().map((assessment, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center">
                      <div 
                        className="w-full bg-green-500 rounded-t"
                        style={{ 
                          height: `${((assessment.diabetes_risk || 0) / 100) * 100}px`,
                          minHeight: '4px'
                        }}
                      ></div>
                      <span className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {assessment.date ? 
                          new Date(assessment.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) :
                          'N/A'
                        }
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Hypertension Trend */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Heart className="w-5 h-5 text-red-600" />
                  <span className="font-medium text-gray-900 dark:text-white">Hypertension Risk Trend</span>
                </div>
                <div className="h-32 bg-gray-50 dark:bg-gray-700 rounded-lg p-4 flex items-end gap-1">
                  {assessments && assessments.slice(0, 5).reverse().map((assessment, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center">
                      <div 
                        className="w-full bg-red-500 rounded-t"
                        style={{ 
                          height: `${((assessment.hypertension_risk || 0) / 100) * 100}px`,
                          minHeight: '4px'
                        }}
                      ></div>
                      <span className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {assessment.date ? 
                          new Date(assessment.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) :
                          'N/A'
                        }
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Metabolic Health Trend */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                  <span className="font-medium text-gray-900 dark:text-white">Metabolic Health Trend</span>
                </div>
                <div className="h-32 bg-gray-50 dark:bg-gray-700 rounded-lg p-4 flex items-end gap-1">
                  {assessments && assessments.slice(0, 5).reverse().map((assessment, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center">
                      <div 
                        className="w-full bg-blue-500 rounded-t"
                        style={{ 
                          height: `${(assessment.metabolic_health_score || 0)}px`,
                          minHeight: '4px'
                        }}
                      ></div>
                      <span className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {assessment.date ? 
                          new Date(assessment.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) :
                          'N/A'
                        }
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Cardiovascular Health Trend */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-purple-600" />
                  <span className="font-medium text-gray-900 dark:text-white">Cardiovascular Health Trend</span>
                </div>
                <div className="h-32 bg-gray-50 dark:bg-gray-700 rounded-lg p-4 flex items-end gap-1">
                  {assessments && assessments.slice(0, 5).reverse().map((assessment, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center">
                      <div 
                        className="w-full bg-purple-500 rounded-t"
                        style={{ 
                          height: `${(assessment.cardiovascular_health_score || 0)}px`,
                          minHeight: '4px'
                        }}
                      ></div>
                      <span className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {assessment.date ? 
                          new Date(assessment.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) :
                          'N/A'
                        }
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quick Actions */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <button 
                  onClick={() => navigate('/assessment')}
                  className="flex items-center gap-4 p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl hover:shadow-md transition-all group"
                >
                  <div className="p-3 bg-white dark:bg-gray-700 rounded-lg shadow-sm">
                    <Plus className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="text-left flex-1">
                    <p className="font-semibold text-gray-900 dark:text-white">New Assessment</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Get health prediction</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 group-hover:translate-x-1 transition-transform" />
                </button>

                <button 
                  onClick={() => navigate('/tracking')}
                  className="flex items-center gap-4 p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl hover:shadow-md transition-all group"
                >
                  <div className="p-3 bg-white dark:bg-gray-700 rounded-lg shadow-sm">
                    <Activity className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div className="text-left flex-1">
                    <p className="font-semibold text-gray-900 dark:text-white">Step Tracker</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Automatic GPS tracking</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 group-hover:translate-x-1 transition-transform" />
                </button>

                <button 
                  onClick={() => navigate('/health-trends-3d')}
                  className="flex items-center gap-4 p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl hover:shadow-md transition-all group"
                >
                  <div className="p-3 bg-white dark:bg-gray-700 rounded-lg shadow-sm">
                    <BarChart3 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="text-left flex-1">
                    <p className="font-semibold text-gray-900 dark:text-white">3D Health Trends</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Interactive 3D visualization</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>

            {/* Recent Assessments */}
            <RecentAssessments limit={5} showViewAll={true} />

          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Recommendations */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Recommendations</h2>
              <div className="space-y-3">
                {recommendations.map((rec, idx) => (
                  <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border-l-4 border-blue-500 dark:border-blue-400">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold text-blue-600 dark:text-blue-400 uppercase">
                        {rec.category}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        rec.priority === 'high' 
                          ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400' 
                          : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400'
                      }`}>
                        {rec.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{rec.text}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Health Tips */}
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 dark:from-blue-700 dark:to-purple-700 rounded-2xl p-6 text-white">
              <h3 className="text-lg font-bold mb-2">Health Tip of the Day</h3>
              <p className="text-sm text-blue-100 dark:text-blue-200">
                Walking for just 30 minutes after meals can significantly improve blood sugar control and reduce diabetes risk.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;