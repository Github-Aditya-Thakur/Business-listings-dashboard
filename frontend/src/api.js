import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export async function fetchCityWise() {
  const res = await api.get("/api/dashboard/city-wise");
  return res.data;
}

export async function fetchCategoryWise() {
  const res = await api.get("/api/dashboard/category-wise");
  return res.data;
}

export async function fetchSourceWise() {
  const res = await api.get("/api/dashboard/source-wise");
  return res.data;
}