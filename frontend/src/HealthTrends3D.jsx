import React, { useState, useEffect, useRef } from 'react';
import { ArrowLeft, TrendingUp, Activity, Heart, Droplet, Moon, Scale } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { trackingAPI } from './api';
import toast from 'react-hot-toast';

// CSS-based 3D Chart component
function Chart3D({ healthData, selectedMetric }) {
  const chartRef = useRef();
  const [rotation, setRotation] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (chartRef.current) {
        const rect = chartRef.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        const deltaX = (e.clientX - centerX) / 100;
        const deltaY = (e.clientY - centerY) / 100;
        
        setRotation({
          x: Math.max(-30, Math.min(30, deltaY)),
          y: deltaX
        });
      }
    };

    const chart = chartRef.current;
    if (chart) {
      chart.addEventListener('mousemove', handleMouseMove);
      return () => chart.removeEventListener('mousemove', handleMouseMove);
    }
  }, []);

  if (!healthData || !healthData[selectedMetric]) {
    return null;
  }

  const data = healthData[selectedMetric];
  const maxValue = Math.max(...data);
  const minValue = Math.min(...data);
  const range = maxValue - minValue || 1;

  const colors = {
    steps: '#3B82F6',
    sleep: '#8B5CF6',
    weight: '#10B981',
    blood_pressure: '#EF4444',
    glucose: '#F59E0B',
    water: '#06B6D4'
  };

  const color = colors[selectedMetric] || '#3B82F6';

  return (
    <div 
      ref={chartRef}
      className="relative w-full h-96 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 rounded-xl overflow-hidden cursor-move"
      style={{
        perspective: '1000px',
        transformStyle: 'preserve-3d'
      }}
    >
      {/* 3D Grid Background */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(90deg, #666 1px, transparent 1px),
            linear-gradient(180deg, #666 1px, transparent 1px)
          `,
          backgroundSize: '20px 20px',
          transform: `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)`
        }}
      />
      
      {/* 3D Chart Container */}
      <div 
        className="absolute inset-4"
        style={{
          transform: `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)`,
          transformStyle: 'preserve-3d'
        }}
      >
        {/* Data Points and Lines */}
        <svg className="w-full h-full">
          {/* Grid Lines */}
          {[0, 25, 50, 75, 100].map((value, index) => (
            <line
              key={index}
              x1="0"
              y1={`${100 - (value / 100) * 100}%`}
              x2="100%"
              y2={`${100 - (value / 100) * 100}%`}
              stroke="#666"
              strokeWidth="1"
              opacity="0.3"
            />
          ))}
          
          {/* Data Line */}
          <polyline
            points={data.map((value, index) => {
              const x = (index / (data.length - 1)) * 100;
              const y = 100 - ((value - minValue) / range) * 100;
              return `${x}%,${y}%`;
            }).join(' ')}
            fill="none"
            stroke={color}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              filter: 'drop-shadow(0 0 8px rgba(0,0,0,0.3))'
            }}
          />
          
          {/* Data Points */}
          {data.map((value, index) => {
            const x = (index / (data.length - 1)) * 100;
            const y = 100 - ((value - minValue) / range) * 100;
            return (
              <circle
                key={index}
                cx={`${x}%`}
                cy={`${y}%`}
                r="4"
                fill={color}
                style={{
                  filter: 'drop-shadow(0 0 4px rgba(0,0,0,0.5))'
                }}
              />
            );
          })}
        </svg>
        
        {/* 3D Labels */}
        <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-600 dark:text-gray-400">
          {data.map((_, index) => (
            <span key={index} className="text-center">
              {index + 1}
            </span>
          ))}
        </div>
        
        <div className="absolute left-0 top-0 bottom-0 flex flex-col justify-between text-xs text-gray-600 dark:text-gray-400">
          {[maxValue, (maxValue + minValue) / 2, minValue].map((value, index) => (
            <span key={index} className="text-right">
              {value.toFixed(1)}
            </span>
          ))}
        </div>
      </div>
      
      {/* 3D Effect Overlay */}
      <div 
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
        style={{
          transform: `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)`,
          transformStyle: 'preserve-3d'
        }}
      />
    </div>
  );
}

const HealthTrends3D = () => {
  const navigate = useNavigate();
  const [healthData, setHealthData] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('steps');
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);

  const metrics = [
    { key: 'steps', label: 'Daily Steps', icon: Activity, color: '#3B82F6' },
    { key: 'sleep', label: 'Sleep Hours', icon: Moon, color: '#8B5CF6' },
    { key: 'weight', label: 'Weight (kg)', icon: Scale, color: '#10B981' },
    { key: 'blood_pressure', label: 'Blood Pressure', icon: Heart, color: '#EF4444' },
    { key: 'glucose', label: 'Glucose Level', icon: Droplet, color: '#F59E0B' },
    { key: 'water', label: 'Water Intake', icon: Droplet, color: '#06B6D4' }
  ];

  useEffect(() => {
    fetchHealthData();
  }, [timeRange]);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      const response = await trackingAPI.getHistory(timeRange);
      
      if (response.data && response.data.history) {
        const processedData = processHealthData(response.data.history);
        setHealthData(processedData);
      } else {
        // Generate sample data for demonstration
        const sampleData = generateSampleData();
        setHealthData(sampleData);
      }
    } catch (error) {
      console.error('Error fetching health data:', error);
      // Generate sample data for demonstration
      const sampleData = generateSampleData();
      setHealthData(sampleData);
      toast.error('Using sample data for demonstration');
    } finally {
      setLoading(false);
    }
  };

  const processHealthData = (rawData) => {
    const processed = {};
    
    metrics.forEach(metric => {
      processed[metric.key] = rawData.map(entry => {
        const value = entry[metric.key];
        return value !== null && value !== undefined ? value : 0;
      });
    });

    return processed;
  };

  const generateSampleData = () => {
    const days = timeRange;
    const sampleData = {};
    
    metrics.forEach(metric => {
      const baseValues = {
        steps: 8000,
        sleep: 7.5,
        weight: 70,
        blood_pressure: 120,
        glucose: 100,
        water: 6
      };
      
      sampleData[metric.key] = Array.from({ length: days }, (_, i) => {
        const base = baseValues[metric.key] || 50;
        const variation = Math.sin(i * 0.2) * (base * 0.2);
        const random = (Math.random() - 0.5) * (base * 0.1);
        return Math.max(0, base + variation + random);
      });
    });

    return sampleData;
  };

  const getMetricStats = (metric) => {
    if (!healthData || !healthData[metric]) return { current: 0, average: 0, trend: 0 };
    
    const data = healthData[metric];
    const current = data[data.length - 1] || 0;
    const average = data.reduce((sum, val) => sum + val, 0) / data.length;
    const trend = data.length > 1 ? (data[data.length - 1] - data[data.length - 2]) : 0;
    
    return { current, average, trend };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">Loading 3D Health Trends...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <button
          onClick={() => navigate('/dashboard')}
          className="mb-6 flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Dashboard
        </button>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
              <TrendingUp className="w-8 h-8 text-blue-600" />
              3D Health Trends Visualization
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Interactive 3D visualization of your health metrics over time
            </p>
          </div>

          {/* Time Range Selector */}
          <div className="mb-6 flex gap-4 items-center">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Time Range:
            </label>
            {[7, 14, 30, 60, 90].map(days => (
              <button
                key={days}
                onClick={() => setTimeRange(days)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  timeRange === days
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                {days} days
              </button>
            ))}
          </div>

          {/* Metric Selector */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Select Health Metric:
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {metrics.map(metric => {
                const Icon = metric.icon;
                const stats = getMetricStats(metric.key);
                const isSelected = selectedMetric === metric.key;
                
                return (
                  <button
                    key={metric.key}
                    onClick={() => setSelectedMetric(metric.key)}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <div className="flex flex-col items-center text-center">
                      <Icon className={`w-6 h-6 mb-2 ${isSelected ? 'text-blue-600' : 'text-gray-600 dark:text-gray-400'}`} />
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {metric.label}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Current: {stats.current.toFixed(1)}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 3D Chart Container */}
          <div className="bg-gray-100 dark:bg-gray-900 rounded-xl p-4 mb-6">
            <div className="h-96 w-full">
              <Chart3D healthData={healthData} selectedMetric={selectedMetric} />
            </div>
          </div>

          {/* Statistics Panel */}
          <div className="grid md:grid-cols-3 gap-6">
            {metrics.slice(0, 3).map(metric => {
              const stats = getMetricStats(metric.key);
              const Icon = metric.icon;
              const isSelected = selectedMetric === metric.key;
              
              return (
                <div
                  key={metric.key}
                  className={`p-6 rounded-xl border-2 transition-all cursor-pointer ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                  onClick={() => setSelectedMetric(metric.key)}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <Icon className={`w-6 h-6 ${isSelected ? 'text-blue-600' : 'text-gray-600 dark:text-gray-400'}`} />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {metric.label}
                    </h3>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Current:</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {stats.current.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Average:</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {stats.average.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Trend:</span>
                      <span className={`text-sm font-medium ${
                        stats.trend > 0 ? 'text-green-600' : stats.trend < 0 ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {stats.trend > 0 ? '↗' : stats.trend < 0 ? '↘' : '→'} {Math.abs(stats.trend).toFixed(1)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Instructions */}
          <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
              🎮 3D Chart Controls
            </h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800 dark:text-blue-200">
              <div>
                <strong>Mouse Controls:</strong>
                <ul className="mt-1 space-y-1">
                  <li>• Move mouse over chart: Rotate 3D view</li>
                  <li>• Hover effects: Interactive 3D perspective</li>
                  <li>• Click metric cards: Switch data views</li>
                </ul>
              </div>
              <div>
                <strong>Features:</strong>
                <ul className="mt-1 space-y-1">
                  <li>• Real-time 3D rotation</li>
                  <li>• Interactive data points</li>
                  <li>• Smooth animations</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthTrends3D;
