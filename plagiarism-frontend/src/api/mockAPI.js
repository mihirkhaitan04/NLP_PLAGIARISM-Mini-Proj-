import axios from "axios";

const BASE_URL = "http://localhost:8000";

export const uploadDocument = async (file, mode = "web") => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await axios.post(`${BASE_URL}/api/upload?mode=${mode}`, formData);
  return response.data;
};

export const getResults = async (id) => {
  const response = await axios.get(`${BASE_URL}/api/results/${id}`);
  return response.data;
};

export const getHistory = async () => {
  const response = await axios.get(`${BASE_URL}/api/history`);
  return response.data;
};