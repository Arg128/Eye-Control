export type EyeTrackingData = {
  x: number;
  y: number;
  confidence: number;
};

export interface EyeTrackerProps {
  onTrackingData: (data: EyeTrackingData) => void;
}

export interface CameraViewProps {
  isActive: boolean;
}

export interface CalibrationData {
  targetPosition: { x: number; y: number };
  userPosition: { x: number; y: number };
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}