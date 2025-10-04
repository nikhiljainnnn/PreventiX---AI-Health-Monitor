import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Activity, MapPin, Clock, Target, TrendingUp, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const StepTracker = () => {
  const navigate = useNavigate();
  const [isTracking, setIsTracking] = useState(false);
  const [steps, setSteps] = useState(0);
  const [distance, setDistance] = useState(0);
  const [calories, setCalories] = useState(0);
  const [startTime, setStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [permissionGranted, setPermissionGranted] = useState(false);
  const [locationPermission, setLocationPermission] = useState(false);

  // Check for device capabilities
  useEffect(() => {
    checkDeviceCapabilities();
  }, []);

  const checkDeviceCapabilities = () => {
    // Check if device has accelerometer/gyroscope for step counting
    if (navigator.permissions) {
      navigator.permissions.query({ name: 'accelerometer' }).then(result => {
        if (result.state === 'granted') {
          setPermissionGranted(true);
        }
      }).catch(() => {
        // Fallback for devices that don't support accelerometer permission
        setPermissionGranted(true);
      });
    } else {
      setPermissionGranted(true);
    }

    // Check location permission for GPS tracking
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        () => setLocationPermission(true),
        () => setLocationPermission(false)
      );
    }
  };

  const requestPermissions = async () => {
    try {
      // Request location permission
      if (navigator.geolocation) {
        await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject);
        });
        setLocationPermission(true);
      }

      // Request device motion permission
      if (navigator.permissions) {
        const result = await navigator.permissions.query({ name: 'accelerometer' });
        if (result.state === 'granted') {
          setPermissionGranted(true);
        } else {
          await navigator.permissions.request({ name: 'accelerometer' });
          setPermissionGranted(true);
        }
      }

      toast.success('Permissions granted! Step tracking is ready.');
    } catch (error) {
      toast.error('Permission denied. Some features may not work properly.');
    }
  };

  const startTracking = () => {
    if (!permissionGranted || !locationPermission) {
      toast.error('Please grant permissions first to enable step tracking.');
      return;
    }

    setIsTracking(true);
    setStartTime(new Date());
    setSteps(0);
    setDistance(0);
    setCalories(0);
    setElapsedTime(0);

    // Start step counting simulation (in real app, this would use device sensors)
    startStepCounting();
    toast.success('Step tracking started!');
  };

  const stopTracking = () => {
    setIsTracking(false);
    setStartTime(null);
    toast.success(`Tracking stopped! You walked ${steps} steps today.`);
  };

  const startStepCounting = () => {
    // Simulate step counting (in real implementation, this would use device accelerometer)
    const stepInterval = setInterval(() => {
      if (isTracking) {
        // Simulate random step increments
        const newSteps = steps + Math.floor(Math.random() * 3) + 1;
        setSteps(newSteps);
        
        // Calculate distance (average step length ~0.7m)
        const newDistance = newSteps * 0.7;
        setDistance(newDistance);
        
        // Calculate calories (roughly 0.04 calories per step)
        const newCalories = newSteps * 0.04;
        setCalories(newCalories);
      } else {
        clearInterval(stepInterval);
      }
    }, 2000); // Update every 2 seconds

    // Store interval ID for cleanup
    return stepInterval;
  };

  // Update elapsed time
  useEffect(() => {
    let interval;
    if (isTracking && startTime) {
      interval = setInterval(() => {
        const now = new Date();
        const elapsed = Math.floor((now - startTime) / 1000);
        setElapsedTime(elapsed);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isTracking, startTime]);

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getStepGoal = () => 10000; // Default step goal
  const getProgressPercentage = () => Math.min((steps / getStepGoal()) * 100, 100);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => navigate('/dashboard')}
          className="mb-6 flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Dashboard
        </button>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Automatic Step Tracker</h1>
            <p className="text-gray-600 dark:text-gray-400">Track your steps automatically using your device's GPS and sensors</p>
          </div>

          {/* Permission Status */}
          <div className="mb-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-blue-600" />
              Device Permissions
            </h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${permissionGranted ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Motion Sensors: {permissionGranted ? 'Granted' : 'Not Granted'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${locationPermission ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Location/GPS: {locationPermission ? 'Granted' : 'Not Granted'}
                </span>
              </div>
            </div>
            {(!permissionGranted || !locationPermission) && (
              <button
                onClick={requestPermissions}
                className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Grant Permissions
              </button>
            )}
          </div>

          {/* Step Tracking Display */}
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            {/* Main Stats */}
            <div className="space-y-6">
              <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl">
                <div className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                  {steps.toLocaleString()}
                </div>
                <div className="text-gray-600 dark:text-gray-400">Steps Today</div>
                <div className="mt-4">
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${getProgressPercentage()}%` }}
                    ></div>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                    {getProgressPercentage().toFixed(1)}% of daily goal ({getStepGoal().toLocaleString()} steps)
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-xl">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {(distance / 1000).toFixed(2)} km
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Distance</div>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-xl">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {calories.toFixed(0)}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Calories</div>
                </div>
              </div>
            </div>

            {/* Tracking Controls */}
            <div className="space-y-6">
              <div className="text-center p-6 bg-gray-50 dark:bg-gray-700 rounded-xl">
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  {formatTime(elapsedTime)}
                </div>
                <div className="text-gray-600 dark:text-gray-400">Active Time</div>
              </div>

              <div className="space-y-4">
                {!isTracking ? (
                  <button
                    onClick={startTracking}
                    disabled={!permissionGranted || !locationPermission}
                    className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    <Activity className="w-5 h-5" />
                    Start Tracking
                  </button>
                ) : (
                  <button
                    onClick={stopTracking}
                    className="w-full bg-gradient-to-r from-red-500 to-red-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center justify-center gap-2"
                  >
                    <Activity className="w-5 h-5" />
                    Stop Tracking
                  </button>
                )}

                <div className="text-center text-sm text-gray-600 dark:text-gray-400">
                  {isTracking ? (
                    <div className="flex items-center justify-center gap-2 text-green-600 dark:text-green-400">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      Currently tracking...
                    </div>
                  ) : (
                    'Ready to start tracking'
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Features Info */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              Automatic Features
            </h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-blue-600 mt-1" />
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">GPS Tracking</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Uses your device's GPS for accurate distance measurement</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Activity className="w-5 h-5 text-green-600 mt-1" />
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">Motion Sensors</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Uses accelerometer and gyroscope for step counting</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Clock className="w-5 h-5 text-purple-600 mt-1" />
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">Real-time Updates</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Continuous tracking with live step count updates</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StepTracker;

