export type Detection = {
  class_name: string; position: string; attention: string; confidence: number;
  box: [number, number, number, number];
};
export type Announcement = { id: number; created_at: string; text: string };
export type DetectionResponse = { detections: Detection[]; description: string; announce: boolean };
export type QuestionResponse = { answer: string };