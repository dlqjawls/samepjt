// src/admin/context/AdminAuthProvider.jsx
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { AdminAuthContext } from "./AdminAuthContext";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

const BASE_URL = import.meta.env.VITE_API_URL;

export const AdminAuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const [admin, setAdmin] = useState(() => {
    const storedAdmin = localStorage.getItem("adminInfo");
    return storedAdmin ? JSON.parse(storedAdmin) : null;
  });

  const [accessToken, setAccessToken] = useState(() =>
    localStorage.getItem("adminToken")
  );
  const [refreshToken, setRefreshToken] = useState(() =>
    localStorage.getItem("adminRefreshToken")
  );

  // ref를 사용하여 로그아웃 처리 중임을 추적
  const isLoggingOutRef = useRef(false);

  const loginAdmin = (adminData) => {
    setAdmin(adminData);
    localStorage.setItem("adminInfo", JSON.stringify(adminData));
    localStorage.setItem("adminToken", adminData.token);
    if (adminData.refreshToken) {
      setRefreshToken(adminData.refreshToken);
      localStorage.setItem("adminRefreshToken", adminData.refreshToken);
    }
    setAccessToken(adminData.token);
    isLoggingOutRef.current = false;
  };

  const logoutAdmin = () => {
    if (isLoggingOutRef.current) return;
    isLoggingOutRef.current = true;
    setAdmin(null);
    setAccessToken(null);
    setRefreshToken(null);
    localStorage.removeItem("adminInfo");
    localStorage.removeItem("adminToken");
    localStorage.removeItem("adminRefreshToken");
  };

  useEffect(() => {
    // 요청 인터셉터: 모든 요청에 Authorization 헤더 자동 설정
    const requestInterceptor = axios.interceptors.request.use(
      (config) => {
        if (accessToken) {
          config.headers["Authorization"] = `Bearer ${accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 응답 인터셉터: 401 에러 발생 시 토큰 갱신 시도
    const responseInterceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        // _retry가 없고, 401 오류인 경우에만 토큰 갱신 시도
        if (
          error.response &&
          error.response.status === 401 &&
          !originalRequest._retry
        ) {
          originalRequest._retry = true;
          if (!refreshToken) {
            console.error("리프레시 토큰이 없습니다.");
            if (!isLoggingOutRef.current) {
              toast.error("세션이 만료되었습니다. 다시 로그인 해주세요.");
              logoutAdmin();
              navigate("/admin/login");
            }
            return Promise.reject(error);
          }
          try {
            console.log("토큰 갱신 시도, 현재 refreshToken:", refreshToken);
            const refreshResponse = await axios.post(
              `${BASE_URL}/auth/refresh-token`,
              { refresh_token: refreshToken },
              { headers: { "Content-Type": "application/json" } }
            );
            if (refreshResponse.data.resultCode === "SUCCESS") {
              const newAccessToken = refreshResponse.data.data.access_token;
              const newRefreshToken = refreshResponse.data.data.refresh_token;
              setAccessToken(newAccessToken);
              setRefreshToken(newRefreshToken);
              console.log("Token refreshed successfully:", {
                newAccessToken,
                newRefreshToken,
              });
              localStorage.setItem("adminToken", newAccessToken);
              localStorage.setItem("adminRefreshToken", newRefreshToken);
              originalRequest.headers[
                "Authorization"
              ] = `Bearer ${newAccessToken}`;
              return axios(originalRequest);
            } else {
              console.error("토큰 갱신 응답 실패:", refreshResponse.data);
              if (!isLoggingOutRef.current) {
                toast.error("세션이 만료되었습니다. 다시 로그인 해주세요.");
                logoutAdmin();
                navigate("/admin/login");
              }
              return Promise.reject(error);
            }
          } catch (refreshError) {
            console.error("토큰 갱신 중 오류:", refreshError);
            if (!isLoggingOutRef.current) {
              toast.error("세션이 만료되었습니다. 다시 로그인 해주세요.");
              logoutAdmin();
              navigate("/admin/login");
            }
            return Promise.reject(refreshError);
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, [accessToken, refreshToken, navigate]);

  return (
    <AdminAuthContext.Provider
      value={{ admin, loginAdmin, logoutAdmin, accessToken }}
    >
      {children}
    </AdminAuthContext.Provider>
  );
};
