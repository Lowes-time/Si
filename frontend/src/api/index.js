import axios from "axios";

const api = axios.create({
  baseURL: "/",
  timeout: 30000,
});

/** 上传光谱文件 */
export function uploadFile(formData) {
  return api.post("/api/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

/** 执行预处理 */
export function preprocess(params) {
  return api.post("/api/preprocess", params);
}

/** 执行厚度计算 */
export function calculate(params) {
  return api.post("/api/calculate", params);
}

/** 导出结果 */
export function exportResult(params) {
  return api.post("/api/export", params, { responseType: "blob" });
}

// --- Records Management ---
export const saveRecord = (data) => {
  return api.post("/api/records/", data);
};

export const fetchRecords = (params) => {
  return api.get("/api/records/", { params });
};

export const fetchRecordDetail = (id) => {
  return api.get(`/api/records/${id}`);
};

export const deleteRecord = (id) => {
  return api.delete(`/api/records/${id}`);
};

export const getReportUrl = (id) => {
  return `/api/records/${id}/report`;
};
